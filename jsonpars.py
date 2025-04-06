import json
from collections import defaultdict
from removeModules import remove_modules

def pars_Json():
    data = remove_modules()
    # Initialize the new data structure
    output_data = {
        "fileMembers": defaultdict(list),
        "pkgFiles": defaultdict(list),
        "callGraph": defaultdict(list)
    }
    # Collect all unique functions from edges
    all_functions = set()
    for edge in data["edges"]:
        all_functions.add(edge["from"])
        all_functions.add(edge["to"])
    # Map nodes to files and packages
    file_to_pkg = defaultdict(set)
    for node in data["nodes"]:
        file_path = node["file"]
        function_name = node["label"]
        # Group functions by file
        output_data["fileMembers"][file_path].append(function_name)
        # Determine package by directory
        pkg_name = "/".join(file_path.split("/")[:-1])
        file_to_pkg[pkg_name].add(file_path)
    # Map edges to callGraph
    for edge in data["edges"]:
        caller = edge["from"]
        callee = edge["to"]
        relationship = edge["relationship"]

        output_data["callGraph"][caller].append({
            "caller": caller,
            "callee": callee,
            "site": relationship
        })
    # Assign files to packages
    for pkg, files in file_to_pkg.items():
        output_data["pkgFiles"][pkg] = list(files)
    # Convert defaultdicts to regular dicts
    output_data["fileMembers"] = dict(output_data["fileMembers"])
    output_data["pkgFiles"] = dict(output_data["pkgFiles"])
    output_data["callGraph"] = dict(output_data["callGraph"])
    # Output to file
    output_file_path = 'data/output.json'
    with open(output_file_path, 'w') as file:
        json.dump(output_data, file, indent=2)

    return output_data

pars_Json()
