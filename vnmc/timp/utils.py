from collections import deque

from vnmc.common.automaton import GBA
from vnmc.logics.ltl.utils import AP
from vnmc.timp.command import Configuration
from vnmc.timp.module import Module
from vnmc.timp.preprocessing import VariableCollector, AnnotationCollector
from vnmc.utils import compute_powerset


def timp_to_gba(module: Module):
    """
    Translates a module to a generalized buchi automaton

    Parameters
    ----------
    module: Module
        Module

    Returns
    -------
    GBA

    """
    alphabet = compute_powerset(module.command.accept_visitor(AnnotationCollector()))
    gba = GBA(alphabet=set(map(frozenset, [map(AP, subset) for subset in alphabet])))
    variables = module.command.accept_visitor(VariableCollector())
    init_config = Configuration(command=module.command, state={v: False for v in variables})
    queue = deque([init_config])
    explored = set()
    state_ids = 1
    config_to_state = dict()

    config_to_state[init_config] = gba.create_state(name="init", config=init_config)
    gba.initial_states.add(config_to_state[init_config])

    # Start GBA creation
    while queue:
        current = queue.popleft()
        explored.add(current)

        for config in current.get_successors():
            if config not in explored:
                queue.append(config)
                config_to_state[config] = gba.create_state(name=f"q_{state_ids}", config=config)
                state_ids += 1
            gba.create_transition(source=config_to_state[current],
                                  letter=frozenset(map(AP, current.command.get_annotations(current.state))),
                                  target=config_to_state[config])

    gba.accepting_state_sets.append(set(gba.states))

    return gba


