import numpy as np
from numba import njit


@njit
def compute_transient_distribution_numba(initial_distribution: np.ndarray, transition_matrix: np.ndarray, t: int):
    result = initial_distribution
    for _ in range(t):
        result = np.dot(result, transition_matrix)
    return result


compute_transient_distribution_numba(initial_distribution=np.zeros(2), transition_matrix=np.zeros((2, 2)), t=1)
