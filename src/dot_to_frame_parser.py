import pygraphviz as pgv
from pygraphviz import Node, Edge
from graph_utils import (find_node_in_edge,
                         has_label, has_type,
                         check_and_extract_state_relation,
                         generate_random_color,
                         extract_states_from_label, extract_vector_from_label)
from state import State

class DotToFrameParser():
    
    car_color_mapping : dict[str, str] = dict()
    
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.graph = pgv.AGraph(file_path)
        self.cells : list[list[Node]] = []
        self.car_cells : dict[Node, Node] = dict()
        self.ego_cars : set[Node] = set()
        self.intermediate_lanes : set[Node] = set()
        self.forward_lanes : set[Node] = set()
        self.reverse_lanes : set[Node] = set()
        self.intended_lane_edges : set[Edge] = set()
        self.containing_lane_edges : set[Edge] = set()
        self.state_tokens : set[State] = set()
        
        self.parse_cells()
        
    def parse_cells(self):
        cell_nodes : set[tuple[Node, int, int]] = set()
        car_nodes : set[Node] = set()
        on_cell_edges : set[Edge] = set()   
        all_nodes = self.graph.nodes()     
        
        for node in all_nodes:            
            if has_type(node, 'Cell'):
                coords = extract_vector_from_label(node.attr['label'])
                cell_nodes.add((node, coords[0], coords[1]))
            elif has_type(node, 'ForwardLane'):
                self.forward_lanes.add(node)
            elif has_type(node, 'ReverseLane'):
                self.reverse_lanes.add(node)
            elif has_type(node, 'IntermediateLane'):
                self.intermediate_lanes.add(node)
            elif has_type(node, 'Car'):
                car_nodes.add(node)
                if has_type(node, 'Ego'):
                    self.ego_cars.add(node)
                                
            states = extract_states_from_label(node.attr['label'])
            for state in states:
                if len(state[1]) == 0:
                    self.state_tokens.add(State(state[0], [], []))
                elif len(state[1]) == 1:
                    self.state_tokens.add(State(state[0], [str(node)], state[1]))
                elif len(state[1]) > 2:
                    state_relation = check_and_extract_state_relation(node.attr['label'])
                    self.state_tokens.add(State(state[0], state_relation, state[1]))
                
        for edge in self.graph.edges():
            if has_label(edge, 'OnCell'):
                on_cell_edges.add(edge)
            elif has_label(edge, 'IntendedLane'):
                self.intended_lane_edges.add(edge)
            elif has_label(edge, 'ContainingLane'):
                self.containing_lane_edges.add(edge)  
            else:
                states = extract_states_from_label(edge.attr['label'])
                for state in states:
                    self.state_tokens.add(State(state[0], [str(edge[0]), str(edge[1])], state[1]))
        
        self.cells = self.create_transposed_grid(cell_nodes)
            
        for car_node in car_nodes:
            self.car_cells[find_node_in_edge(car_node, None, on_cell_edges)[1]] = car_node
            

    def create_transposed_grid(self, coordinates) -> list[list[Node]]:
        # Determine the dimensions of the grid
        max_x = max(coord[2] for coord in coordinates)
        max_y = max(coord[1] for coord in coordinates)
        
        # Initialize the grid with None or a placeholder value
        grid = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        
        # Populate the grid with the coordinates
        for node, x, y in coordinates:
            grid[x][y] = node
        
        return grid
    
    def is_forward(self, car):
        lane = find_node_in_edge(car, None, self.intended_lane_edges)[1]
        return lane in self.forward_lanes
    
    def is_intermediate(self, cell):
        lane = find_node_in_edge(cell, None, self.containing_lane_edges)[1]
        return lane in self.intermediate_lanes
    
    @staticmethod
    def get_car_color(car_node):
        if car_node not in DotToFrameParser.car_color_mapping:
            DotToFrameParser.car_color_mapping[car_node] = generate_random_color()
        return DotToFrameParser.car_color_mapping[car_node]
    

    
    