from typing import Dict, Union

from vnmc.logics.pctl.pctl import PCTLVisitor, PCTLStateFormula
from vnmc.probabilistic import DTMC
from vnmc.probabilistic.dtmc.dtmc import DTMCState
from vnmc.probabilistic.mdp.mdp import MDP


class DTMCModelChecker(PCTLVisitor):

    def __init__(self, dtmc: DTMC):
        self.dtmc = dtmc

    def visit_ap(self, element):
        return set([state for state in self.dtmc.states if element in state.get_atomic_propositions()])

    def visit_true(self, element):
        return self.dtmc.states

    def visit_false(self, element):
        return set()

    def visit_conjunction(self, element, phi1, phi2):
        return phi1.intersection(phi2)

    def visit_disjunction(self, element, phi1, phi2):
        return phi1.union(phi2)

    def visit_negation(self, element, phi):
        return self.dtmc.states.difference(phi)

    def visit_next(self, element, phi) -> Dict[DTMCState, float]:
        result = dict()
        for state in self.dtmc.states:
            result[state] = 0
            for t in self.dtmc.transitions:
                if t.source == state and t.target in phi:
                    result[state] += t.get_probability()
        return result

    def visit_probability_operator(self, element, phi: Dict[DTMCState, float]):
        lb, ub = element.lb, element.ub
        return set([s for s in phi if lb <= phi[s] <= ub])

    def visit_until(self, element, phi1, phi2) -> Dict[DTMCState, float]:
        bad_states = self.dtmc.states.difference(phi1.union(phi2))
        result = self.dtmc.compute_unbounded_reachability(bad_states=bad_states, target_states=phi2)
        for state in bad_states:
            result[state] = 0
        for state in phi2:
            result[state] = 1
        return result

    def visit_bounded_until(self, element, phi1, phi2) -> Dict[DTMCState, float]:
        bad_states = self.dtmc.states.difference(phi1.union(phi2))
        result = self.dtmc.compute_bounded_reachability(bad_states=bad_states, target_states=phi2, t=element.k)
        for state in bad_states:
            result[state] = 0
        for state in phi2:
            result[state] = 1
        return result


def model_check_pctl(model: Union[DTMC, MDP], phi: PCTLStateFormula, state):
    if isinstance(model, DTMC):
        states = phi.accept(DTMCModelChecker(model))
        return state in states
    else:
        raise NotImplementedError("Unsupported model type")