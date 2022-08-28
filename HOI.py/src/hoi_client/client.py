import websockets
import asyncio
import json
from .console_logger import ConsoleLogger
from .device_config import Config
import os

class Client:
    def __init__(self,config):
        self.config = config

    """
    main execution 
    """
    async def main(self,websocket,tasks):
        self.prerequisite_check()
        self.password = os.environ.get("rpw_hoi_gs")

        connection_response = await self.send_connection_credentials(websocket)
        ConsoleLogger.log_auth_status(connection_response)
        await self.await_tasks(tasks)

    async def await_tasks(self,tasks):
        loop = asyncio.get_event_loop()
        loop_created_tasks = []
        for task in tasks:
            loop_created_tasks.append(loop.create_task(task))
        await asyncio.wait(loop_created_tasks)

    async def establish_connection(self):
        times_attempted = 1
        while True:
            try:
                return await websockets.connect(f'ws://{self.config.host}:{self.config.port}', ping_interval= None, max_size = 20000000)
            except:
                ConsoleLogger.log_issue_establishing_connection(times_attempted)
                times_attempted += 1
                await asyncio.sleep(6)

    def prerequisite_check(self):
        if(self.config.port == None):
            ConsoleLogger.log_before_quitting('No port was set for the client!')
        if(self.config.host == None):
            ConsoleLogger.log_before_quitting("No host was set for the client!")
        if(self.config.tasks == None):
            ConsoleLogger.log_before_quitting("No tasks were defined for the client!")
        if(self.config.name == None):
            ConsoleLogger.log_before_quitting("No name was defined for the client!")
        if(self.config.type == None):
            ConsoleLogger.log_before_quitting("No type was defined for the client!")

    async def send_connection_credentials(self,websocket):
        await websocket.send(self.config.password)
        await websocket.send(self.name_and_type())
        await websocket.send("main")
        connection_response = await websocket.recv()
        return connection_response
    
    def name_and_type(self):
        data = {"name":self.config.name , "type":self.config.type}
        return json.dumps(data)