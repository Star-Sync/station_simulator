from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from pydantic import BaseModel
from transitions import Machine

# Define the states
states = ['free', 'science_busy', 'telemetry_busy', 'both_busy']

class TimeBasedStateMachine:
    def __init__(self,name):
        self.name = name
        self.machine = Machine(model=self, states=states, initial='free')
        self.machine.add_transition(trigger='to_both_busy', source='*', dest='both_busy')
        self.machine.add_transition(trigger='to_science_busy', source='*', dest='science_busy')
        self.machine.add_transition(trigger='to_telemetry_busy', source='*', dest='telemetry_busy')
        self.machine.add_transition(trigger='to_free', source='*', dest='free')

        # Store scheduled state changes with (start_time, end_time, state, mission)
        self.scheduled_changes = []

    def schedule_pass(self, start_time, end_time, target_state, mission="Idle"):
        """Schedule a pass with a specific start and stop time and an optional mission."""
        if target_state not in states:
            raise ValueError(f"Invalid state: {target_state}")

        # Check for overlaps or insufficient gaps
        for scheduled_start, scheduled_end, _, _ in self.scheduled_changes:
            # Check if the new change is too close to an existing one
            if abs((start_time - scheduled_end).total_seconds()) < 300 or abs((end_time - scheduled_start).total_seconds()) < 300:
                raise ValueError("Pass is too close to an existing reservation (minimum gap: 5 minutes)")

            # Check for overlapping times
            if not (end_time <= scheduled_start or start_time >= scheduled_end):
                raise ValueError("Time window overlaps with an existing pass")

        # If no conflicts, schedule the state change
        self.scheduled_changes.append((start_time, end_time, target_state, mission))
        self.scheduled_changes.sort(key=lambda x: x[0])


    def query_state_at(self, query_time):
        """Query what the state and mission will be at a specific time."""
        current_state = 'free'
        current_mission = "Idle"
        
        for start_time, end_time, state, mission in self.scheduled_changes:
            if start_time <= query_time <= end_time:
                current_state = state
                current_mission = mission
                break
        
        return current_state, current_mission

    def get_busy_times_in_range(self, start_range, end_range):
        """Return all busy time periods in the given time range."""
        busy_times = []
        
        # Loop through the scheduled changes and check if the state is busy in the given range
        for start_time, end_time, state, _ in self.scheduled_changes:
            # Check if the state is busy and if it overlaps with the time range
            if state in ['science_busy', 'telemetry_busy', 'both_busy']:
                overlap_start = max(start_time, start_range)
                overlap_end = min(end_time, end_range)
                if overlap_start < overlap_end:  # Ensure there is an overlap
                    busy_times.append((overlap_start, overlap_end, state))
        
        return busy_times


# Flask app
app = Flask(__name__)

# Create instance of the state machine for each station
state_machines = {
    "ICAN": TimeBasedStateMachine("ICAN"),
    "GATN": TimeBasedStateMachine("GATN"),
    "PASS": TimeBasedStateMachine("PASS"),
}

# Pydantic model to accept state change data (Flask will validate the JSON input)
class StateChangeRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    state: str
    mission: str = "Idle"  # Default to "Idle" if no mission is specified


# API endpoint to schedule a state change
@app.route('/<machine_name>/schedule_pass/', methods=['POST'])
def schedule_pass(machine_name):
    try:
        if machine_name not in state_machines:
            return jsonify({"error": f"{machine_name} not a valid station"}), 404
        machine = state_machines[machine_name]
        
        # Parse the incoming JSON data
        data = request.get_json()
        
        # Create StateChangeRequest from the incoming data
        state_change = StateChangeRequest(**data)

        # Schedule the state change
        machine.schedule_pass(state_change.start_time, state_change.end_time, state_change.state, state_change.mission)
        
        return jsonify({
            "message": f"Scheduled pass at {machine_name} to {state_change.state} from {state_change.start_time} to {state_change.end_time} with mission {state_change.mission}"
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to schedule pass"}), 500



# API endpoint to query the state at a specific time
@app.route('/<machine_name>/query_state_at/<query_time>', methods=['GET'])
def query_state_at(machine_name, query_time):
    try:
        if machine_name not in state_machines:
            return jsonify({"error": f"{machine_name} not a valid station"}), 404
        machine = state_machines[machine_name]
        
        # Parse the query time from the URL parameter
        query_time_obj = datetime.strptime(query_time, "%Y-%m-%dT%H:%M:%S")
        
        # Query the state at that time
        state, mission = machine.query_state_at(query_time_obj)
        return jsonify({"state": state, "mission": mission}), 200

    except ValueError:
        return jsonify({"error": "Invalid time format. Use 'YYYY-MM-DDTHH:MM:SS'."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API endpoint to query all busy times in a specific range
@app.route('/<machine_name>/query_busy_times/', methods=['GET'])
def query_busy_times(machine_name):
    try:
        if machine_name not in state_machines:
            return jsonify({"error": f"{machine_name} not a valid station"}), 404
        machine = state_machines[machine_name]

        # Get start_time and end_time from query parameters
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        if not start_time_str or not end_time_str:
            return jsonify({"error": "Both 'start_time' and 'end_time' query parameters are required"}), 400

        # Parse the start_time and end_time
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S")

        # Get all busy times in the range
        busy_times = machine.get_busy_times_in_range(start_time, end_time)
        return jsonify({
            "busy_times": [{"start_time": bt[0].strftime("%Y-%m-%dT%H:%M:%S"),
                             "end_time": bt[1].strftime("%Y-%m-%dT%H:%M:%S"),
                             "state": bt[2]} for bt in busy_times]
        }), 200

    except ValueError:
        return jsonify({"error": "Invalid time format. Use 'YYYY-MM-DDTHH:MM:SS'."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)
