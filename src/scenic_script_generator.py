from frame import CarFrame
from pygraphviz import Node
from graph_utils import hex_to_rgb
import os

class ScenicScriptGenerator():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_folder_path = f'{current_directory}/../assets/scenic'
    OBJECTS = False
    
    common_lines1 = [
        'import os',
        'import sys',
        "param map = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../maps/Town06.xodr'))",
        "sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/scenic_src')))",        
        'from follow_lane_edge import PartialLaneChangeBehavior'
    ]
    carla_lines = [
        "param carla_map = 'Town06'",
        "param weather = 'ClearSunset'",
        "param timeout = 60",
        'param port = 2001',
        "param record = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../record'))",
        'model scenic.simulators.carla.model',
    ]
    newtonian_lines = [
        "model scenic.simulators.newtonian.driving_model"
    ]
    common_lines2 = [
        "road = network.elements['road40']"
    ]
        
    lane5=((128.5, -235.9), (599, -236),
        (128.5, -239.25), (599, -239.4)) 
    
    intermediate_lane54=((128.5, -239.25), (599, -239.4),
                         (128.5, -239.38), (599, -239.54))

    lane4=((128.5, -239.38), (599, -239.54),
            (128.5, -242.75), (599, -242.9)) 
    
    intermediate_lane43=((128.5, -242.75), (599, -242.9),
                         (128.5, -242.9), (599, -243))

    lane3=((128.5, -242.9), (599, -243),
            (128.5, -246.25), (599, -246.4)) 
    
    intermediate_lane32=((128.5, -246.25), (599, -246.4),
                         (128.5, -246.4), (599, -246.55))

    lane2=((128.5, -246.4), (599, -246.55),
            (128.5, -249.75), (599, -249.9))
    
    intermediate_lane21=((128.5, -249.75), (599, -249.9),
                         (128.5, -249.9), (599, -250)) 

    lane1=((128.5, -249.9), (599, -250),
            (128.5, -253.25), (599, -253.4)) 
    
    lanelet_length = 10
    offset = 30
    SPEED = 8.0
    checkpoint_dist = 2
    
    lanes = [lane5, intermediate_lane54, lane4, intermediate_lane43, lane3, intermediate_lane32, lane2, intermediate_lane21, lane1]
       
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
   
    
    def __init__(self, frames : list[list[CarFrame]], output_file_name : str) -> None:
        self.frames : list[list[CarFrame]] = frames
        self.output_file_name = output_file_name
        self.car_behaviors : dict[Node, list[str]] = dict()
        self.car_frames : dict[Node, list[tuple[CarFrame, int]]] = dict()
        self.newton_road_objects : dict[tuple, str] = dict()
        self.carla_road_objects : dict[tuple, str] = dict()
        self.first_car_coords : list[tuple] = []
        
        self.car_defs = []
        for i, car_frame in enumerate(self.frames[0]):        
            car_var = 'ego'
            opposite_true = ''
            facing = ''
            coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos)
            if not car_frame.is_ego:
                car_var = f'car{i}'
                ego_last_coords = coords
            if not car_frame.is_forward:
                facing = f' facing toward {coords[0] - 10} @ {coords[1]},'
                opposite_true = 'True'
            car_def = f'{car_var} = Car at {coords[0]} @ {coords[1]},{facing} with behavior {car_var}Behavior({opposite_true}), with color Color{hex_to_rgb(car_frame.color)}'
            self.car_defs.append(car_def)
            self.car_behaviors[car_frame.car] = [f'behavior {car_var}Behavior(is_oppositeTraffic=False):']
            self.car_frames[car_frame.car] = [(car_frame, 1)]
            self.first_car_coords.append(car_frame.cell_frame.abs_pos)
            
                
        for car_frames in self.frames[1:]:
            for car_frame in car_frames: 
                if car_frame.cell_frame.abs_pos == self.car_frames[car_frame.car][-1][0].cell_frame.abs_pos:
                    frame, time_step = self.car_frames[car_frame.car][-1]
                    self.car_frames[car_frame.car][-1] = frame, time_step + 1
                else:
                    self.car_frames[car_frame.car].append((car_frame, 1))
                    coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos)
                    
                    if car_frame.cell_frame.abs_pos not in self.first_car_coords:
                        self.newton_road_objects[car_frame.cell_frame.abs_pos] = f'Object at {coords[0]} @ {coords[1]}'
                        self.carla_road_objects[car_frame.cell_frame.abs_pos] = f'Box at {coords[0]} @ {coords[1]}'
          
        for car in self.car_frames.keys():
            for car_frame, time_step in self.car_frames[car]:
                coords = self.point_to_coordinates(car_frame.cell_frame.abs_pos)      
                target_speed = self.SPEED / (time_step * time_step)
                
                if car_frame.cell_frame.is_intermediate:        
                    self.car_behaviors[car_frame.car].append(f'\tdo PartialLaneChangeBehavior({coords[0]} @ {coords[1]}, is_oppositeTraffic=is_oppositeTraffic, target_speed={target_speed}) until (distance from self to {coords[0]} @ {coords[1]}) < {self.checkpoint_dist}')
                else:
                    self.car_behaviors[car_frame.car].append(f'\ttarget_lane=road.laneAt({coords[0]} @ {coords[1]})')
                    self.car_behaviors[car_frame.car].append(f'\tdo FollowLaneBehavior(is_oppositeTraffic=is_oppositeTraffic, target_speed={target_speed}, laneToFollow=target_lane) until (distance from self to {coords[0]} @ {coords[1]}) < {self.checkpoint_dist}')
            
        for car_frame in self.frames[-1]:
            self.car_behaviors[car_frame.car].append('\ttake SetBrakeAction(1.0)')
        
        self.terminate_line = f'terminate when ego.speed < 0.01 and (distance from ego to {ego_last_coords[0]} @ {ego_last_coords[1]}) < {self.checkpoint_dist}'
            
        self.generate_artifact(True, 'carla')
        self.generate_artifact(False, 'newtonian')               
                
                
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
            for line in self.car_defs:
                target_file.write(line + '\n')
            if self.OBJECTS:
                if carla:
                    road_objects = self.carla_road_objects
                else:
                    road_objects = self.newton_road_objects
                for coords in road_objects.keys():
                    target_file.write(road_objects[coords] + '\n')
    
            target_file.write(self.terminate_line + '\n')
    