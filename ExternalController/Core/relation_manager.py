import json
import os
import traceback
import asyncio

from websockets import exceptions
"""
To Change?
We are storing the device name twice after organization of bots
via organize_bots_to_minimize_searching -> Fn() . This is a minimal
improvement on storage consumption.
"""

class RelationManager:
    def __init__(self,parent):
        #consider changing relations to use a LinkedList for larger data sets.
        self.relations = self.get_relations()
        self.all_conditions_satisfied = None
        self.bots = {}
        self.parent = parent

    async def check_passive_data_for_matching_conditions_and_execute_actions(self,passive_data):
        self.organize_bots_to_minimize_searching(passive_data)
        self.all_conditions_satisfied = True
        # for every relation
        for relation in self.relations:
            #check each relation's condition to see if it is met
            for condition in relation["conditions"]:
                name = condition["device_name"]
                keys = condition.keys()
                for key in keys:
                    if key != "device_name":
                        if self.condition_present_in_passive_data(key,condition[key],name) == False:
                            self.all_conditions_satisfied = False

            #if all of the conditions were satisfied               
            await self.execute_action_if_conditions_were_satisfied(relation)
                
    """
    Background: We recieve a list of objects from the server that are the bots.

    We re-organize the  data(linear complexity) with the keys representing the 
    bot data and then have constant time look up on the bot data. 
    """
    def organize_bots_to_minimize_searching(self,bot_data):
        passive_data = json.loads(bot_data)
        for bot in passive_data["bots"]:
            #ignore all deactivated bots
            if bot["active_status"] == True:
                name = bot["device_name"]
                self.bots[name] = bot

    def get_relations(self):
        file = open("relations.json","r") 
        file_data = file.read()
        file.close()
        relation_data =  json.loads(file_data)
        return relation_data["relations"]

    def condition_present_in_passive_data(self,key,value,bot_name):
        if bot_name in self.bots:
            if key in self.bots[bot_name] and self.bots[bot_name][key] == value:
                return True
            else:
                return False
        else:
            return False
    
    async def execute_action_if_conditions_were_satisfied(self,relation):
        if self.all_conditions_satisfied == True:
            try:
                await self.parent.general_server_client.websocket.send("bot_control")
                await self.parent.general_server_client.websocket.send(relation["action"])
                await self.parent.general_server_client.websocket.send(relation["device_name"])
                response = await self.parent.general_server_client.websocket.recv()
                successfully_authed = await self.authenticate_if_needed(response)

                if successfully_authed:
                    self.parent.server.add_or_replace_last_executed_relation(relation)
                else:
                    print("Failed action execution due to failed auth")
            except Exception as e:
                traceback.print_exc()
             
    def relation_is_valid(self,relation):
        try:
            print(relation)
            if "action" in relation and "device_name" in relation and "conditions" in relation and len(relation["conditions"])>0:
                return True
            else:
                return False
        except Exception as e:
            traceback.print_exc()
            return False

    async def add_or_remove_relation(self,websocket,relation,request):
        #only add/remove relation if the relation is proven to be valid 
        relation_is_valid = self.relation_is_valid(relation)
        print(relation_is_valid)
        if(relation_is_valid): 
            if request == "add_relation":
                self.parent.console_logger.log_new_relation_addition(relation)
                self.relations.append(relation)
                self.update_other_relation_copies()
            else:
                self.parent.console_logger.log_new_relation_removal(relation)
                self.find_and_remove_relation(relation)
                self.update_other_relation_copies()
            await asyncio.wait_for(websocket.send("success"),10)
        else:
            await asyncio.wait_for(websocket.send("issue"),10)

    def update_other_relation_copies(self):
        with open("relations.json","w") as File:
            File.write(json.dumps({"relations":self.parent.relation_manager.relations}))

    def find_and_remove_relation(self,target_relation):
        for i,relation in enumerate(self.relations):
            #there can only be one relation with a unique action/device name.
            if self.relations_are_the_same(relation,target_relation):
               self.relations.pop(i)
               break

    def relations_are_the_same(self,relation_one,relation_two):
        try:
            if relation_one["device_name"] == relation_two["device_name"]:
                if relation_one["action"] == relation_two["action"]:
                    relation_one_conditions = relation_one["conditions"]
                    relation_two_conditions = relation_two["conditions"]
                    for i in range(len(relation_one_conditions)):
                        #for every key in the current condition dict
                        for key in relation_one["conditions"][i].keys():
                            relation_one_value = relation_one_conditions[i][key]
                            relation_two_value = relation_two_conditions[i][key]
                            if relation_one_value != relation_two_value:
                                return False
                    return True
                else:
                    return False

            else:
                return False
        except Exception as e:
            traceback.print_exc()
            return False

    async def authenticate_if_needed(self,response):
        response_dict = json.loads(response)
        if response_dict["status"] == "needs-admin-auth":
            admin_password = os.environ.get("hoi_exc_a_pw")
            await self.parent.general_server_client.websocket.send(admin_password)
            auth_response = await self.parent.general_server_client.websocket.recv()
            auth_response_dict = json.loads(auth_response)
            if auth_response_dict["status"] == "success":
                return True
        elif response_dict["status"] == "success":
            return True
        else:
            return False   