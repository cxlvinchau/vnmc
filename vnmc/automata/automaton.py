import abc
import itertools
from collections import deque
from typing import Set, Dict, Any, Callable, List

from vnmc.graph.graph import Graph


class _AutomatonState:

    def __init__(self, name, state_id, **kwargs):
        self.name = name
        self.state_id = state_id
        self.props = kwargs

    def __eq__(self, other):
        if isinstance(other, _AutomatonState):
            return other.state_id == self.state_id and other.name == self.name
        return False

    def __hash__(self):
        return self.state_id

    def __repr__(self):
        return f"AutomatonState({self.name})"


class _AutomatonTransition:

    def __init__(self, source: _AutomatonState, letter, target: _AutomatonState):
        self.source = source
        self.letter = letter
        self.target = target

    def __eq__(self, other):
        if isinstance(other, _AutomatonTransition):
            return other.source == self.source and other.letter == self.letter and other.target == self.target
        return False

    def __hash__(self):
        return hash(self.source) + hash(self.letter) + hash(self.target)


class FiniteAutomaton(abc.ABC):

    def __init__(self, alphabet):
        self.states: Set[_AutomatonState] = set()
        self.initial_states: Set[_AutomatonState] = set()
        self.transitions: Set[_AutomatonTransition] = set()
        self.alphabet: Set = alphabet
        self.state_to_action_dict: Dict[_AutomatonState, Dict[Any, Set[_AutomatonState]]] = dict()
        self._state_ids = 0

    def get_initial_state(self):
        """
        Returns an arbitrary initial state

        Returns
        -------
        _AutomatonState

        """
        return next(iter(self.initial_states))

    def create_state(self, name, **kwargs) -> _AutomatonState:
        state = _AutomatonState(name=name, state_id=self._state_ids, **kwargs)
        self._state_ids += 1
        self.states.add(state)
        return state

    def create_transition(self, source, letter, target):
        transition = _AutomatonTransition(source, letter, target)
        self.transitions.add(transition)
        action_dict = self.state_to_action_dict.setdefault(source, dict())
        succs = action_dict.setdefault(letter, set())
        succs.add(target)
        return transition

    def get_successors(self, source, letter) -> set:
        return self.state_to_action_dict.get(source, dict()).get(letter, set())

    def to_dot(self, state_formatter: Callable[[Any], str] = None, letter_formatter: Callable[[Any], str] = None):
        out = "digraph G {\n"
        for state in self.states:
            out += f"{state.state_id} [label=\"{state.name if state_formatter is None else state_formatter(state)}\"]"
            out += "\n"
        for t in self.transitions:
            label = str(t.letter) if letter_formatter is None else letter_formatter(t.letter)
            out += f"{t.source.state_id} -> {t.target.state_id} [label=\"{label}\"]\n"
        for idx, state in enumerate(self.initial_states):
            out += f"init_{idx} [label=\"\", shape=none,height=.0,width=.0]\n"
            out += f"init_{idx} -> {state.state_id}\n"
        return out + "}"


class GBA(FiniteAutomaton, Graph):

    def __init__(self, alphabet):
        super().__init__(alphabet)
        self.accepting_state_sets: List[Set[_AutomatonState]] = []

    def create_single_initial_state(self):
        if len(self.initial_states) > 1:
            fresh_init = self.create_state(f"({', '.join(map(lambda s: s.name, self.initial_states))})")
            for init in self.initial_states:
                for letter in self.alphabet:
                    for succ in self.get_successors(init, letter):
                        self.create_transition(fresh_init, letter, succ)
            self.initial_states = {fresh_init}

    def get_graph_successors(self, node):
        if not isinstance(node, _AutomatonState):
            raise TypeError("Node has to be an automaton state")
        successors = set()
        for letter in self.alphabet:
            successors = successors.union(self.get_successors(node, letter))
        return successors


class ProductGBA(GBA):

    def __init__(self, gba1: GBA, gba2: GBA):
        if gba1.alphabet != gba2.alphabet:
            print(gba1.alphabet)
            print(gba2.alphabet)
            raise ValueError("Both GBAs have to have the same alphabet")
        super().__init__(gba1.alphabet)
        self.gba1 = gba1
        self.gba2 = gba2
        self._pair_to_state = dict()
        self._build_initial_states()
        self._build_product()

    def _build_initial_states(self):
        for init1, init2 in itertools.product(self.gba1.initial_states, self.gba2.initial_states):
            self._pair_to_state[(init1.state_id, init2.state_id)] = self.create_state(
                name=f"({init1.name}, {init2.name})",
                q=init1, p=init2)
            self.initial_states.add(self._pair_to_state[(init1.state_id, init2.state_id)])

    def _build_product(self):
        queue = deque(self.initial_states)
        explored = set()

        def get_state_pair(state):
            return state.props["q"], state.props["p"]

        while queue:
            current = queue.popleft()
            q, p = get_state_pair(current)
            explored.add((q.state_id, p.state_id))
            for letter in self.alphabet:
                for q_succ, p_succ in itertools.product(self.gba1.get_successors(q, letter),
                                                        self.gba2.get_successors(p, letter)):
                    if (q_succ.state_id, p_succ.state_id) not in explored:
                        state = self.create_state(name=f"({q_succ.name}, {p_succ.name})",
                                                  q=q_succ, p=p_succ)
                        queue.append(state)
                        self._pair_to_state[(q_succ.state_id, p_succ.state_id)] = state

                    self.create_transition(source=current,
                                           letter=letter,
                                           target=self._pair_to_state[(q_succ.state_id, p_succ.state_id)])
