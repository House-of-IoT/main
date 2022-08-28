from Core.general_server_client import GeneralServerClient
from Core.server import Server
from Config.config import gather_config
from Core.console_logger import ConsoleLogger
from Core.relation_manager import RelationManager
import websockets
import asyncio

class Main:
    def __init__(self):
        self.console_logger = ConsoleLogger(self)
        self.config = gather_config()
        self.server_config = gather_config(
            file_name = "server_config.json",
            env_pw_name="hoi_exc_s_pw")
        self.general_server_client = GeneralServerClient(self,self.config)
        self.relation_manager = RelationManager(self)
        self.server = Server(self,self.server_config)

    def start(self):
        self.console_logger.start_message()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            websockets.serve(
                self.server.authenticate_client_after_connection,
                self.server.config["host"],
                self.server.config["port"],
                ping_interval=None))
        loop.run_until_complete(self.general_server_client.main())
        loop.run_until_complete(self.console_logger.reset_row_num())
        loop.run_forever()

if __name__ == "__main__":
    main = Main()
    main.start()