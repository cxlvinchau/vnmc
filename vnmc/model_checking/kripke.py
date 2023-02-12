from typing import Set, Dict, Union

from vnmc.logics.ctl.ctl import AtomicPropositionCTL
from vnmc.common.graph import Graph


class _KripkeState:

    def __init__(self, name, state_id, atomic_propositions: Set[AtomicPropositionCTL], **kwargs):
        self.name = name
        self.state_id = state_id
        self.atomic_propositions = atomic_propositions
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, _KripkeState):
            return other.state_id == self.state_id and other.name == self.name
        return False

    def __hash__(self):
        return self.state_id

    def __str__(self):
        return self.name

    def __repr__(self):
        aps = "{" + ', '.join(map(str, self.atomic_propositions)) + "}"
        return f"KripkeState(name=\'{self.name}\', atomic_propositions={aps})"


class _KripkeTransition:

    def __init__(self, source: _KripkeState, target: _KripkeState):
        self.source = source
        self.target = target

    def __eq__(self, other):
        if isinstance(other, _KripkeTransition):
            return other.source == self.source and other.target == self.target
        return False

    def __hash__(self):
        return hash(self.source) + hash(self.target)


class KripkeStructure(Graph):

    def __init__(self):
        self.states: Set[_KripkeState] = set()
        self.initial_states: Set[_KripkeState] = set()
        self.transitions: Set[_KripkeTransition] = set()
        self.state_to_successors: Dict[_KripkeState, Set[_KripkeState]] = dict()
        self.state_to_predecessors: Dict[_KripkeState, Set[_KripkeState]] = dict()
        self.state_ids = 0

    def get_initial_state(self):
        return next(iter(self.initial_states))

    def create_state(self, name: str, atomic_propositions: Set[AtomicPropositionCTL], **kwargs):
        state = _KripkeState(name=name, state_id=self.state_ids, atomic_propositions=atomic_propositions, **kwargs)
        self.states.add(state)
        self.state_ids += 1
        return state

    def create_transition(self, source: _KripkeState, target: _KripkeTransition):
        transition = _KripkeTransition(source, target)
        successors = self.state_to_successors.setdefault(source, set())
        successors.add(target)
        predecessors = self.state_to_predecessors.setdefault(target, set())
        predecessors.add(source)
        self.transitions.add(transition)
        return transition

    def get_successors(self, state: _KripkeState) -> Set[_KripkeState]:
        return self.state_to_successors.get(state, set())

    def get_predecessors(self, states: Union[_KripkeState, Set[_KripkeState]]) -> Set[_KripkeState]:
        if isinstance(states, _KripkeState):
            states = {states}
        predecessors = set()
        for state in states:
            predecessors = predecessors.union(self.state_to_predecessors.get(state, set()))
        return predecessors

    def get_graph_successors(self, node):
        return self.state_to_successors.get(node, set())