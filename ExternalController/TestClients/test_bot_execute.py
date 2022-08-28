import asyncio
import websockets
import json
import unittest

'''
protocol
1.Send password for general server
2.Send name and type(json serialized)
3.Send your naming of the server
4.check server response
5.begin general sequence
'''

class AsyncTests(unittest.IsolatedAsyncioTestCase):
    
    async def connect(self):
        websocket = await websockets.connect('ws://localhost:50223', ping_interval= None, max_size = 20000000)
        await websocket.send("")
        await websocket.send(self.name_and_type())
        await websocket.send("test_name")
        connection_response = await websocket.recv()
        self.assertEqual(connection_response,"success")
        return websocket

    async def test(self):
        websocket = await self.connect()
        await self.send_periodic_data_and_listen(websocket)

    async def send_periodic_data_and_listen(self,websocket):
        while True:
            try:
                
                message = await asyncio.wait_for(websocket.recv(),5)
                print(message)
                if message == "deactivate":
                    await websocket.send("success")
                    await self.enter_deactivate_loop(websocket)
                elif message == "disconnect":
                    await websocket.send("success")
                    print("disconnecting.")
                    break
                elif message == "passive_data":
                    await websocket.send(json.dumps({
                        "alert_status":"alert_present", 
                        "message":"test for house of iot network #1"})) #basic data
                elif message == "test_trigger":
                    await websocket.send("success")
                else:
                    await websocket.send("issue")

            except Exception as e: 
                print(e)

    async def enter_deactivate_loop(self,websocket):
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(),5)
                if message == "activate":
                    await websocket.send("success")
                    break
            except Exception as e:
                print(e)

    def name_and_type(self):
        data = {"name":"test_bot_execute" , "type":"test_bot"}
        return json.dumps(data)

if __name__ == "__main__":
    unittest.main()