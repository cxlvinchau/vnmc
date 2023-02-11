import itertools
from itertools import combinations, chain
from typing import Set, List

from vnmc.automata.automaton import GBA
from vnmc.ltl.syntax import LTLVisitor, LTLFormula, ConjunctionLTL, UntilLTL, NegationLTL, AtomicPropositionLTL, \
    DisjunctionLTL, NextLTL, TrueLTL, FalseLTL


# Factory methods
def AP(symbol) -> LTLFormula:
    return AtomicPropositionLTL(symbol=symbol)


def And(phi1: LTLFormula, phi2: LTLFormula) -> LTLFormula:
    return ConjunctionLTL(phi1, phi2)


def Or(phi1: LTLFormula, phi2: LTLFormula) -> LTLFormula:
    return DisjunctionLTL(phi1, phi2)


def Neg(phi: LTLFormula) -> LTLFormula:
    return NegationLTL(phi)


def X(phi: LTLFormula) -> LTLFormula:
    return NextLTL(phi)


def Until(phi1: LTLFormula, phi2: LTLFormula) -> LTLFormula:
    return UntilLTL(phi1, phi2)


def F(phi: LTLFormula) -> LTLFormula:
    return UntilLTL(TrueLTL(), phi)


def G(phi: LTLFormula) -> LTLFormula:
    return NegationLTL(F(NegationLTL(phi)))


class LTLFormatter(LTLVisitor):
    def visit_true(self, element):
        return "true"

    def visit_false(self, element):
        return "false"

    def visit_atomic_proposition(self, element: object) -> object:
        return str(element.symbol)

    def visit_conjunction(self, element, phi1, phi2):
        return f"{phi1} ∧ {phi2}"

    def visit_disjunction(self, element, phi1, phi2):
        return f"{phi1} ∨ {phi2}"

    def visit_negation(self, element, phi):
        return f"¬({phi})"

    def visit_next(self, element, phi):
        return f"𝐗 ({phi})"

    def visit_until(self, element, phi1, phi2):
        return f"({phi1}) 𝐔 ({phi2})"


class LTLClosure(LTLVisitor):

    def visit_true(self, element):
        return {element, element.negate()}

    def visit_false(self, element):
        return {element, element.negate()}

    def visit_atomic_proposition(self, element: object) -> object:
        return {element, element.negate()}

    def visit_conjunction(self, element, phi1, phi2):
        return phi1.union(phi2).union({element, element.negate()})

    def visit_disjunction(self, element, phi1, phi2):
        return phi1.union(phi2).union({element, element.negate()})

    def visit_negation(self, element, phi):
        return {element, element.negate()}.union(phi)

    def visit_next(self, element, phi):
        return {element, element.negate()}.union(phi)

    def visit_until(self, element, phi1, phi2):
        return phi1.union(phi2).union({element, element.negate()})


class LTLSubformulae(LTLVisitor):

    def visit_true(self, element):
        return {element}

    def visit_false(self, element):
        return {element}

    def visit_atomic_proposition(self, element: object) -> object:
        return {element}

    def visit_conjunction(self, element, phi1, phi2):
        return {element}.union(phi1).union(phi2)

    def visit_disjunction(self, element, phi1, phi2):
        return {element}.union(phi1).union(phi2)

    def visit_negation(self, element, phi):
        return {element}.union(phi)

    def visit_next(self, element, phi):
        return {element}.union(phi)

    def visit_until(self, element, phi1, phi2):
        return {element}.union(phi1).union(phi2)


def compute_powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def compute_closure(phi: LTLFormula):
    return phi.accept(LTLClosure())


def compute_subformulae(phi: LTLFormula):
    return phi.accept(LTLSubformulae())


def _check_consistent(formulae_set: Set[LTLFormula], closure: Set[LTLFormula]):
    conjunctions = [phi for phi in closure if isinstance(phi, ConjunctionLTL)]
    untils = [phi for phi in closure if isinstance(phi, UntilLTL)]

    if FalseLTL() in formulae_set:
        return False

    # Check logical consitency w.r.t. negation
    for phi in formulae_set:
        if phi.negate() in formulae_set:
            return False

    # Check logical consistency w.r.t. conjunction, i.e. if a and b are in the set, then a && b have to be also
    for phi in conjunctions:
        if phi.phi1 in formulae_set and phi.phi2 in formulae_set:
            if phi not in formulae_set:
                return False
        if phi in formulae_set:
            if phi.phi1 not in formulae_set or phi.phi1 not in formulae_set:
                return False

    # Check local consistency w.r.t Until-operator
    for phi in untils:
        if phi.phi2 in formulae_set and phi not in formulae_set:
            return False
        if phi in formulae_set and phi.phi2 not in formulae_set:
            if phi.phi1 not in formulae_set:
                return False

    # Check maximality of set
    for phi in closure:
        if phi not in formulae_set and phi.negate() not in formulae_set:
            return False

    if TrueLTL() in closure:
        if TrueLTL() not in formulae_set:
            return False

    return True


def compute_elementary_sets(phi: LTLFormula, atomic_propositions = None):
    closure = compute_closure(phi)
    if atomic_propositions:
        closure = closure.union(atomic_propositions)
        closure = closure.union([ap.negate() for ap in atomic_propositions])
    elementary = [subset for subset in compute_powerset(closure) if _check_consistent(subset, closure)]
    return elementary


def ltl_to_gba(phi: LTLFormula, atomic_propositions: List[AtomicPropositionLTL] = None):
    # Compute elementary sets
    elementary_sets = compute_elementary_sets(phi, atomic_propositions)
    n = len(elementary_sets)

    # Compute alphabet and initialize alphabet
    closure = compute_closure(phi)
    atomic_propositions = [ap for ap in closure if isinstance(ap, AtomicPropositionLTL)] if atomic_propositions is None \
        else atomic_propositions
    closure = set(closure).union(atomic_propositions)
    nexts = [phi for phi in closure if isinstance(phi, NextLTL)]
    untils = [phi for phi in closure if isinstance(phi, UntilLTL)]
    alphabet = set([frozenset(subset) for subset in compute_powerset(atomic_propositions)])
    gba = GBA(alphabet)

    # Create GBA states
    states = []
    for idx, elementary_set in enumerate(elementary_sets):
        state = gba.create_state(name=f"s_{idx}", formulae=elementary_set)
        states.append(state)
        if phi in elementary_set:
            gba.initial_states.add(state)

    for phi in untils:
        accepting_set = set()
        for idx, elementary_set in enumerate(elementary_sets):
            if phi not in elementary_set or phi.phi2 in elementary_set:
                accepting_set.add(states[idx])
        gba.accepting_state_sets.append(accepting_set)

    # Create transitions
    for i, j in itertools.product(range(n), range(n)):
        status = True
        for psi in elementary_sets[i]:
            if isinstance(psi, NextLTL) and psi.phi not in elementary_sets[j]:
                status = False
                break
            if isinstance(psi, UntilLTL):
                if psi.phi2 not in elementary_sets[i] and not (
                        psi.phi1 in elementary_sets[i] and psi in elementary_sets[j]):
                    status = False
                    break

        if not status:
            continue

        for psi in nexts:
            if psi.phi in elementary_sets[j]:
                if psi not in elementary_sets[i]:
                    status = False
                    break

        if not status:
            continue

        for psi in elementary_sets[j]:
            if isinstance(psi, UntilLTL):
                if psi.phi1 in elementary_sets[i] and psi not in elementary_sets[i]:
                    status = False
                    break
        if status:
            letter = frozenset(elementary_sets[i]).intersection(atomic_propositions)
            gba.create_transition(states[i], letter, states[j])

    return gba
