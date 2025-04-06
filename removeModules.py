import json

def remove_modules():
    with open('data/call_graph.json', 'r') as file:
        json_data = json.load(file)

    # Filter nodes and edges
    symbolic_values = {
        "<<", "<", "==", ">", "=~", ">>", "=", "&", ">=", "+@", "-@", "%",
        "===", "!", "-", "*", "", "+", "<=>", "<=", "[]", "[]=", "[]?", "[]=?", "[]!"
    }

    filtered_nodes = [
        node for node in json_data['nodes']
        if not (has_module_prefix(node['id']) or node['id'] in symbolic_values or node['label'] in symbolic_values)
    ]

    filtered_edges = [
        edge for edge in json_data['edges']
        if not (has_module_prefix(edge['from']) or has_module_prefix(edge['to']) or
                edge['to'] in symbolic_values or edge['from'] in symbolic_values)
    ]

    # Create new JSON object with filtered data
    filtered_json = {
        "nodes": filtered_nodes,
        "edges": filtered_edges
    }

    # You can enable this if you want to store filtered results
    # with open('output.json', 'w') as file:
    #     json.dump(filtered_json, file, indent=2)

    return filtered_json


# Function to check if an ID contains "::"
def has_module_prefix(identifier):
    return "::" in identifier

