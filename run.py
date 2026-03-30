import os
import sys
import traci
import sumolib
import csv
import pandas as pd

# Check SUMO environment
if 'SUMO_HOME' not in os.environ:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

SUMO_HOME = os.environ['SUMO_HOME']
sys.path.append(os.path.join(SUMO_HOME, 'tools'))

sumoBinary = sumolib.checkBinary('sumo-gui')

# Start SUMO simulation
traci.start([
    sumoBinary,
    "-c", "sim.sumocfg",
    "--lanechange.duration", "0"
])

# Lock lane changes for vehicles
def lock_lane_changes():
    for veh_id in traci.vehicle.getIDList():
        traci.vehicle.setLaneChangeMode(veh_id, 0)

# Function to get queue length of a lane in meters
def get_lane_queue_length(lane_id, junction_pos, max_distance=50):
    veh_ids = traci.lane.getLastStepVehicleIDs(lane_id)
    lane_length = traci.lane.getLength(lane_id)
    stopped_positions = []

    for vid in veh_ids:
        if traci.vehicle.getSpeed(vid) < 0.1:
            x, y = traci.vehicle.getPosition(vid)
            dx = x - junction_pos[0]
            dy = y - junction_pos[1]
            distance = (dx**2 + dy**2)**0.5
            if distance <= max_distance:
                pos = traci.vehicle.getLanePosition(vid)
                stopped_positions.append(pos)

    if not stopped_positions:
        return 0
    return round(lane_length - min(stopped_positions), 2)

# Function to check if vehicle is near junction
def is_vehicle_near_junction(veh_id, junction_pos, max_distance=50):
    x, y = traci.vehicle.getPosition(veh_id)
    dx = x - junction_pos[0]
    dy = y - junction_pos[1]
    distance = (dx**2 + dy**2)**0.5
    return distance <= max_distance

# Junction position
junction_x, junction_y = traci.junction.getPosition("middle_junction")
junction_pos = (junction_x, junction_y)
max_distance = 50

# Only lane 1 & 2
all_lanes = [lane for lane in traci.lane.getIDList() if lane.endswith("_1") or lane.endswith("_2")]

# Temporary dictionary to track if a lane ever has a non-zero queue
lane_has_queue = {lane: False for lane in all_lanes}

# Hardcoded traffic light phase durations from your tlLogic
phase_durations = [
    10, 0.5, 1,   # East green, yellow, red
    10, 0.5, 1,   # South green, yellow, red
    10, 0.5, 1,   # West green, yellow, red
    10, 0.5, 1    # North green, yellow, red
]

# Descriptive headers
phase_headers = [
    "east_green", "east_yellow", "east_red",
    "south_green", "south_yellow", "south_red",
    "west_green", "west_yellow", "west_red",
    "north_green", "north_yellow", "north_red"
]

# Open CSV and write header
csv_file = open("traffic_data.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
header = ["time", "total", "car", "bus", "bike", "truck"] + \
         [f"{lane}_queue" for lane in all_lanes] + phase_headers
csv_writer.writerow(header)

# Simulation loop
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1

    # Every 10 seconds
    if step % 10 == 0:
        # Active vehicles near junction on lane 1 & 2
        active_veh_ids = [
            vid for vid in traci.vehicle.getIDList()
            if (traci.vehicle.getLaneID(vid).endswith("_1") or traci.vehicle.getLaneID(vid).endswith("_2"))
            and is_vehicle_near_junction(vid, junction_pos, max_distance)
        ]

        total = len(active_veh_ids)

        # Count vehicle types
        type_counts = {"car": 0, "bus": 0, "bike": 0, "truck": 0}
        for vid in active_veh_ids:
            vtype = traci.vehicle.getTypeID(vid)
            if vtype in type_counts:
                type_counts[vtype] += 1

        # Queue lengths for lanes near junction
        lane_queues = [get_lane_queue_length(lane, junction_pos, max_distance) for lane in all_lanes]

        # Update lane_has_queue
        for i, q in enumerate(lane_queues):
            if q > 0:
                lane_has_queue[all_lanes[i]] = True

        # Write CSV row with hardcoded phase durations
        row = [
            step,
            total,
            type_counts["car"],
            type_counts["bus"],
            type_counts["bike"],
            type_counts["truck"]
        ] + lane_queues + phase_durations
        csv_writer.writerow(row)

    lock_lane_changes()

# Close simulation
traci.close()
csv_file.close()

# Filter lanes that never had any queue
filtered_lanes = [lane for lane, has_q in lane_has_queue.items() if has_q]

if filtered_lanes != all_lanes:
    df = pd.read_csv("traffic_data.csv")
    cols_to_keep = ["time", "total", "car", "bus", "bike", "truck"] + \
                   [f"{lane}_queue" for lane in filtered_lanes] + phase_headers
    df[cols_to_keep].to_csv("traffic_data_filtered.csv", index=False)

print("Simulation completed. CSV files generated: traffic_data.csv, traffic_data_filtered.csv")