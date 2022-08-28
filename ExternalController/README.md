# ExternalController
A service that controlls devices in relation to each other. Used to trigger device's actions based on  other device's data.

# When to use an instance of the external controller?
 
 You would setup an instance of the external controller when you have a 
 select amount of devices that have direct relationship in action execution. 
 The external controller is a implemenetation of the concept [ChainControlling](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/ChainControlling.MD).
 
 A good usage for the external controller would be a smart irrigation system
 or basically when one device needs to trigger an action of another device based on its own data.
 
 # Example
 
 Suppose you had a soil moisture/humidity smart device that would trigger a water valve smart device. You would use the external controller to set up this relationship.
 
 But how?
 
 the external controller would monitor the soil moisture/humidity's passive data and determine if it should trigger the device.
 
 # Conditions
 
 The way that the external controller knows when a action should be triggered is through "conditions" aka "relations".
 
 Take a look at this [document](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/ChainControlling.MD) to get more information on the technical aspect of how 
 conditions are setup.
 
 
# How do you setup this service and its relational actions?

1.  Clone the repository
2.  Run `python3 config.py` which is for server connectivity since the external monitor is just a "non-bot" client.
3.  Run `python3 relational_config.py` which is for setting up action relations. It will prompt you for information on your relations.
4.  Run `python3 main.py`
 
 
 
