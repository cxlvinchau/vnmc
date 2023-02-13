from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vnmc.probabilistic import DTMC
    from vnmc.probabilistic.dtmc.dtmc import DTMCState

import abc
from typing import Set, Dict
from vnmc.common.graph_algorithms import dfs
from numba import njit
import numpy as np


class DTMCEngine(abc.ABC):

    def __init__(self, dtmc: DTMC):
        self.dtmc = dtmc

    @abc.abstractmethod
    def compute_transient_distribution(self, initial_distribution: Dict[DTMCState, float], t: int):
        """
        Computes the transient distribution
        """
        pass

    @abc.abstractmethod
    def compute_bounded_reachability(self, bad_states: Set[DTMCState],
                                     target_states: Set[DTMCState], t: int):
        pass

    @abc.abstractmethod
    def compute_unbounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState]):
        pass

    @abc.abstractmethod
    def compute_expected_reward(self, target_states: Set[DTMCState]):
        pass


class DTMCSparseEngine(DTMCEngine):

    def compute_transient_distribution(self, initial_distribution: Dict[DTMCState, float], t: int):
        pass

    def compute_bounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState], t: int):
        pass

    def compute_unbounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState]):
        pass


class DTMCDenseEngine(DTMCEngine):

    def __init__(self, dtmc):
        super().__init__(dtmc)
        n = len(self.dtmc.states)
        self.state_to_idx = {k: v for v, k in enumerate(self.dtmc.states)}
        self.probability_matrix: np.ndarray = np.zeros((n, n))
        for transition in self.dtmc.transitions:
            i, j = self.state_to_idx[transition.source], self.state_to_idx[transition.target]
            self.probability_matrix[i][j] = transition.get_probability()

    def compute_initial_distribution(self, initial_distribution: Dict[DTMCState, float]):
        result = np.zeros(len(self.state_to_idx))
        for state, probability in initial_distribution.items():
            result[self.state_to_idx[state]] = probability
        return result

    def compute_transient_distribution(self, initial_distribution: Dict[DTMCState, float], t: int):
        result = self.compute_initial_distribution(initial_distribution)
        for _ in range(t):
            result = result.dot(self.probability_matrix)
        return {state: result[self.state_to_idx[state]] for state in self.dtmc.states if
                result[self.state_to_idx[state]] > 0}

    def compute_bounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState], t: int):
        return self._compute_reachability(bad_states=bad_states, target_states=target_states, t=t, unbounded=False)

    def compute_unbounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState]):
        return self._compute_reachability(bad_states=bad_states, target_states=target_states, unbounded=True)

    def compute_expected_reward(self, target_states: Set[DTMCState]):
        predecessors = dfs(self.dtmc, nodes=list(target_states), forward=False)
        unreachable = self.dtmc.states.difference(predecessors)
        unreachable_predecessors = dfs(self.dtmc, nodes=list(unreachable), forward=False)
        undetermined_states = list(self.dtmc.states.difference(unreachable_predecessors).difference(target_states))
        undetermined_states_idxs = [self.state_to_idx[s] for s in undetermined_states]
        transition_matrix = self.probability_matrix[undetermined_states_idxs, :][:, undetermined_states_idxs]
        r = np.array([s.get_reward() if s.get_reward() is not None else 0 for s in undetermined_states])
        result = np.linalg.solve(a=transition_matrix - np.identity(len(undetermined_states)), b=-r)
        result = {state: result[idx] for idx, state in enumerate(undetermined_states)}
        result.update({state: 0 for state in target_states})
        return result

    def _compute_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState], t=None, unbounded=True):
        if len(bad_states.intersection(target_states)) > 0:
            raise ValueError("The bad states and target states need to be disjoint")
        undetermined_states = dfs(self.dtmc, nodes=list(target_states), forward=False)
        undetermined_states = list(undetermined_states.difference(bad_states).difference(target_states))
        undetermined_states_idxs = [self.state_to_idx[s] for s in undetermined_states]
        target_states_idxs = [self.state_to_idx[s] for s in target_states]

        transition_matrix = self.probability_matrix[undetermined_states_idxs, :][:, undetermined_states_idxs]
        b = self.probability_matrix[undetermined_states_idxs, :][:, target_states_idxs].sum(axis=1)

        if unbounded:
            result = np.linalg.solve(a=transition_matrix - np.identity(len(undetermined_states)), b=-b)
        else:
            result = np.zeros(len(undetermined_states))
            for _ in range(t):
                result = transition_matrix.dot(result) + b
        return {state: result[idx] for idx, state in enumerate(undetermined_states)}


class DTMCDenseNumbaEngine(DTMCDenseEngine):

    def __init__(self, dtmc):
        super().__init__(dtmc)

        # Execute numba functions to trigger compilation
        DTMCDenseNumbaEngine._compute_transient_distribution_numba(np.zeros(2), np.zeros((2, 2)), t=1)

    @staticmethod
    @njit
    def _compute_transient_distribution_numba(initial_distribution: np.ndarray, transition_matrix: np.ndarray, t: int):
        result = initial_distribution
        for _ in range(t):
            result = np.dot(result, transition_matrix)
        return result

    @staticmethod
    @njit
    def _compute_unbounded_reachability_numba(transition_matrix: np.ndarray, t: int):
        pass

    def compute_transient_distribution(self, initial_distribution: Dict[DTMCState, float], t: int):
        init = self.compute_initial_distribution(initial_distribution)
        result = self._compute_transient_distribution_numba(initial_distribution=init,
                                                            transition_matrix=self.probability_matrix,
                                                            t=t)
        return {state: result[self.state_to_idx[state]] for state in self.dtmc.states if
                result[self.state_to_idx[state]] > 0}

    def compute_bounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState], t: int):
        pass

    def compute_unbounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState]):
        pass
