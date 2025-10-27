from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from Similarity_matrix import matrix_floyd_warshall
from dataStructures import Graph, Node, Edge
from math_helpers import magnitude
import statistics
import matplotlib.pyplot as plt
import numpy as np
import statistics as stat

def stress(graph: Graph, dataset_name:str, projection_method:str):
    similarity_matrix = matrix_floyd_warshall(graph)

    node_count:int = len(graph.nodes.values())

    euclidean_distances = []
    warshall_distances = []

    #Add the euclidean distances and warshall distances to list
    for i in range(1, node_count):
        for j in range(1, node_count):
            #don't measure the distance of a node with itself, continue
            if(i == j): continue

            euclidean_distances.append(magnitude(graph.nodes[i].pos - graph.nodes[j].pos))
            warshall_distances.append(float(similarity_matrix[i, j]))

    #means and standard diviations of euclidean distance and floyd warshall distance, used for standardization
    mean_euclidean:float = statistics.mean(euclidean_distances)
    mean_warshall:float = statistics.mean(warshall_distances)
    std_euclidean:float = statistics.stdev(euclidean_distances)
    std_warshall:float = statistics.stdev(warshall_distances)

    if std_euclidean == 0.0: std_euclidean = 1
    if std_warshall == 0.0: std_warshall = 1

    #Used to calculate stress
    total_stress:float = 0.0
    total_warshall_squared:float = 0.0

    #Used for the Shepard diagram
    shepard_x:list[float] = []
    shepard_y:list[float] = []

    #Used for the Pearson correlation coefficient
    cov_numerator:float = 0.0
    pearson_denominator_x:float = 0.0
    pearson_denominator_y:float = 0.0

    for i in range(0, len(euclidean_distances)):
        #standardize euclidean distance and floyd warshall distance
        standardized_euclidean = (euclidean_distances[i] - mean_euclidean) / std_euclidean
        standardized_warshall = (warshall_distances[i] - mean_warshall) / std_warshall

        #stress numerator
        total_stress += ((standardized_warshall-standardized_euclidean)**2.0)
        #Used as denominator of stress
        total_warshall_squared += standardized_warshall ** 2.0

        #used for the shepard diagram
        shepard_x.append(standardized_warshall)
        shepard_y.append(standardized_euclidean)

        #used for pearson correlation
        cov_numerator += (warshall_distances[i] - mean_warshall) * (euclidean_distances[i] - mean_euclidean)
        pearson_denominator_x += (warshall_distances[i] - mean_warshall) ** 2.0
        pearson_denominator_y += (euclidean_distances[i] - mean_euclidean) ** 2.0



    #normalized stress (single float value)
    print("stress " + dataset_name[0:len(dataset_name)-4] + "-" + projection_method  + "  " + str(total_stress/total_warshall_squared))

    #compute the pearson correlation
    cov = cov_numerator / len(warshall_distances)
    pearson_correlation = cov / (std_warshall * std_euclidean)
    print("p = " + str(pearson_correlation))
    
    #plot styling
    #This is used for the scatterplot's regression line
    b, a = np.polyfit(shepard_x, shepard_y, deg=1)
    xseq = np.linspace(min(shepard_x), max(shepard_x), num=100)

    plt.clf()
    plt.rcParams['figure.dpi'] = 200

    radius:float = 80.0
    ax = plt.gca()
    plt.scatter(shepard_x, shepard_y, alpha=0.1, s=radius, linewidths=0, c="black")

    #plot red diagonal line
    ax.plot([0, 1], [0, 1], transform=ax.transAxes,color="red", linestyle="dashed", alpha=0.3)
    # Plot regression line
    plt.plot(xseq, a + b * xseq, color="black", lw=1.5)

    plt.margins(x=0.02, y=0.02)
    plt.tight_layout()

    plt.title(dataset_name[0:len(dataset_name)-4] + " - " + projection_method + " ($\\rho =$" + str(round(pearson_correlation, 2)) + ")")
    plt.xlabel('$\\Delta^n (x_i, x_j)$')
    plt.ylabel('$\\Delta^q (P(x_i), P(x_j))$')

    #Shepard diagram
    plt.savefig("out/shepard-"+dataset_name[0:len(dataset_name)-4] + "-" + projection_method, dpi=400, bbox_inches='tight')

def scalar(N,k):
    return 2 / (N * k * (2 * N - 3 * k - 1))

def projection_neighbors(graph, k):
    neighbors = []
    for id in range(1,len(graph.nodes)+1):
        node = graph.nodes[id]
        local_neighbors = []
        for index, m in enumerate(graph.nodes):
            if m != id:
                node_2 = graph.nodes[m]
                local_neighbors.append((m-1, np.linalg.norm(np.array(node.pos) - np.array(node_2.pos))))
        local_neighbors.sort(key=lambda x: x[1])
        neighbors.append(local_neighbors[:k])

    result = [[],[]]
    for n in neighbors:
        a = list(map(list, zip(*n)))
        result[0].append(a[0])
        result[1].append(a[1])
    return result[0], result[1]

def sum_of_differences(positions, actual_positions, k):
    sum = 0
    for index, n in enumerate(positions):
        for ind, m in enumerate(n):
            if m==index or m == -1:
                continue
            if type(actual_positions) == list:
                i = actual_positions[index].index(m)
            else:
                i = np.where(actual_positions[index]==m)[0][0]
            sum += i - k

    return sum

def check_neighbors(neighbors, true_neighbors):
    for index, n in enumerate(neighbors):
        for ind, m in enumerate(n):
            tocheck = true_neighbors[index]
            if m in tocheck:
                neighbors[index][ind] = -1
    return neighbors

def trustworthiness(graph, k:int):
    N = len(graph.nodes)

    ## create distance matrix
    dm = matrix_floyd_warshall(graph)

    ## find nearest neighbors in dataset
    neigh = NearestNeighbors(n_neighbors=(k+1)).fit(dm)
    distances, indices = neigh.kneighbors(dm)

    ## now we need to find the true position for all those neighbors
    p_indices, p_distances = projection_neighbors(graph, k)
    indices = check_neighbors(indices, p_indices)

    ## now we need to find the true position for all those neighbors
    p_indices, p_distances = projection_neighbors(graph, len(graph.nodes))

    ## scalar times sum
    print("scalar", scalar(N,k))
    return 1 - scalar(N,k) * sum_of_differences(indices, p_indices, k)

def continuity(graph, k):
    N = len(graph.nodes)
    scalar(N,k)

    ## create distance matrix
    dm = matrix_floyd_warshall(graph)

    ## find nearest neighbors in dataset
    neigh = NearestNeighbors(n_neighbors=(k+1)).fit(dm)
    distances, indices = neigh.kneighbors(dm)
    ## find nearest neighbors in projection
    p_indices, p_distances = projection_neighbors(graph, k)

    p_indices = check_neighbors(p_indices, indices)

    ## now we need to find the true position for all those neighbors
    neigh = NearestNeighbors(n_neighbors=len(graph.nodes)).fit(dm)
    distances, indices = neigh.kneighbors(dm)

    return 1 - scalar(N, k) * sum_of_differences(p_indices, indices, k)

# Credits: 
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://mathworld.wolfram.com/Line-LineIntersection.html
# https://www.cuemath.com/geometry/angle-between-vectors/

# Given three collinear points p, q, r, the function checks if  
# point q lies on line segment 'pr'  
def onSegment(p:Node, q:Node, r:Node): 
    if ( (q.pos[0] <= max(p.pos[0], r.pos[0])) and (q.pos[0] >= min(p.pos[0], r.pos[0])) and 
           (q.pos[1] <= max(p.pos[1], r.pos[1])) and (q.pos[1] >= min(p.pos[1], r.pos[1]))): 
        return True
    return False

def orientation(p:Node, q:Node, r:Node):
    val = (float(q.pos[1] - p.pos[1]) * (r.pos[0] - q.pos[0])) - (float(q.pos[0] - p.pos[0]) * (r.pos[1] - q.pos[1])) 
    if (val > 0): # Clockwise orientation 
        return 1
    elif (val < 0): # Counterclockwise orientation 
        return 2
    else: # Collinear orientation 
        return 0

# Line p1-q1, and line p2-q2
def doIntersect(edge1:Edge, edge2:Edge, graph:Graph): 
    p1 = graph.nodes[edge1.u]
    q1 = graph.nodes[edge1.v]
    p2 = graph.nodes[edge2.u]
    q2 = graph.nodes[edge2.v]

    # Check if edges share the same node
    if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
        return False

    # Find the 4 orientations required for the general and special cases 
    o1 = orientation(p1, q1, p2) 
    o2 = orientation(p1, q1, q2) 
    o3 = orientation(p2, q2, p1) 
    o4 = orientation(p2, q2, q1) 
  
    # General case 
    if ((o1 != o2) and (o3 != o4)): 
        return True
  
    # Special Cases 
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1 
    if ((o1 == 0) and onSegment(p1, p2, q1)): 
        return True
  
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1 
    if ((o2 == 0) and onSegment(p1, q2, q1)): 
        return True
  
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2 
    if ((o3 == 0) and onSegment(p2, p1, q2)): 
        return True
  
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2 
    if ((o4 == 0) and onSegment(p2, q1, q2)): 
        return True
  
    # If none of the cases 
    return False

# Kinda messy, uses a lot of determinant
# Check the equation in the wolfram link
def getCrossingPoint(edge1:Edge, edge2:Edge, graph:Graph):
    p1 = graph.nodes[edge1.u]
    q1 = graph.nodes[edge1.v]
    p2 = graph.nodes[edge2.u]
    q2 = graph.nodes[edge2.v]

    det1 = np.linalg.det(np.array([p1.pos, q1.pos]))
    det2 = np.linalg.det(np.array([p2.pos, q2.pos]))
    x_dif1 = p1.pos[0] - q1.pos[0]
    y_dif1 = p1.pos[1] - q1.pos[1]
    x_dif2 = p2.pos[0] - q2.pos[0]
    y_dif2 = p2.pos[1] - q2.pos[1]

    denominator = x_dif1*y_dif2 - y_dif1*x_dif2
    if denominator == 0:
        denominator = 1
    x_crossing = (det1 * x_dif2 - x_dif1 * det2) / denominator
    y_crossing = (det1 * y_dif2 - y_dif1 * det2) / denominator
    return np.array([x_crossing,y_crossing])

def getAngle(vector1:np.array, vector2:np.array):
    dot_product = np.dot(vector1, vector2)
    norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
    # angle = np.degrees(np.arccos(np.clip(dot_product / norm_product, -1, 1)))
    # return round((angle + 360) % 360, 2)
    cos = round(np.clip(dot_product / norm_product, -1, 1), 5)
    return abs(cos)

def calculateCrossingAngle(edge1:Edge, edge2:Edge, graph:Graph):
    crossing_point = getCrossingPoint(edge1, edge2, graph)
    p1 = graph.nodes[edge1.u]
    p2 = graph.nodes[edge2.u]
    v1 = p1.pos - crossing_point
    v2 = p2.pos - crossing_point

    # Only need to calculate one angle to compare the remaining angle
    # angle = getAngle(v1, v2)
    # if angle > 90:
    #     angle = round(180 - angle, 2)

    # return angle
    cos = getAngle(v1, v2)
    return cos

# Iterate over every edges
def crossingCalculation(graph:Graph):
    number_of_crossings = 0
    crossings = []

    for i in range(len(graph.edges)-1):
        for j in range(i+1,len(graph.edges)):
            edge1 = graph.edges[i]
            edge2 = graph.edges[j]
            # Check if there is a crossing
            if doIntersect(edge1, edge2, graph):
                number_of_crossings +=1

                # Get crossing angle
                new_angle = calculateCrossingAngle(edge1, edge2, graph)
                crossings.append(new_angle)
    if len(crossings) == 0:
        crossings.append(1)
    mean_resolution = round(stat.mean(crossings), 5)
    median_resolution = round(stat.median(crossings), 5)
    smallest_resolution = max(crossings)
    return number_of_crossings, mean_resolution, median_resolution, smallest_resolution