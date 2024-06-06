import pygraphviz as pgv
from pygraphviz import Node
from graph_utils import find_node_in_edge, format_url, extract_float_from_label

class DotToTrajectoryParser():
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.graph = pgv.AGraph(file_path)
        self.solutions : list[list[tuple[str, float]]] = []
        self.parse_trajectory()
        
    def parse_trajectory(self):
        edges = self.graph.edges()
        root_node = "0"
        solution_nodes : list[Node] = []
        for node in self.graph.nodes():
            if node.attr['peripheries'] == '2':
                solution_nodes.append(node)
            if node not in {y for _, y in edges}:
                root_node = node
                
        for node in solution_nodes:
            current_node = node
            path_list : list[tuple[str, float]] = []
            while current_node != root_node:
                path_list.append(self.get_values(current_node))          
                current_node = find_node_in_edge(None, current_node, edges)[0]
            path_list.append(self.get_values(current_node))
            path_list.reverse()
            self.solutions.append(path_list)
        
    def get_values(self, node):
        return ((format_url(node.attr['URL']), extract_float_from_label(node.attr['label'])))