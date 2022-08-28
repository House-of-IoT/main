# Design
The ExternalController is an implementation of [ChainControlling](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master),this document will
go into depth about this specific implementation.

From this point forward we assume you know what ChainControlling is.

## How do we check if a relation should be executed?

We first start by gathering `passive data`(a collection of periodic data from all bots connected) from the GeneralServer, after
we have the passive data we check if ALL of the conditions of the relation are satisfied by the passive data.

For example if we had the following relation:
```JSON
{"device_name":"water_valve", "action":"open", "conditions":[{"device_name":"soil_monitor", "humidity":2}]}
```

and we had the following passive data come from the GeneralServer:
```JSON
{"bots" : [{"device_name":"soil_monitor", "active_status":True, "humidity":2}]}
```

we would see that all of the conditions in the relation are satisfied by the passive data, since there
is a bot by the name `soil_monitor` with the key `humidity` being equal to `2` which is outlined by the relation.


## How often do we check the relations against passive data?
Every 5 seconds we gather a set of passive data and compare it against our relations.
It could take longer than 5 seconds to gather the passive data depending on how quick the 
GeneralServer responds, this is directly dependent on network speed and other factors.

## Could this system perform with very little delay?
On top of the 5 second delay:
  This system is designed to be used for systems that aren't extremely time sensitive. There are different
  factors that could affect the speed of relation execution, these factors are all network and load based. 
  One should consider these factors when building a system around the ExternalMonitor. 

  Good system examples:  

  - Sprinkler system relation with a `sprinkler_bot` and a `light_monitor_bot`.
    - You would like to turn off the sprinkler when it gets too dark outside.
    - Not time sensitive because the sprinkler could be 5 seconds late turning off with no damage to the grass at all.
    
  - Smart Irrigation system with a `water_pump` and a `soil_moisture_sensor`.
    - You would like to turn on the water pump to supply water when the soil moisture sensor senses small amounts of moisture.
    - Not time sensitive because the plants aren't going to die with a lack of moisture for 5 seconds.

 Bad system examples:
  - Smart water tank regulator with a `tank_level_monitor` and a `empty_solenoid_valve`.
    - You would like open the empty_solenoid_valve when the tank reaches a certain level. 
    - This is time sensitive based on how fast the water is being pumped into the tank, but we are going to assume we don't have control over the pump.
      If we wait too long to open the value we could have water pressure issues if less than 5 seconds could be enough time for the tank to fill up.
 
 You could make the bad examples usable with this service by tweaking certain factors, but they are just examples. Design is VERY important when 
 using this service for your system(s).


