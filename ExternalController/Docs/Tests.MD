# Tests
The unit tests for this application is mostly done to 
check the correctness of relations internally, relation execution is checked along with 
other state assertions. The unit tests could be ran by running `tests.py`

The integration tests for this application is done through setting up:

- One instance of the GeneralServer
- One instance of the ExternalMonitor
- One instance of EACH of the test clients `test_bot_execute.py`,`test_bot_read.py`, `test_non_bot.py`

The order to start the instances:

1. GeneralServer
2. ExternalMontior
3. `test_bot_read.py`
4. `test_bot_execute.py`
5. `test_non_bot.py`

## What are the main test points in the integration tests?
In the integration tests:
- We check if the relations are being successfully
added/removed by checking the state of the external controller.
- We check if the relations are being successfully executed by checking the 
  state of the external controller and the action history of the GeneralServer.
