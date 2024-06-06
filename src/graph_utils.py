def has_type(node, type):
    label = node.attr['label']
    return f'>{type}<' in label

def has_label(edge, label):
    return edge.attr['label'] == label

def find_node_in_edge(node1, node2, edges):
    if node1 is None:
        for e in edges:
            if e[1] == node2:
                return (e[0], node2)
    elif node2 is None:
        for e in edges:
            if e[0] == node1:
                return (node1, e[1])
    return (node1, node2)

def format_url(url : str):
    return url.replace('svg', 'dot').replace('./', '')


def generate_random_color():
    import random
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def extract_float_from_label(s : str):
    import re
    # Regular expression to find a floating-point number after '='
    match = re.search(r'=\s*([0-9]*\.?[0-9]+)', s)
    if match:
        return float(match.group(1))
    return None

def extract_vector_from_label(s : str):
    import re
    pattern = r'\((\d+),\s*(\d+)\)'
    
    # Use re.findall to extract all matching tuples
    match = re.search(pattern, s)
    if match:
        # Extract the groups and convert them to integers
        x, y = match.groups()
        return (int(x), int(y))
    else:
        return None  # Return None if no match is found
    
def extract_states_from_label(input_string : str):
    import re
    # Define the regex pattern to capture state_name and parameters
    pattern = r'MonitorState: (\w+)\[(.*?)\]'
    
    # Find all matches in the input string
    matches = re.findall(pattern, input_string)
    
    # Process the matches
    parsed_results = []
    for match in matches:
        state_name = match[0]
        parameters = match[1].split(', ') if match[1] else []
        parsed_results.append((state_name, parameters))
    
    return parsed_results

def check_and_extract_state_relation(s):
    import re
    pattern = r"relation_(\d+(?:_\d+)*)"
    
    # Find all matches in the given text
    matches = re.findall(pattern, s)
    
    return matches[0].split('_')

def hex_to_rgb(hex : str) -> tuple[float]:
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16)/255.0 for i in (0, 2, 4))

