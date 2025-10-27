from dataStructures import Graph, Edge, InterEdge
from math_helpers import unit_vector, magnitude
import numpy as np
from copy import deepcopy

stiffness:float = 0.2 #stiffness constant (K)


def get_inter_edges(graph:Graph) -> tuple[dict[str, list[Edge]], list[Edge]]:
    ''' Get a list of all edges connecting two subgraphs '''
    inter_edges:dict[str, list[Edge]] = dict()        ## edges between layers
    intra_edges:list[Edge] = []                   ## edges in one layer

    for edge in graph.edges:
        node1 = graph.nodes[edge.u]
        node2 = graph.nodes[edge.v]

        # check if we're dealing with an inter layer edge
        if node1.subgraph != node2.subgraph:
            key = [node1.subgraph, node2.subgraph]
            key.sort()
            key = ' '.join(key)

            # check if key is already in inter_edges
            if key in inter_edges:
                inter_edges[key].append(edge)
            else:
                inter_edges[key] = [edge]

        # when not dealing with an inter_layer edge
        else:
            intra_edges.append(edge)

    return inter_edges, intra_edges

def subdivide(subdivided_edges:list[InterEdge]):
    ''' Compute coordinates of new subdivision of points '''

    for edge in subdivided_edges:
        subdivision_count = edge.subdivision_count + 1  #number of new points
        old_division_points:list[np.array] = deepcopy(edge.division_points)
        for i in range(0, subdivision_count):
            if(i == 0):
                p1 = edge.starting_point
            else: p1 = old_division_points[i-1]
            if(i == subdivision_count -1):
                p2 = edge.ending_point
            else: p2 = old_division_points[i]
            edge.division_points.insert(i*2, (p1+p2)/2.0) #insert new point halway between two points that already exist
            edge.forces.append(np.array([0.0,0.0]))
        #edge.stiffness /= 2.0 #edges are now half the size, so divide by 2 <-- I think this is incorrect bc the length of the edges changes when points are moving.....
        edge.subdivision_count = len(edge.division_points)

def initial_inter_edge_subdivision(graph:Graph, inter_edges:list[Edge], n:int = 1):
    ''' Subdivide edge, each inter edge now consists of a list of dataclass InterEdge'''
    subdivided_edges:list[InterEdge] = []

    for i, edge in enumerate(inter_edges):
        P1:np.array = graph.nodes[edge.u].pos
        P2:np.array = graph.nodes[edge.v].pos

        direction = unit_vector(P2 - P1)
        length = magnitude(P2-P1)
        segment_length = length / (n + 1) #n+1, because the number of line segments = number of points +1
        k = stiffness/segment_length

        subdivided_edge:InterEdge = InterEdge(i, [], [], P1, P2, n, length, k)
        for i in range(1, n+1):
            subdivided_edge.division_points.append(P1+(direction*(segment_length * i)))
            subdivided_edge.forces.append(np.array([0,0]))

        subdivided_edges.append(subdivided_edge)
    
    return subdivided_edges

def compute_spring_force(P:InterEdge, i:int) -> np.array:
    ''' Create the spring force on a node'''

    ## get previous node. If node is first node, then get starting point
    if i == 0:
        p_prev = P.starting_point
    else:
        p_prev = P.division_points[i-1]

    ## get current node
    p_curr = P.division_points[i]

    ## get next node. If node is last node, then get the end point
    if i == P.subdivision_count-1:
        p_nxt = P.ending_point
    else:
        p_nxt = P.division_points[i+1]

    ## calculate spring force
    # spring_force: np.array = P.stiffness * (magnitude(p_prev - p_curr) + magnitude(p_nxt - p_curr)) * ((p_prev - p_curr)/magnitude(p_prev - p_curr) + (p_nxt - p_curr)/magnitude(p_nxt - p_curr))
    spring_force: np.array = P.stiffness * ((p_prev - p_curr) + (p_nxt - p_curr))

    return spring_force

#TODO: figure out how vis_compatibility works with non-parallel edges
def visibility_compatibility(edge1:InterEdge, edge2:InterEdge):
    direction_vector1 = edge1.ending_point - edge1.starting_point
    direction_vector2 = edge2.ending_point - edge2.starting_point
    return

def visibility_helper():
    return

def angle_compatibility(edge1:InterEdge, edge2:InterEdge):
    direction_vector1 = edge1.ending_point - edge1.starting_point
    direction_vector2 = edge2.ending_point - edge2.starting_point
    c_angle = np.dot(direction_vector1, direction_vector2) / (magnitude(direction_vector1)*magnitude(direction_vector2))
    return abs(c_angle)

# TODO: returned c_scale is really small 
def scale_compatibility(edge1:InterEdge, edge2:InterEdge):
    direction_vector1 = edge1.ending_point - edge1.starting_point
    direction_vector2 = edge2.ending_point - edge2.starting_point
    magnitude_vector1 = magnitude(direction_vector1)
    magnitude_vector2 = magnitude(direction_vector2)
    average_length = (magnitude_vector1 + magnitude_vector2)/2
    c_scale = 2/(average_length/min(magnitude_vector1, magnitude_vector2) + max(magnitude_vector1, magnitude_vector2)/average_length)
    return c_scale

def position_compatibility(edge1:InterEdge, edge2:InterEdge):
    direction_vector1 = edge1.ending_point - edge1.starting_point
    direction_vector2 = edge2.ending_point - edge2.starting_point
    magnitude_vector1 = magnitude(direction_vector1)
    magnitude_vector2 = magnitude(direction_vector2)
    average_length = (magnitude_vector1 + magnitude_vector2)/2
    midpoint1 = (edge1.ending_point + edge1.starting_point)/2
    midpoint2 = (edge2.ending_point + edge2.starting_point)/2
    c_position = average_length/(average_length + magnitude(midpoint1 - midpoint2))
    return c_position

def total_compatibility(angle, scale, position, visibility, edge1, edge2):
    # calculate compatibilities
    compatibility = 1
    if angle:
        compatibility *= angle_compatibility(edge1, edge2)
    # scale is not working
    if scale:
        compatibility *= scale_compatibility(edge1, edge2)
    if position:
        compatibility *= position_compatibility(edge1, edge2)
    if visibility:
        compatibility *= 1  # visibility_compatibility(edge1, edge2)
    return compatibility


def bundle_edges(graph:Graph, angle:bool, scale:bool, position:bool, visibility:bool):
    inter_edges, intra_edges = get_inter_edges(graph)
    subdivided_edges = dict()
    
    #I did not use the recommended values from the paper, but tweaked it a bit to get good results for our graph
    step_size: float = 0.05 #step size each point on a subdivided will move in the force direction
    number_of_cycles:int = 5 #One cycle consists of cycle_length iterations
    current_cycle:int = 0 #index of curernt cycle
    cycle_length:float = 50 #number of iterations within one cycle
    iteration:int = 1 #index of current iteration

    for layer in inter_edges:
        edges = inter_edges[layer]
        subdivided_edges[layer] = initial_inter_edge_subdivision(graph, edges)

        while current_cycle < number_of_cycles:
            #calculate forces
            for edge1 in subdivided_edges[layer]:
                for i in range(edge1.subdivision_count):
                    edge1.forces[i] = np.array([0.0,0.0])

                    # add spring force
                    total_force:np.array = compute_spring_force(edge1, i)

                    # for all other edges, we add electrostatic force based on compatibilities
                    for edge2 in subdivided_edges[layer]:
                        if edge2 != edge1:
                            compatibility = total_compatibility(angle, scale, position, visibility, edge1, edge2)
                            total_force += compatibility/magnitude(edge1.division_points[i] - edge2.division_points[i])*(edge2.division_points[i] - edge1.division_points[i])
                            # Finetunning the electrostatic force to immediate neiboring points
                            if i+1 < edge1.subdivision_count:
                                total_force += compatibility/magnitude(edge1.division_points[i] - edge2.division_points[i+1])*(edge2.division_points[i+1] - edge1.division_points[i])
                            if i-1 >= 0:
                                total_force += compatibility/magnitude(edge1.division_points[i] - edge2.division_points[i-1])*(edge2.division_points[i-1] - edge1.division_points[i])
                    edge1.forces[i] += total_force * step_size
                    # applying force immediately
                    #edge1.division_points[i] += edge1.forces[i]
            # apply forces
            for edge in subdivided_edges[layer]:
                for i in range(edge1.subdivision_count):
                    edge.division_points[i] += edge.forces[i]
            iteration+=1

            #each cycle, some variable values change and the edge gets subdivided
            if iteration >= cycle_length:
                subdivide(subdivided_edges[layer])
                step_size*=0.5
                iteration = 1
                current_cycle+= 1
                cycle_length*= 2.0/3.0
    return intra_edges, subdivided_edges