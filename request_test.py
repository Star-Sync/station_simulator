import requests
from datetime import datetime, timedelta

# Flask API URL (adjust the host and port if necessary)
API_URL = "http://127.0.0.1:5000"

# Example 1: Scheduling a state change (POST request)
def schedule_pass(station, start_time, end_time, state, mission="Idle"):
    pass_data = {
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "state": state,
        "mission": mission
    }
    
    response = requests.post(f"{API_URL}/{station}/schedule_pass/", json=pass_data)
    
    if response.status_code == 200:
        print("Pass scheduled at {station}:", response.json())
    else:
        print("Error scheduling pass at {station}:", response.json())

# Example 2: Querying the state at a specific time (GET request)
def query_state_at(station, query_time):
    formatted_query_time = query_time.strftime("%Y-%m-%dT%H:%M:%S")
    response = requests.get(f"{API_URL}/{station}/query_state_at/{formatted_query_time}")
    
    if response.status_code == 200:
        print(f"State at {station} at {formatted_query_time}:", response.json())
    else:
        print(f"Error querying state at {station} at {formatted_query_time}:", response.json())

# Example 3: Querying busy times within a time range (GET request)
def query_busy_times(station, start_time, end_time):
    formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    formatted_end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")
    response = requests.get(f"{API_URL}/{station}/query_busy_times/", params={
        "start_time": formatted_start_time,
        "end_time": formatted_end_time
    })
    
    if response.status_code == 200:
        print(f"Busy times for {station} between {formatted_start_time} and {formatted_end_time}:", response.json())
    else:
        print(f"Error querying busy times for {station} between {formatted_start_time} and {formatted_end_time}:", response.json())

# Main execution
if __name__ == '__main__':
    # Schedule a state change
    station = "GATN"
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=1,minutes=10)
    schedule_pass(station, start_time, end_time, "science_busy", "Research A")
    start_time = datetime.now() + timedelta(hours=1,minutes=30)
    end_time = datetime.now() + timedelta(hours=1,minutes=45)
    schedule_pass(station, start_time, end_time, "telemetry_busy", "Research B")
    start_time = datetime.now() + timedelta(hours=1,minutes=20)
    end_time = datetime.now() + timedelta(hours=1,minutes=26)
    schedule_pass(station, start_time, end_time, "telemetry_busy", "Research B")

    # Query the state at a specific time
    query_time = datetime.now() + timedelta(hours=1, minutes=30)
    query_state_at(station, query_time)

    # Query busy times within a specific range
    range_start_time = datetime.now() + timedelta(hours=0, minutes=30)
    range_end_time = datetime.now() + timedelta(hours=3)
    query_busy_times(station, range_start_time, range_end_time)
