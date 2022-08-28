
from relation_manager import RelationManager
from server import Server
import json
import unittest
from unittest import IsolatedAsyncioTestCase

"""Making utilization of mock classes to simulate the actual logic and test the side effects."""

class MockRelationManager:
    def __init__(self):
        self.relations = []

class MockWebsocket:
    def __init__(self,recv_data = None):
        self.recv_data = recv_data

    async def recv(self):
        return self.recv_data

    async def send(self,data):
        pass

class MockGeneralServerClient:
    def __init__(self):
        self.websocket = MockWebsocket(json.dumps({"status":"success"}))


class Tests(unittest.TestCase):

    def tests(self):
        #check that relations are being picked up from the config file
        self.generate_static_relation_config()
        relation_handler = RelationManager(self)
        self.assertEqual(len(relation_handler.relations),1)

        #check passive_data logic
        passive_data = json.dumps({"bots" : [{"device_name":"soil_monitor", "active_status":True, "humidity":2}]})
        relation_handler.organize_bots_to_minimize_searching(passive_data)
        condition_present = relation_handler.condition_present_in_passive_data("humidity",2,"soil_monitor")
        self.assertTrue(condition_present)

        #other tests
        self.removing_single_relation_works(relation_handler)
        self.relation_comparison_works(relation_handler)
        self.relation_validation(relation_handler)
        self.removing_all_relations()

    def generate_static_relation_config(self):
        mock_relation_config = {
            "relations" : [
                {"device_name":"water_valve", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
            ]
        }
        with open("relations.json","w") as File:
            File.write(json.dumps(mock_relation_config))

    def relation_validation(self,relation_manager):    
        good_test_relation =  {"device_name":"water_valve", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
        bad_test_relation =  {"device_name":"water_valve", "action":"open"}

        good_relation_is_valid = relation_manager.relation_is_valid(good_test_relation)
        bad_relation_is_valid = relation_manager.relation_is_valid(bad_test_relation)

        self.assertTrue(good_relation_is_valid)
        self.assertFalse(bad_relation_is_valid)
    
    def relation_comparison_works(self,relation_manager):
        test_relation =  {"device_name":"water_valve1", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
        test_relation_two =  {"device_name":"water_valve2", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
        first_comparison = relation_manager.relations_are_the_same(test_relation_two,test_relation_two)
        second_comparison = relation_manager.relations_are_the_same(test_relation_two,test_relation)
        self.assertTrue(first_comparison)
        self.assertFalse(second_comparison)
    
        #comparing same base data with different conditions
        test_relation_three =  {"device_name":"water_valve1", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":3}]}
        third_comparison = relation_manager.relations_are_the_same(test_relation_three,test_relation)
        self.assertFalse(third_comparison)


    def removing_all_relations(self):
        server = Server(self,{"host": "127.0.0.1", "port": 50224, "password":""})
        #mock manager for the test(server needs it for updating copies of the relations held in memory)
        self.relation_manager = MockRelationManager()
        server.remove_all_relations()
        
        #check that the relation is deleted 
        relations_data = self.gather_relations_from_config()
        self.assertEqual(len(relations_data["relations"]),0)

    def removing_single_relation_works(self,relation_manager):
        test_relation =  {"device_name":"water_valve1", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
        test_relation_two =  {"device_name":"water_valve2", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
        relation_manager.relations.append(test_relation)
        relation_manager.relations.append(test_relation_two)

        self.assertEqual(len(relation_manager.relations),3)
        relation_manager.find_and_remove_relation(test_relation_two)
        self.assertEqual(len(relation_manager.relations),2)

        for relation in relation_manager.relations:
            self.assertTrue(relation["device_name"] != test_relation_two["device_name"])

    def gather_relations_from_config(self):
        with open("relations.json","r") as File:
            data =  File.read()
            relations = json.loads(data)
            return relations
        
class AsyncTests(IsolatedAsyncioTestCase):

    async def test(self):
        #needed for the general server client's websocket which is used to execute actions
        self.general_server_client = MockGeneralServerClient()
        await self.last_executed_relation()
        
    def overwrite_relation_config(self,data):
        with open("relations.json","w") as File:
            File.write(json.dumps({"relations" : data}))

    async def last_executed_relation(self):
        self.starting_number = 0
        self.mock_passive_data = json.dumps({"bots" : [{"device_name":"soil_monitor", "active_status":True, "humidity":2}]})

        self.temp_relational_config = [{"device_name":"water_valve", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}]
        #making sure the config file is setup correctly
        self.overwrite_relation_config(self.temp_relational_config)

        #server(required to be in the parent of relation_manager)
        self.server = Server(self,{"host": "127.0.0.1", "port": 50224, "password":""})
        
        #to be tested
        self.relation_manager = RelationManager(self)

        #websocket(required to be in the parent of relation_manager)
        self.websocket = MockWebsocket(json.dumps({"status":"success"}))
        
        #check side effects(server should be mutated by the relation_manager)
        await self.check_queue_size_after_execution_simulation(1)

        #continue checking side effects and fill up the queue to test overwritting
        await self.check_queue_size_after_execution_simulation(2)
        await self.check_queue_size_after_execution_simulation(3)
        await self.check_queue_size_after_execution_simulation(4)
        await self.check_queue_size_after_execution_simulation(5)

        queue_in_list_form = list(self.server.last_executed_relational_actions)

        #make sure the oldest  item is always getting overwritten. We only keep record of the newest executed relations
        oldest_executed_relation = queue_in_list_form[0]
        print(queue_in_list_form)
        
        await self.relation_manager.check_passive_data_for_matching_conditions_and_execute_actions(self.mock_passive_data)
        self.assertEqual(len(self.server.last_executed_relational_actions),5)

        second_capture_of_oldest_executed_relation = self.server.last_executed_relational_actions.popleft()

        #the oldest item should be the second excecuted relation since the first one should have gotten overwritten.
        self.assertFalse(oldest_executed_relation.time_data == second_capture_of_oldest_executed_relation.time_data)
        self.assertFalse(oldest_executed_relation.relation["action"] == second_capture_of_oldest_executed_relation.relation["action"]) 
        self.assertFalse(oldest_executed_relation.relation["device_name"] == second_capture_of_oldest_executed_relation.relation["device_name"]) 

    def overwrite_relational_config_randomly(self):
        self.temp_relational_config[0]["device_name"] = str(self.temp_relational_config[0]["device_name"]) + str(self.starting_number)
        self.temp_relational_config[0]["action"] = str(self.temp_relational_config[0]["action"]) + str(self.starting_number)
        self.starting_number += 1
        with open("relations.json","w") as File:
            File.write(json.dumps({"relations" : self.temp_relational_config}))
        self.relation_manager.relations = self.relation_manager.get_relations()

    async def check_queue_size_after_execution_simulation(self,num):
        self.overwrite_relational_config_randomly()
        await self.relation_manager.check_passive_data_for_matching_conditions_and_execute_actions(self.mock_passive_data)
        self.assertEqual(len(self.server.last_executed_relational_actions),num)

if __name__ == "__main__":
    unittest.main()