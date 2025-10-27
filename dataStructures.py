from dataclasses import dataclass
import numpy as np

##################data structures####################
@dataclass
class Node:
    idx: int    #node index
    pos:np.array #position of the node
    n: int      #number of connections
    connections:list[int]   #list of connected nodes
    visited:bool #visited
    tree_edges: list
    parent_node: int #index of node that is parent
    offsprings: int #number of offsprins in other words l(u)
    angle: float # angle on which node was placed
    layer:int #tree layer node is in (only for trees)
    displacement_vector: np.array # force for reingold alg implementation
    incoming_edges: list[int]   # if this list is empty and outgoing_edges is not, the node is a sink
    outgoing_edges: list[int]   # if this list is empty and incoming_edges is not, the node is a source
    dummy_node: bool # is the node a dummy node
    subgraph: str       # name of subgraph the node is part of

@dataclass
class Edge:
    u: int
    v: int
    weight: int
    is_reversed: bool
    is_dummy: bool

@dataclass
class Graph:
    nodes:dict[int, Node]
    edges:list[Edge]
    layers: list[list[int]]  # layered layout
    type: str #say whether it is directed, undirected etc.

@dataclass
class Tree:
    root:int
    nodes:dict

@dataclass
class InterEdge:
    idx:int #for comparison
    division_points:list[np.array] #List of the division point coordinates
    forces:list[np.array] # list of forces to be applied to division points
    starting_point:np.array #Edge starting point coordinates
    ending_point:np.array #Edge ending point coordinates
    subdivision_count:int #number of division_points
    initial_length:float #initial length of edge
    stiffness:float #stiffness of edge