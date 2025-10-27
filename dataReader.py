import pydot
from dataStructures import Edge, Node, Graph
import numpy as np
from directedGraph import DAG, LayerAssignment, set_node_positions

# read .dot file and return graph
def ReadFromDOT(file_name:str, layout:str) -> tuple[Graph, bool]:
    G = pydot.graph_from_dot_file(file_name)[0]
    is_directed:bool = "digraph" in G.to_string()
    #initialize data structures
    node_dict:dict[int, Node] = dict()
    edges:list[Edge] = []

    ## subgraphs
    layers = G.get_subgraph_list()
    
    if layers == []:
        layers = [G]
    for h in layers:
        for n in h.get_node_list():
            node_name = n.get_name()
            if node_name[0] == "n":
                node_name = node_name[1:]
            node_idx:int = int(node_name)
            pos:np.array = np.array([0, 0])
            displacement_vector = np.array([0, 0])
            node:Node = Node(node_idx, pos, 0, [], False, [], 0, 0, 0, 0, displacement_vector, [],[], False, h.get_name())
            node_dict[node_idx] = node

    for e in G.get_edge_list():
        weight = e.get_attributes().get('weight')
        # if weight does not exist, set to -1, assuming weight is alway >= 0
        if weight == None or layout == "layered layout":
            weight = 1
        source = e.get_source()
        sink = e.get_destination()
        if source[0] == "n":
            source = source[1:]
            sink = sink[1:]

        edge = Edge(int(source), int(sink), int(weight), False, False)

        node_dict[edge.u].connections.append(edge.v)
        node_dict[edge.u].n = len(node_dict[edge.u].connections)
        node_dict[edge.v].connections.append(edge.u)
        node_dict[edge.v].n = len(node_dict[edge.v].connections)

        node_dict[edge.u].outgoing_edges.append(edge.v)
        node_dict[edge.v].incoming_edges.append(edge.u)

        edges.append(edge)

    #remove isolated nodes
    for node in list(node_dict.values()):
        if len(node.connections) == 0:
            node_dict.pop(node.idx)


    node_dict = dict(sorted(node_dict.items(), key=lambda item: item[1].n, reverse=True))
    graph_type:str = "directed" if is_directed else "normal"
    graph:Graph = Graph(node_dict, edges, [], graph_type)

    return graph, is_directed
