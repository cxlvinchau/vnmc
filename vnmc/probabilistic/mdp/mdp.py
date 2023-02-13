from typing import Any, Set

from vnmc.common.graph import Graph, GraphNode, GraphEdge
from vnmc.probabilistic.mdp.engine import MDPEngine


class MDPState(GraphNode):

    def __init__(self, name, state_id, atomic_propositions=None, reward=None):
        super().__init__(name, node_id=state_id,
                         atomic_propositions=set() if atomic_propositions is None else atomic_propositions,
                         reward=reward)

    def get_reward(self):
        return self.reward


class MDPTransition(GraphEdge):

    def __init__(self, source: MDPState, action: Any, p: float, target: MDPState):
        super().__init__(source=source, target=target, action=action, p=p)

    def get_probability(self):
        return self.p

    def get_action(self):
        return self.action


class MDP(Graph):

    def get_graph_successors(self, node):
        return [t.target for t in self.transitions if t.source == node]

    def __init__(self):
        self.states: Set[MDPState] = set()
        self.transitions: Set[MDPTransition] = set()
        self.state_ids = 0
        self.is_built = False
        self.engine: MDPEngine = None

    def create_state(self, name, atomic_propositions=None, reward=None):
        state = MDPState(name=name, state_id=self.state_ids, atomic_propositions=atomic_propositions, reward=reward)
        self.states.add(state)
        self.state_ids += 1
        return state

    def create_transition(self, source: MDPState, action: Any, p: float, target: MDPState):
        transition = MDPTransition(source=source, action=action, p=p, target=target)
        self.transitions.add(transition)
        return transition

    def get_actions(self):
        return set([t.get_action() for t in self.transitions])

