from dataStructures import Graph, Node, Edge
from math_helpers import min_int, max_int
from itertools import permutations
import numpy as np
import copy
import statistics as stat

def is_sink(node:Node) -> bool:
    return len(node.incoming_edges)!= 0 and len(node.outgoing_edges) == 0

def is_source(node:Node) -> bool:
    return len(node.outgoing_edges)!= 0 and len(node.incoming_edges) == 0

def is_isolated(node:Node) -> bool:
    return len(node.outgoing_edges)== 0 and len(node.incoming_edges) == 0

def find_sinks(graph:Graph):
    sinks = []
    for n in list(graph.values()):
        if is_sink(n):
            sinks.append(n)
    return sinks

def find_sources(graph:Graph):
    sources = []
    for n in list(graph.values()):
        if is_source(n):
            sources.append(n)
    return sources

def remove_sink(node, graph):
    # remove node from outgoing edges other nodes
    for v in node.incoming_edges:
        graph[v].outgoing_edges.remove(node.idx)
    # remove node from graph
    graph.pop(node.idx)
    return graph

def remove_source(node, graph):
    # remove node from outgoing edges other nodes
    for v in node.outgoing_edges:
        graph[v].incoming_edges.remove(node.idx)

    # remove node from graph
    graph.pop(node.idx)
    return graph

############################### Step 1 ###############################
def DAG(graph:Graph):
    dummy_graph:dict[int, Node] = copy.deepcopy(graph.nodes)

    TO_BE_FLIPPED = []
    while(len(dummy_graph) != 0):

        # Remove sinks
        sink_exists:bool = True
        while(sink_exists):

            ## find all sinks
            sinks = find_sinks(dummy_graph)
            if len(sinks) > 0:

                ## remove sinks from graph
                for s in sinks:
                    dummy_graph = remove_sink(s, dummy_graph)
            else:
                sink_exists = False

        # find isolated values
        for v in list(dummy_graph.values()):
            if is_isolated(v):
                dummy_graph.pop(v.idx)

        # Remove sources
        source_exists: bool = True
        while (source_exists):

            ## find all sinks
            sources = find_sources(dummy_graph)
            if len(sources) > 0:

                ## remove sinks from graph
                for s in sources:
                    dummy_graph = remove_source(s, dummy_graph)
            else:
                source_exists = False

        #remove node with where outgoing_edges - incoming edges is the highest value
        if(len(dummy_graph) != 0):

            # maximum difference between number of outgoing and incoming edges
            max_delta:int = min_int

            # index of node with max_out
            max_delta_idx:int = 0
            for n in list(dummy_graph.values()):

                ## calculate difference between outgoing and incoming edges
                delta = len(n.outgoing_edges) - len(n.incoming_edges)
                if delta > max_delta:
                    max_delta = delta
                    max_delta_idx = n.idx

            ## found max difference, found node to remove
            ## remove outgoing edges
            for n in dummy_graph[max_delta_idx].outgoing_edges:
                # remove edges
                dummy_graph[n].incoming_edges.remove(max_delta_idx)

            ## remove incoming edges
            for n in dummy_graph[max_delta_idx].incoming_edges:

                # flip edge
                TO_BE_FLIPPED.append(Edge(n, max_delta_idx, 1 ,False, False))

                # remove edges
                dummy_graph[n].outgoing_edges.remove(max_delta_idx)

            # remove node
            dummy_graph.pop(max_delta_idx)
    #Reverse edges
    for e in TO_BE_FLIPPED:
        u:int = e.u
        v:int = e.v

        #update the incoming/outging edges lists of the Node
        graph.nodes[v].incoming_edges.remove(u)
        graph.nodes[v].outgoing_edges.append(u)
        graph.nodes[u].outgoing_edges.remove(v)
        graph.nodes[u].incoming_edges.append(v)

        #reverse the indices of the Edge
        index = graph.edges.index(Edge(u,v, 1 ,False, False))
        graph.edges[index] = Edge(v,u, 1, True, False)

############################### Step 2 ###############################
def LayerAssignment(graph: Graph):
    ''' Input is a directed graph G'''
    i = 0
    dummy_graph = copy.deepcopy(graph)
    # get sources
    S = Sources(dummy_graph)
    while len(S) > 0:
        ## assign all sources to layer
        graph.layers.append(S)
        for n in S:
            graph.nodes[n].layer = i
        i += 1
        ## remove sources from the graph (and corresponding edges)
        for n in S:
            remove_source(dummy_graph.nodes[n], dummy_graph.nodes)

        ## find new sources of G
        S = Sources(dummy_graph)

    return addLayerCrossings(graph)

def Sources(graph):
    ''' Get a list of all sources in a graph'''
    list = []
    for i in graph.nodes:
        if is_source(graph.nodes[i]) or is_isolated(graph.nodes[i]):
            list.append(i)
    return list

def addLayerCrossings(graph):
    for e in graph.edges:
        ## check if we need to add dummy nodes
        delta = abs(graph.nodes[e.u].layer - graph.nodes[e.v].layer)
        if delta > 1:
            ## find the lower edge
            if graph.nodes[e.u].layer < graph.nodes[e.v].layer:
                lower_node = graph.nodes[e.u]
                upper_node = graph.nodes[e.v]
            else:
                lower_node = graph.nodes[e.v]
                upper_node = graph.nodes[e.u]

            ## remove edge between v and u
            graph.nodes[e.u].outgoing_edges.remove(e.v)
            graph.nodes[e.v].incoming_edges.remove(e.u)

            graph.edges.remove(e)

            ## add dummy nodes
            temp = lower_node
            node_dict = graph.nodes
            for i in range(1,delta):

                ## create dummy node
                node_idx: int = len(node_dict) + 1
                pos: np.array = np.array([0, 0])
                displacement_vector = np.array([0, 0])
                layer = lower_node.layer + i
                incoming_edges = [temp.idx]
                temp.outgoing_edges.append(node_idx)
                node: Node = Node(node_idx, pos, 0, [], False, [], 0, 0, 0, layer, displacement_vector, incoming_edges, [], True, "")

                # add dummy to the layer
                graph.layers[layer].append(node_idx)

                # add edge to dummy
                graph.edges.append(Edge(temp.idx, node_idx, 1, False, True))
                node_dict[node.idx] = node
                temp = node

            ## connect last dummy node to the upper node
            temp.outgoing_edges.append(upper_node.idx)
            upper_node.incoming_edges.append(temp.idx)
            graph.edges.append(Edge(temp.idx, upper_node.idx, 1, False, True))
    return graph

############################### Step 3 ###############################

def BarycenterHeuristic(graph:Graph, u:Node, starting_layer:str, n:int):
    x_sum = 0
    constant = 0.8
    if starting_layer == "top":
        for i in u.incoming_edges:
            v = graph.nodes[i]
            if u.layer - v.layer == 1:
                x_sum += v.pos[0]
        #print("node: ", u.idx," x_sum: ", x_sum, " length of incoming edges: ", len(u.incoming_edges))
        u.pos[0] = (x_sum/len(u.incoming_edges) + n*50)*constant

    if starting_layer == "bottom":
        for i in u.outgoing_edges:
            v = graph.nodes[i]
            if u.layer - v.layer == -1:
                x_sum += v.pos[0]
        #print("node: ", u.idx, "x_sum: ", x_sum, " length of outgoing edges: ", len(u.outgoing_edges))
        if len(u.outgoing_edges) != 0:
            u.pos[0] = (x_sum/len(u.outgoing_edges) + n*20)*constant

def MedianHeuristic(graph:Graph, u:Node, starting_layer:str, n:int):
    x_list = []
    constant = 0.8
    if starting_layer == "top":
        for i in u.incoming_edges:
            v = graph.nodes[i]
            if u.layer - v.layer == 1:
                x_list.append(v.pos[0])
    if starting_layer == "bottom":
        for i in u.outgoing_edges:
            v = graph.nodes[i]
            if u.layer - v.layer == -1:
                x_list.append(v.pos[0])
    if len(x_list) != 0:
        u.pos[0] = (stat.median(x_list) + n*50)*constant

def GenerateNodeInitialPositions(graph:Graph):
    for n in graph.nodes:
        node = graph.nodes[n]
        node.pos[1] = 100 + node.layer*50
    
    for n in graph.layers[0]:
        node = graph.nodes[n]
        node.pos[0] = 0 + graph.layers[0].index(n)*50

def GetPermutations(data:list):
    result = []
    for i in permutations(data):
        result.append(list(i))
    return result

def CountCrossings(graph:Graph):
    crossings = 0
    # Compare 2 edges with u belonging to layer n and v belonging to layer n+1
    for edge1 in graph.edges:
        for edge2 in graph.edges[graph.edges.index(edge1)+1:]:
            if graph.nodes[edge1.u].layer + 1 == graph.nodes[edge1.v].layer and graph.nodes[edge2.u].layer + 1 == graph.nodes[edge2.v].layer:
                if graph.nodes[edge1.u].layer == graph.nodes[edge2.u].layer and graph.nodes[edge1.u].idx != graph.nodes[edge2.u].idx:
                    # Hopefully this is exhaustive enough
                    if graph.nodes[edge1.u].pos[0] < graph.nodes[edge2.u].pos[0] and graph.nodes[edge1.v].pos[0] > graph.nodes[edge2.v].pos[0]:
                        crossings += 1
                        #print('edge1: ', edge1.u,'-', edge1.v, ' // edge2: ', edge2.u,'-', edge2.v)
                    elif graph.nodes[edge1.u].pos[0] > graph.nodes[edge2.u].pos[0] and graph.nodes[edge1.v].pos[0] < graph.nodes[edge2.v].pos[0]:
                        crossings += 1
                        #print('edge1: ', edge1.u,'-', edge1.v, ' // edge2: ', edge2.u,'-', edge2.v)
    return crossings

def IterativeCrossingMinimization(graph:Graph, BaryOrMedian:str, number_of_iteration:int, number_of_permutations:int):
    # Step 1 Select a permutation to work with
    permutation_list = GetPermutations(graph.layers[0])
    current_minimum_crossings = 0
    count = 0
    saved_nodes = []
    for i in range(len(permutation_list)):
        # check count to see how many permutation the function has to go through
        if count < number_of_permutations:
            graph.layers[0] = permutation_list[i]
            GenerateNodeInitialPositions(graph)
            for _ in range(number_of_iteration):
                # Step 2 Minimize crossings from top to bottom
                for layer in graph.layers[1:]:
                    for n in layer:
                        u = graph.nodes[n]
                        if BaryOrMedian == 'Bary':
                            BarycenterHeuristic(graph, u, 'top', layer.index(n))
                        if BaryOrMedian == 'Median':
                            MedianHeuristic(graph, u, 'top', layer.index(n))

                # Step 3 Minimize crossings from bottom to top
                for layer in reversed(graph.layers[:-1]):
                    for n in layer:
                        u = graph.nodes[n]
                        if BaryOrMedian == 'Bary':
                            BarycenterHeuristic(graph, u, 'bottom', layer.index(n))
                        if BaryOrMedian == 'Median':
                            MedianHeuristic(graph, u, 'bottom', layer.index(n))
            
            # check the best the permuation by comparing to the previous result
            if count == 0:
                current_minimum_crossings = CountCrossings(graph)
                saved_nodes = copy.deepcopy(graph.nodes)
            elif count > 1:
                if current_minimum_crossings < CountCrossings(graph):
                    graph.nodes = saved_nodes
                else:
                    current_minimum_crossings = CountCrossings(graph)
                    saved_nodes = copy.deepcopy(graph.nodes)

            count +=1
            # print('perm ', i)
            # print('count ', count)
            # print('Number of current crossings:', current_minimum_crossings)

############################### Step 4 ###############################

def add_dummy_nodes(graph:Graph, current_node:Node, path) -> tuple[list[Node], Node]:

    ## add dummy node
    path.append(current_node)
    next_node = graph.nodes[current_node.outgoing_edges[0]]

    ## as long as the next node is also a dummy node, we keep adding it
    if next_node.dummy_node:
        path, last_node = add_dummy_nodes(graph, graph.nodes[current_node.outgoing_edges[0]],path)
    return path, next_node
        
def create_paths(graph:Graph, starting_node:Node, all_paths:list[list[Node]]):
    for child in starting_node.outgoing_edges:
        child_node:Node = graph.nodes[child]
        if child_node.dummy_node:
            path, ending_node = add_dummy_nodes(graph, child_node, [])
            all_paths.append(path)
            create_paths(graph, ending_node, all_paths)
        else:
            create_paths(graph, child_node, all_paths)

def get_position_score(graph:Graph, first_layer:list[Node]) -> float:
    #Create list with all paths
    all_paths:list[list[Node]] = []
    for node in first_layer:
        create_paths(graph, node, all_paths)

    #compute the score
    total_score:float = 0
    for path in all_paths:
        #get the starting node and ending node of this path (assuming dummy nodes have only 1 incoming/outgoing edge)
        starting_node:Node = graph.nodes[path[0].incoming_edges[0]]
        ending_node:Node = graph.nodes[path[-1].outgoing_edges[0]]
        k = path[-1].layer

        g:float = 0
        for dummy_node in path:
            a = starting_node.pos[0] + (dummy_node.layer / (k+1)) * (ending_node.pos[0] - starting_node.pos[0])
            g += (dummy_node.pos[0] - a)**2

        total_score += g

    return total_score

#Set position based on 01101001 string, layer = list of all the nodes in layer, permutation = bit string
def set_positions_to_bit_string(graph:Graph, layer: list[Node], permutation, x_offset:float):
    current_node = 0
    x_pos = 0
    #set all positions according to the permutation
    for position in permutation:         
        if position == '1':
            idx = layer[current_node].idx
            graph.nodes[idx].pos[0] = x_pos * x_offset
            layer[current_node].pos[0] = x_pos * x_offset
            current_node += 1

        x_pos += 1

def set_node_positions(graph:Graph):
    y_offset:float = -40.0
    x_offset:float = 20.0

    #sort nodes by layer index
    sorted_nodes: dict[int, Node] = dict(sorted(graph.nodes.items(), key=lambda item: item[1].layer, reverse=False))

    #list that holds a list with the nodes of each layer, so like [[n_0, n_0], ...,  [n_i, n_i, n_i]]
    layers:list[list[Node]] = []

    current_layer = -1
    highest_breadth = 0 # number of nodes of the layer with the most nodes (not used atm?? might be deleted)

    #add nodes for each layers in the separate lists
    for node in sorted_nodes.values():
        if(node.layer > current_layer):
            current_layer += 1
            layers.append([])
        layers[current_layer].append(node)
        highest_breadth = len(layers[current_layer]) if len(layers[current_layer]) > highest_breadth else highest_breadth

    
    #sort nodes within layers based on x position and set the node's position
    y:int = 0
    i:int = 0
    for layer in layers:
        sorted_layer = sorted(layer, key=lambda item: item.pos[0])

        x:int = 0
        for node in sorted_layer:
            node.pos = [x, y]
            x += x_offset

        layers[i] = sorted_layer

        y += y_offset
        i += 1

    for iterations in range(3):            
        for layer in layers:
            node_count = len(layer)
            initial_layout:str = '1' * node_count + '0' * (highest_breadth - node_count)
            all_permutations = set(permutations(initial_layout, highest_breadth))

            best_score = max_int
            best_permutation_idx = 0
            current_permutation_idx = 0
            #for each possible permutation
            for permutation in all_permutations:

                set_positions_to_bit_string(graph, layer, permutation, x_offset)


                score:float = get_position_score(graph, layers[0])
                if(score < best_score):
                    best_score = score
                    best_permutation_idx = current_permutation_idx

                current_permutation_idx += 1


            #set positions according to permutation with the highest score TODO turn this into a function
            best_permutation = list(all_permutations)[best_permutation_idx]
            set_positions_to_bit_string(graph, layer, best_permutation, x_offset)
        

######FLIP EDGES BACK###########
def flip_edges_back(graph:Graph):
    #Reverse edges
    for e in graph.edges:
        if e.is_dummy:
            u:int = e.u
            v:int = e.v

            #update the incoming/outging edges lists of the Node
            graph.nodes[v].incoming_edges.remove(u)
            graph.nodes[v].outgoing_edges.append(u)
            graph.nodes[u].outgoing_edges.remove(v)
            graph.nodes[u].incoming_edges.append(v)

            #reverse the indices of the Edge
            index = graph.edges.index(e)
            graph.edges[index] = Edge(v,u, 1, False, False)
        







    
    