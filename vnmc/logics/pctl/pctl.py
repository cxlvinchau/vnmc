import abc


class PCTLVisitor(abc.ABC):

    @abc.abstractmethod
    def visit_ap(self, element):
        pass

    @abc.abstractmethod
    def visit_true(self, element):
        pass

    @abc.abstractmethod
    def visit_false(self, element):
        pass

    @abc.abstractmethod
    def visit_conjunction(self, element, phi1, phi2):
        pass

    @abc.abstractmethod
    def visit_disjunction(self, element, phi1, phi2):
        pass

    @abc.abstractmethod
    def visit_negation(self, element, phi):
        pass

    @abc.abstractmethod
    def visit_next(self, element, phi):
        pass

    @abc.abstractmethod
    def visit_probability_operator(self, element, phi):
        pass

    @abc.abstractmethod
    def visit_until(self, element, phi1, phi2):
        pass

    @abc.abstractmethod
    def visit_bounded_until(self, element, phi1, phi2):
        pass


class PCTLFormula(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: PCTLVisitor):
        pass


class PCTLStateFormula(PCTLFormula, abc.ABC):
    pass


class PCTLPathFormula(PCTLFormula, abc.ABC):
    pass


class AtomicPropositionPCTL(PCTLStateFormula):

    def __init__(self, symbol):
        self.symbol = symbol

    def accept(self, visitor: PCTLVisitor):
        return visitor.visit_ap(self)

    def __eq__(self, other):
        if isinstance(other, AtomicPropositionPCTL):
            return other.symbol == self.symbol
        return False

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol


class TruePCTL(PCTLStateFormula):

    def accept(self, visitor: PCTLVisitor):
        return visitor.visit_true(self)

    def __eq__(self, other):
        return isinstance(other, TruePCTL)

    def __hash__(self):
        return hash(True)

    def __str__(self):
        return "true"


class FalsePCTL(PCTLStateFormula):

    def accept(self, visitor: PCTLVisitor):
        return visitor.visit_false(self)

    def __eq__(self, other):
        return isinstance(other, FalsePCTL)

    def __hash__(self):
        return hash(False)

    def __str__(self):
        return "false"


class ConjunctionPCTL(PCTLStateFormula):

    def __init__(self, phi1: PCTLStateFormula, phi2: PCTLStateFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: PCTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_conjunction(self, self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, ConjunctionPCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 1

    def __str__(self):
        return f"({str(self.phi1)} ∧ {str(self.phi2)})"


class DisjunctionPCTL(PCTLStateFormula):

    def __init__(self, phi1: PCTLStateFormula, phi2: PCTLStateFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: PCTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_disjunction(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, DisjunctionPCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 2

    def __str__(self):
        return f"({str(self.phi1)} ∨ {str(self.phi2)})"


class NegationPCTL(PCTLStateFormula):

    def __init__(self, phi: PCTLStateFormula):
        self.phi = phi

    def accept(self, visitor: PCTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_negation(self, phi)

    def __eq__(self, other):
        if isinstance(other, NegationPCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 1

    def __str__(self):
        return f"¬({str(self.phi)})"


class ProbabilityOperatorPCTL(PCTLStateFormula):

    def __init__(self, phi: PCTLPathFormula, lb: float, ub: float):
        if lb > ub:
            raise ValueError("The lower bound has to be smaller than the upper bound")
        self.phi = phi
        self.lb = lb
        self.ub = ub

    def accept(self, visitor: PCTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_probability_operator(self, phi)

    def __eq__(self, other):
        if isinstance(other, ProbabilityOperatorPCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 2

    def __str__(self):
        return f"𝗣[{self.lb}, {self.ub}]({str(self.phi)})"


class NextPCTL(PCTLPathFormula):

    def __init__(self, phi: PCTLStateFormula):
        self.phi = phi

    def accept(self, visitor: PCTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_next(self, phi)

    def __eq__(self, other):
        if isinstance(other, NextPCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 2

    def __str__(self):
        return f"𝐗 ({str(self.phi)})"


class BoundedUntilPCTL(PCTLPathFormula):

    def __init__(self, phi1: PCTLStateFormula, phi2: PCTLStateFormula, k: int):
        self.phi1 = phi1
        self.phi2 = phi2
        self.k = k

    def accept(self, visitor: PCTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_bounded_until(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, BoundedUntilPCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2 and other.k == self.k
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 3

    def __str__(self):
        return f"{str(self.phi1)} 𝐔(≤{self.k}) {str(self.phi2)}"


class UntilPCTL(PCTLPathFormula):

    def __init__(self, phi1: PCTLStateFormula, phi2: PCTLStateFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: PCTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_until(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, UntilPCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 4

    def __str__(self):
        return f"{str(self.phi1)} 𝐔 {str(self.phi2)}"
