import json 
import hoi_client
import os

"""
Set config for the server or the GeneralServer
"""
def set_config(file_name = None):
    data_dict = {}
    data_dict["host"] = input('host:\n')
    data_dict["port"] = int(input("port:\n"))
    if file_name == None:
        data_dict["name"] = input("name:\n")
        data_dict["type"] = input("type:")

    if file_name == None:
        file_name = "config.json"

    with open(file_name , "w") as File:
        data_to_write = json.dumps(data_dict)
        File.write(data_to_write)

"""
Gather config for either the server hosting or 
the GeneralServer
"""
def gather_config(file_name = None, env_pw_name = "hoi_mdc_pw"):

    if file_name == None:
        file_name = "config.json"

    with open(file_name , "r") as File:
        data = json.loads(File.read())
        password = os.environ.get(env_pw_name)
        print(password)
        data["password"] = password
        if env_pw_name != "hoi_mdc_pw":
            return data
        else:
            config = hoi_client.Config(
                data["port"],
                data["host"],
                password,
                data["name"],
                data["type"])
            return config
       
if __name__ == "__main__":
    input_data = input("would you like to set up config for connecting to the general server?[y/n]:")

    if input_data == "y" or input_data == "Y":
        set_config()
    else:
        set_config("server_config.json")