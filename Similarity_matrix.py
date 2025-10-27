import numpy as np
from sklearn.manifold import TSNE, MDS, Isomap
from dataStructures import Graph


## we create a matrix

def matrix_dijkstra(graph: Graph):
    # define size of the graph
    similarity_matrix = np.full((len(graph.nodes), len(graph.nodes)), None)
    ###     A   B   C
    ### A   0   1   2
    ### B   1   0   2
    ### C   2   2   0
    ## now we fill the matrix one row at a time
    for n in graph.nodes:
        list = Dijkstra(graph, n)
        for m in list.keys():
            similarity_matrix[n - 1,m - 1] = list[m]
    print(similarity_matrix)
    return similarity_matrix


def Dijkstra(graph: Graph, source: int):
    # unvisited nodes
    Queue = []
    distance = dict()
    temp_dist = dict()

    ## initialization
    for idx in graph.nodes:
        node = graph.nodes[idx]
        distance[idx] = 1000
        temp_dist[idx] = 1000
        Queue.append(node)
    temp_dist[source] = 0
    distance[source] = 0

    while Queue:
        ## get element with minimum distance and remove from queue
        smallest_dist_idx = min(temp_dist, key=temp_dist.get)
        u = graph.nodes[smallest_dist_idx]
        Queue.remove(u)
        distance[smallest_dist_idx] = temp_dist[smallest_dist_idx]
        temp_dist.pop(smallest_dist_idx)

        # check all their neighbours, if min dist to those isn't found yet,
        # check if the dist is shorter via working node
        for neighbour in u.connections:
            if graph.nodes[neighbour] in Queue:
                alt_dist = distance[smallest_dist_idx] + 1
                if alt_dist < temp_dist[neighbour]:
                    temp_dist[neighbour] = alt_dist
    return distance

#Check out https://www.youtube.com/watch?v=4OQeCuLYj-4
def matrix_floyd_warshall(graph:Graph):
    # Initialize the matrix
    #graph.nodes = sorted(graph.nodes.items())
    similarity_matrix = np.full((len(graph.nodes), len(graph.nodes)), 999)
    for edge in graph.edges:
        similarity_matrix[edge.u-1, edge.v-1] = edge.weight
        if graph.type is "directed": 
            similarity_matrix[edge.v-1, edge.u-1] = edge.weight
    for i in range(0, len(graph.nodes)):
        similarity_matrix[i, i] = 0

    # Check for 'shortest path'
    for k in range(0, len(graph.nodes)):
        for i in range(0, len(graph.nodes)):
            for j in range(0, len(graph.nodes)):
                    # there is a difference between similarity matrix and distance matrix, 
                    # so not sure if the check should be bigger or smaller yet
                if similarity_matrix[i, j] > similarity_matrix[i, k] + similarity_matrix[k, j]:
                    similarity_matrix[i, j] = similarity_matrix[i, k] + similarity_matrix[k, j]
    print(similarity_matrix) 

    return similarity_matrix

def dimensionality_reduction(similarity_matrix, graph, dr):
    #Scale of the drawn graph, higher for isomap and mds, because with scale 1 they tend to be clustered too much
    scale:float = 1.0
    if dr == "t-SNE":
        #scale 1 seems to give good results feel free to change
        scale = 1.5
        #perplexity = expected number of close neighbours according to https://distill.pub/2016/misread-tsne/
        #number of iterations also affects the results, play around for it and see for yourself
        X = TSNE(perplexity=5, n_iter=500).fit_transform(similarity_matrix)
    elif dr == "MDS":
        #set to 10 bc tends to cluster too much with scale 1, idk why but it seems to give good results
        scale = 10.0
        #haven't looked at these paremeters yet, so feel free to experiment
        X = MDS(normalized_stress='auto').fit_transform(similarity_matrix)
    elif dr == "ISOMAP":
        #set to 10 bc tends to cluster too much with scale 1, idk why but it seems to give good results
        scale = 10.0
        #This seems to give OK results, but maybe there is still room for improvement
        X = Isomap(n_neighbors=7).fit_transform(similarity_matrix)

    #Set the nodes positions based on the dimensionality reduction that has been set
    for idx, i in enumerate(X):
        graph.nodes[idx+1].pos[0] = i[0] * scale
        graph.nodes[idx+1].pos[1] = i[1] * scale
    return graph