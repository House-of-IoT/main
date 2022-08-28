# Setup 

To setup an instance of the ExternalController you will need to generate two config files along with the correct 
environmental variables to match.

## The GeneralServer Client Config
 This config will contain all of the credentials needed to connect to the
 GeneralServer. To generate this config you could simply run the `config.py` file
 and answer `Y` to the question `would you like to set up config for connecting to the general server?[y/n]:`
 from here you will answer the questions and move your generated config file to the base directory.
 
## The ExternalMonitor Server Config
  This config will contain all of the information needed to host the external monitor's server.
  To generate this config you could simply run the `config.py` file
  and answer `N` to the question `would you like to set up config for connecting to the general server?[y/n]:`
  from here you will answer the questions and move your generated config file to the base directory.
  
## Environmental variables
  - `hoi_exc_s_pw` is the password for the ExternalMonitor Server. This password is what clients will be prompted for when trying to connect.
  - `hoi_mdc_pw` is the password for the GeneralServer. This password is what will be used to try to connect to the GeneralServer when gathering passive data.
  - `hoi_exc_a_pw` is the admin password for the GeneralServer. THis password is needed for when admin authentication is required for action execution.
## Start
There are two options to start the ExternalController:
- Install all the dependencies locally and running `main.py`(in the root directory)
- Using the dockerfile to run the service in a docker container.
