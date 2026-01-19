import os
import sys
import traci
import sumolib

if 'SUMO_HOME' not in os.environ:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

SUMO_HOME = os.environ['SUMO_HOME']
sys.path.append(os.path.join(SUMO_HOME, 'tools'))

sumoBinary = sumolib.checkBinary('sumo-gui')

traci.start([
    sumoBinary,
    "-c", "sim.sumocfg",
    "--lanechange.duration", "0"
])

def lock_lane_changes():
    for veh_id in traci.vehicle.getIDList():
        traci.vehicle.setLaneChangeMode(veh_id, 0)

# # Duration
# small_traffic = "10"
# medium_traffic = "20"
# large_traffic = "30"

# # State
# horizontal_lane = "GGGrrGGrrrGGGrrGGrrr"
# first_buffer = "GGyrrGGrrrGGyrrGGrrr"

# vertical_lane = "GGrrrGGGrrGGrrrGGGrr"
# second_buffer = "GGrrrGGyrrGGrrrGGyrr"

# horizontal_diagonal_lane = "GGrrGGGrrrGGrrGGGrrr"
# third_buffer = "GGrryGGrrrGGrrGGyrrr"

# vertical_diagonal_lane = "GGrrrGGrrGGGrrrGGrrG"
# fourth_buffer = "GGrryGGrrrGGrryGGrrr"

# # List of count of vehicles which comes from yolo model
# traffic_count = []

tl_id = "middle_junction"
# previous_state = traci.trafficlight.getRedYellowGreenState(tl_id)
# print("Initial traffic light state of ", tl_id, "is ", previous_state)

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    state = traci.trafficlight.getRedYellowGreenState(tl_id)
    links = traci.trafficlight.getControlledLinks(tl_id)

    for veh in traci.vehicle.getIDList():
        lane = traci.vehicle.getLaneID(veh)

        if not lane.endswith("_0"):
            continue

        for i, group in enumerate(links):
            for fromLane, toLane, via in group:
                if lane == fromLane and state[i] == "G":
                    traci.vehicle.setSpeedMode(veh, 32)
                    traci.vehicle.setSpeed(veh, traci.lane.getMaxSpeed(lane))


    lock_lane_changes()

    # current_state = traci.trafficlight.getRedYellowGreenState(tl_id)

    # if(previous_state != current_state):
    #     phase_index = traci.trafficlight.getPhase(tl_id)
    #     phase_duration = traci.trafficlight.getPhaseDuration(tl_id)
    #     print(f"Current traffic light state of {tl_id} is {current_state} it has phase index of {phase_index} and it has phase duration of {phase_duration}")
    #     previous_state = current_state

traci.close()