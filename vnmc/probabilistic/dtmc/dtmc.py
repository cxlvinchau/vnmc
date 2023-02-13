from __future__ import annotations

from typing import Set, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from vnmc.probabilistic.dtmc.engine import DTMCEngine

from numba import njit

from vnmc.common.graph import Graph, GraphNode, GraphEdge

import numpy as np

from vnmc.common.graph_algorithms import dfs
from vnmc.probabilistic.dtmc.engine import DTMCSparseEngine, DTMCDenseEngine, DTMCDenseNumbaEngine


class DTMCState(GraphNode):

    def __init__(self, name, state_id, atomic_propositions=None, reward=None):
        super().__init__(name, node_id=state_id,
                         atomic_propositions=set() if atomic_propositions is None else atomic_propositions,
                         reward=reward)

    def get_reward(self):
        return self.reward

    def get_atomic_propositions(self):
        return self.atomic_propositions


class DTMCTransition(GraphEdge):

    def __init__(self, source: DTMCState, p: float, target: DTMCState):
        super().__init__(source=source, target=target, p=p)

    def get_probability(self):
        return self.p


class DTMC(Graph):

    def __init__(self):
        self.states: Set[DTMCState] = set()
        self.transitions: Set[DTMCTransition] = set()
        self.state_ids = 0
        self.is_built = False
        self.engine: DTMCEngine = None

    def create_state(self, name, atomic_propositions=None, reward=None):
        state = DTMCState(name=name, state_id=self.state_ids, atomic_propositions=atomic_propositions,
                          reward=reward)
        self.states.add(state)
        self.state_ids += 1
        return state

    def create_transition(self, source: DTMCState, p: float, target: DTMCState):
        transition = DTMCTransition(source=source, p=p, target=target)
        self.transitions.add(transition)
        return transition

    def build(self, engine):
        if engine == "sparse":
            self.engine = DTMCSparseEngine(self)
        elif engine == "dense":
            self.engine = DTMCDenseEngine(self)
        elif engine == "dense-numba":
            self.engine = DTMCDenseNumbaEngine(self)
        else:
            raise ValueError("Invalid representation type")

    def compute_transient_distribution(self, initial_distribution: Dict[DTMCState, float], t: int):
        return self.engine.compute_transient_distribution(initial_distribution, t)

    def compute_bounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState], t: int):
        return self.engine.compute_bounded_reachability(bad_states, target_states, t)

    def compute_unbounded_reachability(self, bad_states: Set[DTMCState], target_states: Set[DTMCState]):
        return self.engine.compute_unbounded_reachability(bad_states, target_states)

    def compute_expected_reward(self, target_states: Set[DTMCState]):
        return self.engine.compute_expected_reward(target_states)

    def get_graph_successors(self, node):
        return set([t.target for t in self.transitions if t.source == node and t.get_probability() > 0])

    def get_graph_predecessors(self, node):
        return set([t.source for t in self.transitions if t.target == node and t.get_probability() > 0])