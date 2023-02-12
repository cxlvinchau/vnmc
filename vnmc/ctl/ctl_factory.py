from vnmc.ctl.ctl import CTLFormula, DisjunctionCTL, AtomicPropositionCTL, ConjunctionCTL, NegationCTL, \
    ExistsGloballyCTL, ExistsUntilCTL, ExistsNextCTL, TrueCTL


def AP(symbol):
    return AtomicPropositionCTL(symbol)


def And(phi1: CTLFormula, phi2: CTLFormula):
    return ConjunctionCTL(phi1, phi2)


def Or(phi1: CTLFormula, phi2: CTLFormula):
    return DisjunctionCTL(phi1, phi2)


def Neg(phi: CTLFormula):
    return NegationCTL(phi)


def Implies(phi1: CTLFormula, phi2: CTLFormula):
    return Or(NegationCTL(phi1), phi2)


def EX(phi: CTLFormula):
    return ExistsNextCTL(phi)


def AX(phi: CTLFormula):
    return Neg(EX(Neg(phi)))


def EF(phi: CTLFormula):
    return ExistsUntilCTL(TrueCTL(), phi)


def EG(phi: CTLFormula):
    return ExistsGloballyCTL(phi)


def AG(phi: CTLFormula):
    return Neg(EF(Neg(phi)))


def EW(phi1: CTLFormula, phi2: CTLFormula):
    return Or(EG(phi1), ExistsUntilCTL(phi1, phi2))


def EU(phi1: CTLFormula, phi2: CTLFormula):
    return ExistsUntilCTL(phi1, phi2)


def AU(phi1: CTLFormula, phi2: CTLFormula):
    return Neg(EW(Neg(phi2), And(Neg(phi1), Neg(phi2))))
