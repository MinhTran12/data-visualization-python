import math
import numpy
from screenSettings import screen_center

initial_radius:float = 60.0
radius_increase:float = 50
draw_offset:list = [-80, -130]

def Offsprings(graph, node):
    ''' function to calculate offsprings using recursion'''
    total = 1
    # base case
    for e in graph.nodes[node].tree_edges:
        if e == graph.nodes[node].parent_node:
            continue
        # as long as the node has more offsprings, count their offsprings and add it to the total
        total += Offsprings(graph, e)
    graph.nodes[node].offsprings = total
    return total

def Position_offsprings(graph, working_node, r, r1, center_node, multiplier):
    ''' Function to determine the position of all offsprings of a node using recursion '''
    ## 1. calculate Tu. The center_node has no parent node, so we set that tu to 1
    if working_node == center_node:
        tu =  1
    else:
        parent_offsprings = graph.nodes[working_node.parent_node].offsprings
        tu = min((working_node.offsprings / (parent_offsprings - 1), 2 * numpy.arccos(r / r1)))

    ## 2. calculate the total angle available to place nodes on
    arc = tu*multiplier

    ## 3. divide the arc up based on the number of offsprings a node has
    number_of_edges = len(working_node.tree_edges)
    total_offsprings = working_node.offsprings
    offspring_counter = 0
    for child in working_node.tree_edges:
        if child == working_node.parent_node:
            continue
        ## 4. determine the angle, x and y of the node
        offsprings = graph.nodes[child].offsprings
        angle = (offspring_counter + offsprings / 2) * arc / total_offsprings  + working_node.angle - arc/2# looks more complex than it is
        offspring_counter += offsprings  # we keep track with a counter "how far on the circle" w
        graph.nodes[child].angle = angle # save the angle, we use this later
        graph.nodes[child].pos[0] = r1 * math.cos(angle) + center_node.pos[0]
        graph.nodes[child].pos[1] = r1 * math.sin(angle) + center_node.pos[1]

        ## if the child has offsprings, determine the positions of the offsprings
        if graph.nodes[child].offsprings != 0:
            Position_offsprings(graph, graph.nodes[child], r1, r1 + radius_increase, center_node, arc)

def Create_Radial(graph, starting_node):

    ## we set a center point
    center_node = graph.nodes[starting_node]

    ## calculate offsprings of all nodes
    Offsprings(graph, starting_node)

    ## because the random location of the starting node is too high to fit the whole layout, I gave it a new position
    graph.nodes[starting_node].pos[0] = screen_center[0] + draw_offset[0]
    graph.nodes[starting_node].pos[1] = screen_center[1] + draw_offset[1]

    ## determine the position for all offsrings of the node
    ## radius for first layer is 100, for the second layer is the radius 50 more
    Position_offsprings(graph, center_node, initial_radius, initial_radius+radius_increase, center_node, 2 * math.pi)
