import asyncio
import json
from datetime import datetime
from collections import deque
import traceback

class LastExecuted:
    def __init__(self,relation,time_data):
        self.relation = relation
        self.time_data = time_data

class Server:
    def __init__(self,parent,config):
        self.last_executed_relational_actions = deque()
        self.parent = parent
        self.devices = {}
        self.config = config

    async def authenticate_client_after_connection(self,websocket,path):
        try:
            credentials = await asyncio.wait_for(websocket.recv(),30)
            credentials_dict = json.loads(credentials)
            gathered_password = credentials_dict["password"]
            gathered_name = credentials_dict["name"]

            if self.is_successfully_authenticated(gathered_name,gathered_password):
                self.devices[gathered_name] = websocket
                await asyncio.wait_for(websocket.send("success"),20)
                loop = asyncio.get_event_loop()
                await loop.create_task(self.main_loop(websocket,gathered_name))
            else:
                await asyncio.wait_for(websocket.send("issue"),20)
        except Exception as e:
            traceback.print_exc()
    
    def is_successfully_authenticated(self,name,user_password):
        if user_password == self.config["password"] and name not in self.devices:
            return True
        else:
            return False

    async def main_loop(self,websocket,name):
        self.parent.console_logger.log_new_connection(name)
        while name in self.devices:
            try:
                await self.gather_and_route_request(websocket)
            except:
                self.parent.console_logger.log_generic_row(f"{name} was disconnected from the server!\n","red")
                self.parent.console_logger.log_device_stats()
                del self.devices[name]
                break
            await asyncio.sleep(3)
    
    async def gather_and_route_request(self,websocket):
        message = await websocket.recv()
        message = json.loads(message)
        client_is_authed = self.is_authed(message["password"])

        if client_is_authed == False:
            await asyncio.wait_for(self.websocket.send("issue"),30)
        elif message["request"] == "add_relation" or message["request"] == "remove_relation":
            await self.parent.relation_manager.add_or_remove_relation(
                websocket,message["relation"],message["request"])
        elif message["request"] == "remove_all_relations":
            self.remove_all_relations()
            await asyncio.wait_for(websocket.send("success"),10)
        elif message["request"] == "view_last_relations":
            await self.send_last_execute_relations(websocket)
        elif message["request"] == "view_relations":
            await self.send_relations(websocket)
        else:
            await asyncio.wait_for(self.websocket.send("issue"),30)
        
    def add_or_replace_last_executed_relation(self,relation):
        last_executed = LastExecuted(relation,datetime.utcnow())
        if len(self.last_executed_relational_actions) == 5:
            #remove the oldest  from the queue and add the new one
            self.last_executed_relational_actions.popleft()
            self.last_executed_relational_actions.append(last_executed)
        else:
            self.last_executed_relational_actions.append(last_executed)

    async def send_last_execute_relations(self,websocket):
        list_last_executed = self.convert_last_executed_into_dict_list()
        status_and_list = {
            "status":"success",
            "type":"last_executed" ,
            "relations":list_last_executed}
        await asyncio.wait_for(websocket.send(json.dumps(status_and_list)),20)

    async def send_relations(self,websocket):
        current_relations_and_status = {
                "status":"success",
                "type":"current_relations",
                "relations":self.parent.relation_manager.relations}
        await asyncio.wait_for(websocket.send(json.dumps(current_relations_and_status)),20)
    
    def convert_last_executed_into_dict_list(self):
        queue_to_list = list(self.last_executed_relational_actions)
        executed_dict_list = []
        for last_executed in queue_to_list:
            executed_dict_list.append({
                "relation" : last_executed.relation,
                "datetime" : str(last_executed.time_data)
            })
        return executed_dict_list

    def remove_all_relations(self):
        self.parent.relation_manager.relations = []
        with open("relations.json","w") as File:
            File.write(json.dumps({"relations":[]}))

    def is_authed(self, password_response):
        if password_response == self.config["password"]:
            return True
        else:
            return False