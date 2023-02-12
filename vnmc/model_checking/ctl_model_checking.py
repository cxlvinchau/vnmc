from collections import deque
from typing import Set

from vnmc.ctl.ctl import AtomicPropositionCTL, CTLVisitor, CTLFormula
from vnmc.ctl.ctl_factory import AP
from vnmc.graph.graph_algorithms import graph_to_dot
from vnmc.model_checking.kripke import KripkeStructure
from vnmc.timp.command import Configuration
from vnmc.timp.expr import Variable
from vnmc.timp.module import Module
from vnmc.timp.preprocessing import VariableCollector


def timp_to_kripke(module: Module):
    kripke = KripkeStructure()
    variables = module.command.accept_visitor(VariableCollector())
    init_config = Configuration(command=module.command, state={v: False for v in variables})
    queue = deque([init_config])
    explored = set()
    state_ids = 1
    config_to_state = dict()

    true_variables: Set[AtomicPropositionCTL] = {AP(v.name) for v in init_config.state if init_config.state[v]}
    atomic_propositions = set(map(AP, init_config.command.get_annotations(init_config.state))).union(true_variables)
    config_to_state[init_config] = kripke.create_state(name="init",
                                                       config=init_config,
                                                       atomic_propositions=atomic_propositions)
    kripke.initial_states.add(config_to_state[init_config])

    # Start GBA creation
    while queue:
        current = queue.popleft()
        explored.add(current)

        for config in current.get_successors():
            if config not in explored:
                queue.append(config)
                true_variables: Set[AtomicPropositionCTL] = {AP(v.name) for v in config.state if config.state[v]}
                atomic_propositions = set(map(AP, current.command.get_annotations(current.state))).union(true_variables)
                config_to_state[config] = kripke.create_state(name=f"q_{state_ids}",
                                                              config=config,
                                                              atomic_propositions=atomic_propositions)
                state_ids += 1
            kripke.create_transition(source=config_to_state[current], target=config_to_state[config])

    return kripke


class GlobalCTLModelChecker(CTLVisitor):

    def __init__(self, kripke_structure: KripkeStructure):
        self.kripke_structure = kripke_structure

    def visit_ap(self, element):
        return set([state for state in self.kripke_structure.states if element in state.atomic_propositions])

    def visit_true(self, element):
        return self.kripke_structure.states

    def visit_false(self, element):
        return set()

    def visit_conjunction(self, element, phi1: Set, phi2: Set):
        return phi1.intersection(phi2)

    def visit_disjunction(self, element, phi1: Set, phi2: Set):
        return phi1.union(phi2)

    def visit_negation(self, element, phi):
        return self.kripke_structure.states.difference(phi)

    def visit_ex(self, element, phi: Set):
        return self.kripke_structure.get_predecessors(phi)

    def visit_eu(self, element, phi1: Set, phi2: Set):
        satisfying_states = set()
        updated_set = phi2
        while satisfying_states != updated_set:
            satisfying_states = updated_set
            updated_set = phi1.intersection(self.kripke_structure.get_predecessors(satisfying_states))
            updated_set = updated_set.union(phi2)
        return satisfying_states

    def visit_eg(self, element, phi: Set):
        # Compute fixpoint
        satisfying_states = set()
        updated_set = phi
        while satisfying_states != updated_set:
            satisfying_states = updated_set
            updated_set = phi.intersection(self.kripke_structure.get_predecessors(satisfying_states))
        return satisfying_states


def model_check_ctl(module: Module, phi: CTLFormula):
    kripke_structure = timp_to_kripke(module)
    global_result = phi.accept(GlobalCTLModelChecker(kripke_structure))
    return kripke_structure.initial_states.issubset(global_result)


