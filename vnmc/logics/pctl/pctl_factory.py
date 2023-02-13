from vnmc.logics.pctl.pctl import TruePCTL, FalsePCTL, AtomicPropositionPCTL, PCTLStateFormula, NegationPCTL, \
    ConjunctionPCTL, DisjunctionPCTL, PCTLPathFormula, ProbabilityOperatorPCTL, NextPCTL, UntilPCTL, BoundedUntilPCTL


def state_formulae_arguments(func):

    def decorated_func(*args):
        for arg in args:
            if not isinstance(arg, PCTLStateFormula) and not isinstance(arg, (int, float)):
                raise ValueError(f"{str(arg)} is not a PCTL state formula")
        return func(*args)

    return decorated_func


def tt():
    return TruePCTL()


def ff():
    return FalsePCTL()


def AP(symbol):
    return AtomicPropositionPCTL(symbol)


@state_formulae_arguments
def Neg(phi: PCTLStateFormula):
    return NegationPCTL(phi)


@state_formulae_arguments
def And(phi1: PCTLStateFormula, phi2: PCTLStateFormula):
    return ConjunctionPCTL(phi1, phi2)


@state_formulae_arguments
def Or(phi1: PCTLStateFormula, phi2: PCTLStateFormula):
    return DisjunctionPCTL(phi1, phi2)


def P(phi: PCTLPathFormula, lb: float, ub: float):
    if not isinstance(phi, PCTLPathFormula):
        raise ValueError(f"{phi} has to be a PCTL path formula")
    return ProbabilityOperatorPCTL(phi, lb=lb, ub=ub)


@state_formulae_arguments
def X(phi: PCTLStateFormula):
    return NextPCTL(phi)


@state_formulae_arguments
def U(phi1: PCTLStateFormula, phi2: PCTLStateFormula):
    return UntilPCTL(phi1, phi2)


@state_formulae_arguments
def U_bounded(phi1: PCTLStateFormula, phi2: PCTLStateFormula, k: int):
    return BoundedUntilPCTL(phi1, phi2, k=k)