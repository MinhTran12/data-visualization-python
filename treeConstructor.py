from dataStructures import Node, Graph, Tree
import random

def Check_Child(graph: Graph, node:Node, list, new_edges):
    ## check for all edges if they are already added to the stack/queue
    for e in node.connections:
        if not graph.nodes[e].visited:
            graph.nodes[e].visited = True
            new_edges.append((node.idx, e))
            graph.nodes[e].parent_node = node.idx
            graph.nodes[e].layer = node.layer + 1

            list.append(e)

def Add_tree_edges(graph:Graph, new_edges:list):
    for m in new_edges:
        graph.nodes[m[0]].tree_edges.append(m[1])
        graph.nodes[m[1]].tree_edges.append(m[0])

def DFS(graph:Graph, starting_node):
    ## list to keep track of the nodes to be visited
    stack = [starting_node]
    graph.nodes[starting_node].visited = True


    ## keep track of the new edges
    new_edges = []

    ## keep going until there are no more edges to visit left
    while stack:
        idx = stack.pop()
        Check_Child(graph, graph.nodes[idx], stack, new_edges)

    ## add edges of tree to graph
    Add_tree_edges(graph, new_edges)

def BFS(graph:Graph, starting_node):
    ## list to keep track of the nodes to be visited
    queue = [starting_node]
    graph.nodes[starting_node].visited = True

    ## keep track of the new edges
    new_edges = []

    while queue:
        idx = queue.pop(0)
        Check_Child(graph, graph.nodes[idx], queue, new_edges)

    ## add edges of tree to graph
    Add_tree_edges(graph, new_edges)

