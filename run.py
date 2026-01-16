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
        traci.vehicle.setLaneChangeMode(veh_id, 512)

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    lock_lane_changes()

traci.close()
