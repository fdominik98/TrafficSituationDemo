import scenic
from my_carla_simulator import CarlaSimulator
import os
from scenic.simulators import carla
from manage_carla import run_carla, terminate_carla, get_files_in_folder

terminate_carla()
run_carla()

current_directory = os.path.dirname(os.path.abspath(__file__))
scenic_script_dir = f'{current_directory}/assets/scenic/carla'
scenic_scripts = get_files_in_folder(scenic_script_dir)
# Load the Scenic scenario
scenario = scenic.scenarioFromFile(scenic_scripts[0][0])

# Connect to the CARLA simulator
simulator = CarlaSimulator(carla_map = scenario.params['carla_map'],
                        map_path = scenario.params['map'],
                        address = scenario.params['address'],
                        port = scenario.params['port'],
                        timeout = scenario.params['timeout'],
                        render = scenario.params['render'],
                        record = scenario.params['record'],
                        timestep = scenario.params['timestep'],
                        video_output_path = None if 'video_output_path' not in scenario.params else scenario.params['video_output_path'])

for i in range(5):
    for file_path, file in scenic_scripts:
        scenario = scenic.scenarioFromFile(file_path)
        scene, _ = scenario.generate()
        simulation = simulator.createSimulation(scene, verbosity=1, solution_name=file)
        simulation.run(85 / scenario.params['timestep'])


terminate_carla()
