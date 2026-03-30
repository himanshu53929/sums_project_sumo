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


# State
east_path = "GGGGGGGrrrGGrrrGGrrr"
first_buffer = "GGyyyGGrrrGGrrrGGrrr"

south_path = "GGrrrGGGGGGGrrrGGrrr"
second_buffer = "GGrrrGGyyyGGrrrGGrrr"

west_path = "GGrrrGGrrrGGGGGGGrrr"
third_buffer = "GGrrrGGrrrGGyyyGGrrr"

north_path = "GGrrrGGrrrGGrrrGGGGG"
fourth_buffer = "GGrrrGGrrrGGrrrGGyyy"



tl_id = "middle_junction"


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


traci.close()