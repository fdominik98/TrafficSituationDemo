from frame import CarFrame
from pygraphviz import Node
from graph_utils import hex_to_rgb
import os
from maps import map_town_06

class ScenicScriptGenerator():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_folder_path = f'{current_directory}/../assets/scenic'
    carla_objects = False
    newtonian_objects = True
    
    common_lines1 = [
        'import os',
        'import sys',
        "param map = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maps/Town06.xodr'))",
        "sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/scenic_src')))",        
        'from follow_lane_edge import PartialLaneChangeBehavior',        
    ]
    carla_lines = [
        "param carla_map = 'Town06'",
        "param weather = 'ClearSunset'",
        "param timeout = 60",
        'param port = 2001',
        'param timestep = 0.04',
        "param record = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../record'))",
        #"param video_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../record'))",        
        'model scenic.simulators.carla.model',
    ]
    newtonian_lines = [
        "model scenic.simulators.newtonian.driving_model"
    ]
    common_lines2 = [
        "road = network.elements['road40']",
        'terminated = False'
    ]

    lanes = map_town_06 
    
    lanelet_length = 7
    offset = lanelet_length * 2
    SPEED = 10
    checkpoint_dist = 3
    
    def lanelet_left_width(self, lane):
        return lane[0][1] - lane[2][1]
    
    def lanelet_right_width(self, lane):
        return lane[1][1] - lane[3][1]
    
    def lanelet_left_center(self, lane):
        return (lane[0][0], (lane[0][1] + lane[2][1]) / 2)
    
    def lanelet_right_center(self, lane):
        return (lane[1][0], (lane[1][1] + lane[3][1]) / 2)
    
    def lane_length(self, lane):
        return abs(lane[0][0] - lane[1][0])
    
    def point_to_coordinates(self, point):
        x_d, y_d = point
        lane = self.lanes[point[0]]
        
        x_lane = lane[2][0] + self.offset + y_d * self.lanelet_length
        y_lane = (self.lanelet_left_center(lane)[1] + self.lanelet_right_center(lane)[1]) / 2
        return (x_lane, y_lane)  
   
    
    def __init__(self, frames : list[list[CarFrame]], road_length, output_file_name : str) -> None:
        self.road_length = road_length * self.lanelet_length
        self.frames : list[list[CarFrame]] = frames
        self.output_file_name = output_file_name
        self.car_behaviors : dict[Node, list[str]] = dict()
        self.car_frames : dict[Node, list[tuple[CarFrame, int, int]]] = dict()
        self.newton_road_objects : dict[tuple, str] = dict()
        self.carla_road_objects : dict[tuple, str] = dict()
        self.first_car_coords : dict[Node, tuple] = dict()
        self.start_coords : set[tuple[float, float]] = set()
        
        self.create_car_defs()
        self.compress_frames_and_create_objects()
          
        self.terminate_lines = []
        for car in self.car_frames.keys():
            self.create_terminate_line(car)
            self.create_behaviors(car)
            
        self.generate_artifact(True, 'carla')
        self.generate_artifact(False, 'newtonian')               


    def create_car_defs(self):
        self.carla_car_defs = []
        self.newtonian_car_defs = []
        for i, car_frame in enumerate(self.frames[0]):        
            opposite_true = ''
            facing = ''
            first_coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos)
            coords = (first_coords[0] - self.lanelet_length, first_coords[1])
            if not car_frame.is_forward:
                coords = (first_coords[0] + self.lanelet_length, first_coords[1])
                facing = f' facing toward {coords[0] - 10} @ {coords[1]},'
                opposite_true = 'True'
            self.start_coords.add(coords)
            car_def = f'{car_frame.name} = Car at {coords[0]} @ {coords[1]},{facing} with behavior {car_frame.name}Behavior({opposite_true}), with color Color{hex_to_rgb(car_frame.color)}, with requireVisible False'
            self.newtonian_car_defs.append(car_def)
            self.carla_car_defs.append(f"{car_def}, with blueprint '{car_frame.blueprint}'")
            self.car_behaviors[car_frame.car] = [f'behavior {car_frame.name}Behavior(is_oppositeTraffic=False):']
            self.first_car_coords[car_frame.car] = car_frame.cell_frame.abs_pos

    def compress_frames_and_create_objects(self):
        for car_frames in self.frames:
            for car_frame in car_frames: 
                if car_frame.car not in self.car_frames:
                    self.car_frames[car_frame.car] = [(car_frame, 1, 10000)]
                elif car_frame.cell_frame.abs_pos == self.car_frames[car_frame.car][-1][0].cell_frame.abs_pos:
                    frame, time_step, last = self.car_frames[car_frame.car][-1]
                    self.car_frames[car_frame.car][-1] = (frame, time_step + 1, last)
                    continue
                else:
                    self.car_frames[car_frame.car].append((car_frame, 1, self.car_frames[car_frame.car][-1][1]))

                coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos)
                if coords not in self.start_coords:
                    self.newton_road_objects[car_frame.cell_frame.abs_pos] = f'Object at {coords[0]} @ {coords[1]}, with requireVisible False'
                    self.carla_road_objects[car_frame.cell_frame.abs_pos] = f"Cone at {coords[0]} @ {coords[1]}, with blueprint 'static.prop.constructioncone', with requireVisible False"


    def create_terminate_line(self, car):
        last_car_frame = self.car_frames[car][-1][0]
        if last_car_frame.is_ego:
            last_coords = self.point_to_coordinates(last_car_frame.cell_frame.abs_pos)
            first_coords = self.point_to_coordinates(self.first_car_coords[car])
            terminate_line = (f'terminate when '
                                f'({last_car_frame.name}.speed < 0.01 and '
                                f'terminated) '
                                f'or (distance from {last_car_frame.name} to {first_coords[0]} @ {first_coords[1]}) > {self.road_length}')
            self.terminate_lines.append(terminate_line)


    def create_behaviors(self, car):
        car_frames = self.car_frames[car]
        num_frames = len(car_frames)
        for i, (car_frame, time_step, last_time_step) in enumerate(car_frames):
            coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos) 
            if time_step <= 2:
                magnitude = time_step
            else:
                magnitude = self.SPEED
            magnitude = time_step
            target_speed = self.SPEED / (magnitude)

            if time_step > last_time_step:
                self.car_behaviors[car].append(f'\ttake SetBrakeAction({1 - 1/magnitude})')
            
            if car_frame.cell_frame.is_intermediate:        
                self.car_behaviors[car].append(f'\tdo PartialLaneChangeBehavior({coords[0]} @ {coords[1]}, is_oppositeTraffic=is_oppositeTraffic, target_speed={target_speed}) until (distance from self to {coords[0]} @ {coords[1]}) < {self.checkpoint_dist}')
            else:
                self.car_behaviors[car].append(f'\ttarget_lane=road.laneAt({coords[0]} @ {coords[1]})')
                self.car_behaviors[car].append(f'\tdo FollowLaneBehavior(is_oppositeTraffic=is_oppositeTraffic, target_speed={target_speed}, laneToFollow=target_lane) until (distance from self to {coords[0]} @ {coords[1]}) < {self.checkpoint_dist}')
            if car_frame.is_ego:
                self.car_behaviors[car].append(f"\tprint('ego reached checkpoint ' + str({i+1})+'/'+ str({num_frames}))")
                self.car_behaviors[car].append(f"\tprint('ego speed: ' + str(self.speed))")
        self.car_behaviors[car].append('\ttake SetBrakeAction(0.9)')   

        last_car_frame = self.car_frames[car][-1][0]
        if last_car_frame.is_ego:
            self.car_behaviors[car].append(f'\tterminated = True')

        
    def generate_artifact(self, carla : bool, folder : str):
        target_file_path = f'{self.target_folder_path}/{folder}/{self.output_file_name}'

        with open(target_file_path, 'w') as target_file:
            for line in self.common_lines1:
                    target_file.write(line + '\n')
            if carla:
                for line in self.carla_lines:
                    target_file.write(line + '\n')
            else:
                for line in self.newtonian_lines:
                        target_file.write(line + '\n')
            for line in self.common_lines2:
                    target_file.write(line + '\n')
        
        with open(target_file_path, 'a') as target_file:
            target_file.write('\n')
            for car_node in self.car_behaviors.keys():
                for line in self.car_behaviors[car_node]:
                    target_file.write(line + '\n')
                target_file.write('\n')
            if carla:
                for line in self.carla_car_defs:
                    target_file.write(line + '\n')
                if self.carla_objects:
                    for coords in self.carla_road_objects.keys():
                        target_file.write(self.carla_road_objects[coords] + '\n')
            if not carla:
                for line in self.newtonian_car_defs:
                    target_file.write(line + '\n')
                if self.newtonian_objects:
                    for coords in self.newton_road_objects.keys():
                        target_file.write(self.newton_road_objects[coords] + '\n')
            target_file.write('\n')
            for terminate_line in self.terminate_lines:
                target_file.write(terminate_line + '\n')
    