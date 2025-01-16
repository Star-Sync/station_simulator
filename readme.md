## Getting Started

### Prerequisites
* Python

### Installation
1. Create and activate python virtual environment (recommended)
    ```sh
    python -m venv new_venv
    ```
    Linux
    ```
    source new_venv/bin/activate
    ```
    Windows
    ```
    new_venv/Scripts/activate 
    ```
2. Install required python packages
    ```sh
    pip install -r requirements.txt
    ```

### Usage
* Start the station simulator state machine
    ```sh
    python State_machines.py
    ```
* The station simulator flask app should now be functioning and ready to receive API calls.  By default the app is running on 127.0.0.1:5000

* You can run request_test.py to quickly ensure it's functioning properly

* You can also see some sample requests in testendpoints.http

The station simulator functions as multiple relatively simple time based state machines.

The states are:
* free: the station is available and not in use
* science_busy: the station is being used to downlink science only
* telemetry_busy: the station is being used to downlink telemetry only
* both_busy: the station is being used to downlink both science and telemetry

The stations are:
* ICAN 
* GATN 
* PASS
### API Description

#### POST

There is currently only one POST endpoint which controls scheduling a pass at the station

##### SCHEDULE PASS

```
http://{API_URL}/{station}/schedule_pass/

content-type: application/json

{
    "start_time": "YYYY-MM-DDTHH:MM:SS",
    "end_time": "YYYY-MM-DDTHH:MM:SS",
    "state": "{desired_state}",
    "mission": "{mission_name}"
}
```
#### GET

There are two different calls you can make via GET. 

##### QUERY STATE
The first is a query for the state of the station at a particular time. The parameters for this call will be the station and a particular time.
```
{API_URL}/{station}/query_state_at/{YYYY-MM-DDTHH:MM:SS}
```
The response to this call will be a state and a mission.
* state = [free, both_busy, science_busy, telemetry_busy]
* mission = idle if not in use or specific mission

##### QUERY BUSY TIMES
The second is a query to determine when the station is in use.
```
{API_URL}/{station}/query_busy_times/?start_time={YYYY-MM-DDTHH:MM:SS}&end_time={YYYY-MM-DDTHH:MM:SS}
```
The response to this call will be a start and end time as well as a state