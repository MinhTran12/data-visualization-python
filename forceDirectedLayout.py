from dataStructures import Graph, Node
from math_helpers import magnitude, unit_vector
import numpy as np
import math

c_spring:float = 2.0 #spring constant (attraction)
c_rep:float = 1.0 #repulsion constant
l:float = 100.0 #ideal edge length
c_grav:float = 10.0 #gravitation

c_reingold:float = 0.5 # reingold constant C for ideal edge length

def get_repulsive_force(p1:np.array, p2:np.array) -> np.array:
    distance:float = magnitude(p2 - p1)
    direction:np.array = unit_vector(p1 - p2)
    return np.array((c_rep / (distance**2)) * direction)

#here c_spring * np.log(distance / l) will be negative when repulsing and positive when attracting an adjacent node
# rename get_attractive_force to get_spring_force to refelct F_spring and not F_attr
def get_spring_force(p1:np.array, p2:np.array) -> np.array:
    distance:float = magnitude(p1 - p2)
    direction:np.array = unit_vector(p2 - p1)
    return np.array(c_spring * np.log(distance / l) * direction)

def inertia(node):
    return 1/(1 + len(node.connections)/2)

def gravitation(node: Node,p_bary):
    return c_grav*len(node.connections)*unit_vector(p_bary - node.pos)

def barycenter(graph: Graph):
    sum_of_nodes = np.array([0, 0])
    for n in graph.nodes:
        sum_of_nodes = sum_of_nodes + graph.nodes[n].pos
    return (1 / len(graph.nodes)) * sum_of_nodes

def get_magnetic_force(node_1:Node, node_2:Node):
    # parameters for tuning the model
    c_m = 1000
    b = 1
    alpha = 1
    beta = 1

    # non parameters
    edge = node_2.pos - node_1.pos
    field = np.array([0,1])
    distance = magnitude(node_2.pos - node_1.pos)
    theta = math.acos(np.dot(edge, field)/distance)
    return c_m*b*(distance**alpha)*(theta**beta)



#noname.dot --> epsilon: 1.5, max_it: 300, c_spring: 200, c_rep: 1000, l: 100
#setting new node positions based on the spring and repulsive force, returns the maximum force
def set_new_positions(graph:Graph, delta:float, inertia_bool:bool, gravitation_bool:bool) -> float:
    max_force:float = 0.0
    for n in graph.nodes:
        node:Node = graph.nodes[n]
        adjacent_nodes:set = set(node.connections)
        non_adjacent_nodes:set = set(range(1, len(graph.nodes) + 1))
        non_adjacent_nodes.discard(n)
        non_adjacent_nodes -= adjacent_nodes

        total_repulsive_force:np.array = np.array([0, 0])
        total_attractive_force:np.array = np.array([0, 0])

        #compute the repulsive force based on all non adjacent noces
        for i in non_adjacent_nodes:
            na_node:Node = graph.nodes[i]
            total_repulsive_force = total_repulsive_force + get_repulsive_force(node.pos, na_node.pos)

        #compute the attractive force based on all adjacent nodes
        for j in adjacent_nodes:
            a_node:Node = graph.nodes[j]
            inertia_node = 1
            if inertia_bool:
                inertia_node = inertia(node)
            total_attractive_force = total_attractive_force + inertia_node*get_spring_force(node.pos, a_node.pos)
        
        #compute gravitation force
        #grav = gravitation(node, p_bary)

        displacement:np.array = total_repulsive_force + total_attractive_force #+ grav

        if(magnitude(displacement) > max_force): max_force = magnitude(displacement)

        node.pos = node.pos + (delta * displacement)
    #print("Max force:", max_force)
    return max_force

def get_repulsive_force_reingold(p1:np.array, p2:np.array, l:float) -> np.array:
    distance:np.array = magnitude(p1 - p2)
    direction:np.array = unit_vector(p1 - p2)
    return np.array((l**2/distance) * direction)

def get_attractive_force_reingold(p1:np.array, p2:np.array, l:float) -> np.array:
    distance:np.array = magnitude(p1 - p2)
    direction:np.array = unit_vector(p1 - p2)
    return np.array((distance**2/l) * direction)

# function that get a dictionary of grids containing their associated nodes 
def initialize_grid(graph:Graph):
    grid_size = 2*c_reingold*np.sqrt(1000*750/len(graph.nodes))
    grid = {}
    for n in graph.nodes:
        node:Node = graph.nodes[n]
        #print(node.pos)
        grid_x = int(node.pos[0] / grid_size)
        grid_y = int(node.pos[1] / grid_size)
        
        if (grid_x, grid_y) not in grid:
            grid[(grid_x, grid_y)] = []
        grid[(grid_x, grid_y)].append(node)

    return grid

def set_new_positions_reingold(graph:Graph, delta:float, inertia_bool:bool, gravitation_bool:bool, grid_bool:bool) -> float:
    max_force:float = 0.0
    l_reingold = c_reingold*np.sqrt(1000*1000/len(graph.nodes))
    p_bary = barycenter(graph)
    grid_size = 2 * l_reingold

    # Grid version of the algorithm
    if grid_bool == True:
        grid = initialize_grid(graph)
        for n in graph.nodes:
            total_repulsive_force:np.array = np.array([0, 0])
            node:Node = graph.nodes[n]

            # Get neiboring nodes within its own grid or neighboring grid
            grid_x = int(node.pos[0]/(grid_size))
            grid_y = int(node.pos[1]/(grid_size))
            for i in range(max(0, grid_x - 1), min(int(1000 / grid_size), grid_x + 2)):
                    for j in range(max(0, grid_y - 1), min(int(750 / grid_size), grid_y + 2)):
                        if (i, j) in grid:
                            for neighbor_node in grid[(i, j)]:
                                if neighbor_node != node:
                                    # Check that the distance between the neighboring nodes are closed enough to be repulsed
                                    if magnitude(node.pos - neighbor_node.pos) <= grid_size:
                                        total_repulsive_force = total_repulsive_force + get_repulsive_force_reingold(node.pos, neighbor_node.pos, l_reingold)

            node.displacement_vector = total_repulsive_force
    # Standard version
    # Loop through the nodes to determine the repulsive force between all neighbors
    else:
        for n1 in graph.nodes:
            total_repulsive_force:np.array = np.array([0, 0])
            node_1:Node = graph.nodes[n1]

            for n2 in graph.nodes:  
                if n1 != n2:
                    node_2:Node = graph.nodes[n2]
                    total_repulsive_force = total_repulsive_force + get_repulsive_force_reingold(node_1.pos, node_2.pos, l_reingold)
            node_1.displacement_vector = total_repulsive_force

    # Loop through the edges to determine the attraction force between all neighbors
    for e in graph.edges:
        node_1:Node = graph.nodes[e.u]
        node_2:Node = graph.nodes[e.v]
        f_mag = get_magnetic_force(node_1, node_2)
        inertia_node_1 = 1
        inertia_node_2 = 1
        if inertia_bool:
            inertia_node_1 = inertia(node_1)
            inertia_node_2 = inertia(node_2)
        node_1.displacement_vector = node_1.displacement_vector - inertia_node_1 * get_attractive_force_reingold(node_1.pos, node_2.pos, l_reingold)
        node_2.displacement_vector = node_2.displacement_vector + inertia_node_2 * get_attractive_force_reingold(node_1.pos, node_2.pos, l_reingold)

        # add gravitation
       # node_1.displacement_vector = node_1.displacement_vector + get_magnetic_force(node_1,node_2)
       # node_2.displacement_vector = node_2.displacement_vector - get_magnetic_force(node_1, node_2)
    # Loop through the nodes to determine gravitation force
    if gravitation_bool:
        for n in graph.nodes:
            node:Node = graph.nodes[n]
            gravitation_force = gravitation(node, p_bary)
            node.displacement_vector = node.displacement_vector + gravitation_force

    for n in graph.nodes:
        node:Node = graph.nodes[n]
        node.pos = node.pos + node.displacement_vector/magnitude(node.displacement_vector) * min(delta, magnitude(node.displacement_vector))

        if(magnitude(node.displacement_vector) > max_force): 
            max_force = magnitude(node.displacement_vector)
    #print("Max force:", max_force)
    return max_force