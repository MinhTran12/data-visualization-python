from tkinter import *
from screenSettings import *
from dataStructures import Graph, Node, Edge, InterEdge
from Similarity_matrix import matrix_floyd_warshall, dimensionality_reduction
from qualMetrics import stress, trustworthiness, continuity, crossingCalculation
from math_helpers import unit_vector

import forceDirectedLayout
import treeConstructor
import radial
import dataReader
import random
import math
import time
import pydot
import edgeBundler
import directedGraph

draw_offset:float = 10.0
node_colors:list[str] = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
subgraph_colors:dict[str, str] = {"Youngest Devonian Strata": '#e6194b', "Gap in the Sequence of Devonshi":'#3cb44b'}
is_directed:bool = False

def draw_nodes(graph:Graph, myCanvas:Canvas, network_type:str, tree_extra_edges:bool=False, draw_numbers:bool=False):
    radius:float = 7.0 #radius of node
    for n in graph.nodes:
        node:Node = graph.nodes[n]
        if not node.dummy_node:
            node_color = '#e6194b'
            if(node.dummy_node):
                node_color = "#ffffff"
            myCanvas.create_oval(node.pos[0]-radius, node.pos[1]-radius, node.pos[0]+radius, node.pos[1]+radius, fill=node_color)
            if(draw_numbers):
                myCanvas.create_text(node.pos[0], node.pos[1], font=('Arial', 7),text=n)
            if not tree_extra_edges and network_type == 'tree':
                for c in node.tree_edges:
                    line = myCanvas.create_line(node.pos[0], node.pos[1], graph.nodes[c].pos[0], graph.nodes[c].pos[1],fill="gray", width=1)
                    myCanvas.tag_lower(line)

def draw_edges(paths, myCanvas:Canvas):
    radius:float = 7.0
    for p in paths:
        line = np.concatenate(p).ravel().tolist()
        line_length = len(line)
        last_end:np.array = np.array([line[line_length-2], line[line_length-1]])
        last_start:np.array = np.array([line[line_length-4], line[line_length-3]])
        dir = unit_vector(last_end- last_start)
        line[line_length-2] = line[line_length-2] - dir[0] * radius
        line[line_length-1] = line[line_length-1] - dir[1] * radius

        #myCanvas.create_line(node1.pos[0]+dir[0]*radius, node1.pos[1]+dir[1]*radius, node2.pos[0]-dir[0]*radius, node2.pos[1]-dir[1]*radius,fill="gray",arrow='last', width=1)


        myCanvas.create_line(line, smooth=1, fill="gray")
    return

def draw_bounding_boxes(bounding_boxes:[], myCanvas:Canvas):
    colors = ['#bae1ff', '#ffb3ba', '#baffc9', '#ffdfba','#bae1ff', '#ffb3ba', '#baffc9', '#ffdfba','#bae1ff', '#ffb3ba', '#baffc9', '#ffdfba','#bae1ff', '#ffb3ba', '#baffc9', '#ffdfba']
    counter = 0
    for box in bounding_boxes:
        x1 = bounding_boxes[box]["min_x"]
        x2 = bounding_boxes[box]["max_x"]
        y1 = bounding_boxes[box]["min_y"]
        y2 = bounding_boxes[box]["max_y"]
        myCanvas.create_rectangle(x1,y1,x2,y2, fill=colors[counter], outline=colors[counter])
        counter += 1

def draw_multilevel_graph(nodes:dict[int, Node], intra_edges:list[Edge], inter_edges:dict[str,list[InterEdge]], myCanvas:Canvas):
    radius:float = 7.0
    for edge in intra_edges:
        node1:Node = nodes[edge.u]
        node2:Node = nodes[edge.v]
        myCanvas.create_line(node1.pos[0], node1.pos[1], node2.pos[0], node2.pos[1], fill="gray", width=1)

    for layer in inter_edges:
        for edge in inter_edges[layer]:
            for i in range(-1, len(edge.division_points)):
                if i == -1:
                    p1 = edge.starting_point
                else:
                    p1 = edge.division_points[i]
                if i == len(edge.division_points) -1:
                    p2 = edge.ending_point
                else:
                    p2 = edge.division_points[i + 1]
                myCanvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="blue", width=1)

    for node in nodes.values():
        myCanvas.create_oval(node.pos[0]-radius, node.pos[1]-radius, node.pos[0]+radius, node.pos[1]+radius, fill="red")

# Setting new positions based on number of connections <-- ASSUMES NODES SORTED BY CONNECTION COUNT
# perhaps this function can be in a seperate python file?
def set_node_positions_random(graph:Graph):
    for n in graph.nodes:
        node:Node = graph.nodes[n]
        node.pos[0] = random.uniform(0, screen_width)
        node.pos[1] = random.uniform(0, screen_height)

def set_node_positions_semirandom(graph:Graph):
    i:int = 1
    for n in graph.nodes:
        node:Node = graph.nodes[n]

        prev_offset = (i-1)/len(graph.nodes)
        offset = i/len(graph.nodes)

        node.pos[0] = random.uniform(screen_center[0] - ((screen_center[0] - draw_offset) * offset), screen_center[0] + ((screen_center[0] - draw_offset) * offset))
        if(node.pos[0] < screen_center[0] - ((screen_center[0] - draw_offset) * prev_offset) or node.pos[0] > screen_center[0] + ((screen_center[0] - draw_offset) * prev_offset)):
            r = random.randrange(0, 2)
            if(r == 0):
                node.pos[1] = random.uniform(screen_center[1] - ((screen_center[1] - draw_offset) * offset), screen_center[1] - ((screen_center[1] - draw_offset) * prev_offset))
            else:
                node.pos[1] = random.uniform(screen_center[1] + ((screen_center[1] - draw_offset) * prev_offset), screen_center[1] + ((screen_center[1] - draw_offset) * offset))

        else:
            node.pos[1] = random.uniform(screen_center[1] - ((screen_center[1] - draw_offset) * offset), screen_center[1] + ((screen_center[1] - draw_offset) * offset))

        i += 1

def set_node_position_in_circle(graph:Graph):
    radius = 150
    length = len(graph.nodes)
    counter = 0
    step = 2*math.pi/length
    for n in graph.nodes:
        node:Node = graph.nodes[n]
        node.pos[0] = radius * math.cos(step*counter) + 500
        node.pos[1] = radius * math.sin(step*counter) + 500
        counter += 1

def set_node_position_tree(graph:Graph, search_algorithm:str="DFS", starting_node:str="Most"):
    if search_algorithm == 'BFS':
        treeConstructor.BFS(graph, starting_node)
    if search_algorithm == "DFS":
        treeConstructor.DFS(graph, starting_node)
    radial.Create_Radial(graph, starting_node)

def set_starting_layout(graph:Graph, starting_layout:str, search_algorithm:str="DFS", starting_node:str="Most"):
    if starting_layout == "random":
        set_node_positions_random(graph)
    elif starting_layout == "semi random":
        set_node_positions_semirandom(graph)
    elif starting_layout == "circle":
        set_node_position_in_circle(graph)
    elif starting_layout == "tree":
        set_node_position_tree(graph, search_algorithm, starting_node)

def bezier_curves(graph: Graph, tree_edges):
    ## find paths from sources to sinks
    paths = []
    if not tree_edges:

        for source in graph.nodes:

            ## if the node is a dummy, it's not a source
            if not graph.nodes[source].dummy_node:

                # loop through their oudgoing edges and create paths
                for sink in graph.nodes[source].outgoing_edges:
                    path = []
                    path.append(graph.nodes[source].pos)
                    sink_not_found = True
                    while sink_not_found:

                        ## but only if there are dummies left
                        if graph.nodes[sink].dummy_node:
                            temp = sink
                            path.append(graph.nodes[temp].pos)
                            sink = graph.nodes[temp].outgoing_edges[0]
                            sink_not_found = graph.nodes[sink].dummy_node
                        else:
                            sink_not_found = False
                    ## lastly, add sink
                    path.append(graph.nodes[sink].pos)
                    paths.append(path)
    return paths

def move_back(graph:Graph):
    middle_x = graph.nodes[1].pos[0]
    middle_y = graph.nodes[1].pos[1]
    move_x = screen_width/2 - middle_x
    move_y = screen_height/2 - middle_y
    for n in graph.nodes:
        graph.nodes[n].pos[0] += move_x
        graph.nodes[n].pos[1] += move_y
    return graph

def boundingbox(graph:Graph):
    names:dict[str, dict[str,int]] = dict()
    a = []
    b = []
    for n in graph.nodes:
        node = graph.nodes[n]
        ## if the subgraph isn't in the list, add it to the list
        if node.subgraph not in names:
            names[node.subgraph] = {}
            names[node.subgraph]["min_x"] = node.pos[0]
            names[node.subgraph]["max_x"] = node.pos[0]
            names[node.subgraph]["min_y"] = node.pos[1]
            names[node.subgraph]["max_y"] = node.pos[1]

        ## else, check if the node would be in the bounding box, else increase the bounding box
        if names[node.subgraph]["min_x"] > node.pos[0]: names[node.subgraph]["min_x"] = node.pos[0]
        if names[node.subgraph]["max_x"] < node.pos[0]: names[node.subgraph]["max_x"] = node.pos[0]
        if names[node.subgraph]["min_y"] > node.pos[1]: names[node.subgraph]["min_y"] = node.pos[1]
        if names[node.subgraph]["max_y"] < node.pos[1]: names[node.subgraph]["max_y"] = node.pos[1]

    # make sure all bounding boxes don't overlap
    offset = 100
    subgraphs = names.keys()
    total_max_x = None
    total_max_y = None
    total_min_x = None
    total_min_y = None
    for cluster in subgraphs:
        if total_max_x == None:
            total_max_x = names[cluster]["max_x"]
            total_max_y = names[cluster]["max_y"]
            total_min_x = names[cluster]["min_x"]
            total_min_y = names[cluster]["min_y"]
        else:
            ## check if cluster overlaps with total set of subgraphs
            if names[cluster]["max_x"] > total_max_x:
                difference_x = total_max_x - names[cluster]["min_x"]
            else:
                difference_x = names[cluster]["max_x"] - total_min_x
            if names[cluster]["max_y"] > total_max_y:
                difference_y = total_max_y - names[cluster]["min_y"]
            else:
                difference_y = names[cluster]["max_y"] - total_min_y

            ## if they overlap, move the cluster
            if difference_y > -offset and difference_x > -offset:
                ## check which difference is the smallest, in that direction we'll move the subgraph
                if difference_y > difference_x:
                    difference = difference_y
                    coordinate = 1

                    ## change total area
                    names[cluster]["min_y"] += difference + offset
                    names[cluster]["max_y"] += difference + offset
                    if names[cluster]["min_y"] < total_min_y:
                        total_min_y = names[cluster]["min_y"]
                    else:
                        total_max_y = names[cluster]["max_y"]

                else:
                    difference = difference_x
                    coordinate = 0

                    # change total area
                    names[cluster]["min_x"] += difference + offset
                    names[cluster]["max_x"] += difference + offset
                    if names[cluster]["min_x"] < total_min_y:
                        total_min_y = names[cluster]["min_x"]
                    else:
                        total_max_y = names[cluster]["max_x"]

                for n in graph.nodes:
                    node = graph.nodes[n]
                    if node.subgraph == cluster:
                        node.pos[coordinate] = node.pos[coordinate] + difference + offset
    return names

# draw the graph
def draw_graph(myCanvas, dot_file_name:str, network_type:str, search_algorithm:str, starting_node:int, starting_layout:str, inertia:bool, gravitation:bool, angle:bool, scale:bool, position:bool, visibility:bool, tree_extra_edges:bool, get_random_node:bool, draw_numbers:bool, force_directed_algo:str, dr:str):
    global is_directed 
    graph, is_directed = dataReader.ReadFromDOT("data/" + dot_file_name, network_type)
    start = time.time()  

    if get_random_node == True:
        starting_node = random.randint(1, len(graph.nodes))

    # check graph type -> generate coordinates and edges accordingly -> draw nodes then edges
    if network_type == "tree":
        set_node_position_tree(graph, search_algorithm, starting_node)

    if network_type == "random":
        set_starting_layout(graph, starting_layout, search_algorithm, starting_node)

    if network_type == "force directed":
        if force_directed_algo == "Eades":
            set_starting_layout(graph, starting_layout, search_algorithm, starting_node)

            max_it:int = 500
            delta = 1
            epsilon:float = 1
            for i in range(1,max_it):
                i = i/100
                if(forceDirectedLayout.set_new_positions(graph, delta, inertia, gravitation) < epsilon): break
                delta = 5/i
        if force_directed_algo == "Reingold":
            set_starting_layout(graph, starting_layout, search_algorithm, starting_node)

            max_it:int = 500
            delta = 1
            epsilon:float = 500
            for i in range(1,max_it):
                if(forceDirectedLayout.set_new_positions_reingold(graph, delta,inertia, gravitation, grid_bool=False) < epsilon): break
                delta = 1000/i
        if force_directed_algo == "Reingold - Grid":
            set_starting_layout(graph, starting_layout, search_algorithm, starting_node)
            # grid version seems to work with low amount of iteration (20 to 40 seems to be decent)
            # and also high epsilon when checking for maximum force (1000 to 1500)
            max_it:int = 30
            delta = 1
            epsilon:float = 1500
            for i in range(1,max_it):
                if(forceDirectedLayout.set_new_positions_reingold(graph, delta,inertia, gravitation, grid_bool=True) < epsilon): break
                delta = 1000/i
        move_back(graph)

    if network_type == "layered layout":
        directedGraph.DAG(graph)
        directedGraph.LayerAssignment(graph)
        directedGraph.IterativeCrossingMinimization(graph, "Bary", 20, 10)
        graph = move_back(graph)
        directedGraph.set_node_positions(graph)
        directedGraph.flip_edges_back(graph)

    if network_type == "multilayer layout":
        set_starting_layout(graph, starting_layout, search_algorithm, starting_node)

        max_it:int = 100
        delta = 1
        epsilon:float = 500
        # for i in range(1,max_it):
        #     if(forceDirectedLayout.set_new_positions_reingold(graph, delta,inertia, gravitation, grid_bool=False) < epsilon): break
        #     delta = 1000/i
        bounding_boxes = boundingbox(graph)
        draw_bounding_boxes(bounding_boxes, myCanvas)
        intra_edges, inter_edges = edgeBundler.bundle_edges(graph, angle, scale, position, visibility)
        draw_multilevel_graph(graph.nodes, intra_edges, inter_edges, myCanvas)

        #graph = move_back(graph)

    if network_type == "projection":

        similarity_matrix = matrix_floyd_warshall(graph)
        #similarity_matrix = matrix_dijkstra(graph)
        graph = dimensionality_reduction(similarity_matrix, graph, dr)

    if network_type != "multilayer layout":
        # get paths via dummy nodes
        paths = bezier_curves(graph, tree_extra_edges)
        # draw edges and nodes
        draw_edges(paths, myCanvas)
        draw_nodes(graph, myCanvas, network_type, draw_numbers=draw_numbers)

    end = time.time()
    length = end - start
    print("**********************************")
    print("The runtime is:", length, " seconds.")

    number_of_crossings, mean_resolution, median_resolution, smallest_resolution = crossingCalculation(graph)
    print("Number of edge crossings: ", number_of_crossings)
    print("Mean crossing resolution: ", mean_resolution)
    print("Median crossing resolution: ", median_resolution)
    print("Smallest crossing resolution: ", smallest_resolution)

    trust = trustworthiness(graph, 3)
    print("Trustworthiness score is:", trust)
    cont = continuity(graph, 3)
    print("Continuity score is:", cont)

    stress(graph, dot_file_name, dr)
