import abc
from typing import Set, Dict, Any, Callable


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

    def to_dot(self, letter_formatter: Callable[[Any], str] = None):
        out = "digraph G {\n"
        for t in self.transitions:
            label = str(t.letter) if letter_formatter is None else letter_formatter(t.letter)
            out += f"{t.source.name} -> {t.target.name} [label=\"{label}\"]\n"
        for idx, state in enumerate(self.initial_states):
            out += f"init_{idx} [label=\"\", shape=none,height=.0,width=.0]\n"
            out += f"init_{idx} -> {state.name}\n"
        return out + "}"


class GBA(FiniteAutomaton):

    def __init__(self, alphabet):
        super().__init__(alphabet)
        self.accepting_state_sets = []
