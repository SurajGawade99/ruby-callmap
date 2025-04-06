import json
import hashlib
from typing import Dict, List, Union, Optional
from enum import Enum


class EdgeStyle(Enum):
    DEFAULT = 0
    DASHED = 1
    DOT_ARROW = 2


# Define the data structures
class EdgeNode:
    def __init__(self, table_id: int, node_id: int):
        self.table_id = table_id
        self.node_id = node_id

    def __repr__(self):
        return f"EdgeNode(table_id={self.table_id}, node_id={self.node_id})"


class Edge:
    def __init__(self, from_node: EdgeNode, to_node: EdgeNode, style: EdgeStyle):
        self.from_node = from_node
        self.to_node = to_node
        self.style = style

    def __repr__(self):
        return f"Edge(dst={self.from_node}, to={self.to_node}, style={self.style.name})"


class Node:
    def __init__(self, id: int, title: str, sub_nodes: Optional[List['Node']] = None, classes: Optional[List[str]] = None):
        self.id = id
        self.title = title
        self.sub_nodes = sub_nodes if sub_nodes is not None else []
        self.classes = classes if classes is not None else []

    def __repr__(self):
        return f"Node(id={self.id}, title='{self.title}', sub_nodes={self.sub_nodes}, classes={self.classes})"


class Table:
    def __init__(self, table_id: int, title: str, sections: List[Node]):
        self.table_id = table_id
        self.title = title
        self.sections = sections

    def __repr__(self):
        return f"Table(table_id={self.table_id}, title='{self.title}', sections={self.sections})"


class Cluster:
    def __init__(self, title: str, nodes: List[int], sub_clusters: Optional[List['Cluster']] = None):
        self.title = title
        self.nodes = nodes
        self.sub_clusters = sub_clusters if sub_clusters is not None else []

    def __repr__(self):
        return f"Cluster(title='{self.title}', nodes={self.nodes}, sub_clusters={self.sub_clusters})"


class Graph:
    def __init__(self, tables: List[Table], clusters: List[Cluster], edges: List[Edge]):
        self.tables = tables
        self.clusters = clusters
        self.edges = edges

    def __repr__(self):
        return f"Graph(tables={self.tables}, clusters={self.clusters}, edges={self.edges})"


# EdgeStyle determination function
def edge_style(edge) -> EdgeStyle:
    # Assuming site can be used to determine the style; defaults to DEFAULT
    if edge.get('site') == 'calls':
        return EdgeStyle.DEFAULT
    return EdgeStyle.DEFAULT


# Hashing function
def hash_string(s: str) -> int:
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16) & 0xFFFFFFFF


# Reversing function
def reverse(s: List):
    s.reverse()


# Graph generation function
def gen_graph(json_data: str) -> Graph:
    data = json_data

    file_members = data['fileMembers']
    pkg_files = data['pkgFiles']
    call_graph = data['callGraph']

    tables = []
    edge_set = set()
    function_to_node = {}

    # Create nodes from fileMembers
    for path, functions in file_members.items():
        file_id = hash_string(path)
        nodes = []

        for func in functions:
            node_id = hash_string(func)
            node = Node(id=node_id, title=func)
            nodes.append(node)
            function_to_node[func] = (file_id, node_id)

        reverse(nodes)

        tables.append(Table(
            table_id=file_id,
            title=path.split('/')[-1],
            sections=nodes
        ))

    # Create edges from callGraph
    for caller, edges in call_graph.items():
        if caller not in function_to_node:
            continue

        from_table_id, from_node_id = function_to_node[caller]

        for edge in edges:
            callee = edge['callee']
            if callee not in function_to_node:
                continue

            to_table_id, to_node_id = function_to_node[callee]
            edge_style_value = edge_style(edge)

            edge_set.add(Edge(
                from_node=EdgeNode(from_table_id, from_node_id),
                to_node=EdgeNode(to_table_id, to_node_id),
                style=edge_style_value
            ))

    # Create clusters from pkgFiles
    clusters = []
    for pkg, files in pkg_files.items():
        nodes = [hash_string(file) for file in files]
        cluster = Cluster(
            title=pkg,
            nodes=nodes
        )
        clusters.append(cluster)

    return Graph(
        tables=tables,
        clusters=clusters,
        edges=list(edge_set)
    )
