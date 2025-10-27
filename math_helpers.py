import numpy as np
import sys

min_int = -sys.maxsize - 1
max_int = sys.maxsize

#returns vector's magnitude
def magnitude(vector:np.array) -> float:
    return np.linalg.norm(vector)

#returns normalized vector
def unit_vector(vector:np.array) -> np.array:
    m = magnitude(vector)
    if(m == 0):
        return vector
    return vector / m