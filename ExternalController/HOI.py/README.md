# HOI.py
A bot client library for HOI.
 
This library handles the authentication protocol and main task execution for you abstracting the event loop away. To learn more about usage and implementation
please take a look in the docs section of this repository.


# Sample Usage for bots
The client in this piece of code handles the authentication protocol and task execution. The implementation has no limits to the amount of tasks that 
can be executed in the main event loop. You will need to pass a list of tasks to `client.main` as the second argument as seen in the
example below. Ideally you would have two tasks, one for listening to the server for control requests and one for monitoring the state
of the hardware(sensors and other setups). Please check [MotionDetectionCamera](https://github.com/House-of-IoT/MotionDetectionCamera) to see a real world example of this lib being used.

```python3
    import hoi_client
    
    async def task_one():
        pass
        
    async def task_two():
        pass
        
    async def main():
        #setup config and client
        config = hoi_client.Config(PORT,HOST,PASSWORD,NAME,TYPE)
        client = hoi_client.Client(config)
        
        #gather websocket connection
        websocket = client.establish_connection()      
        
        #send credentials and gather response
        response = await client.send_connection_credentials(websocket)
        
        #check the response and continue
        if response == "success":
            tasks = [task_one(),task_two()]
            await client.main(websocket,tasks)
        else:
            print("auth failed")
            


```
