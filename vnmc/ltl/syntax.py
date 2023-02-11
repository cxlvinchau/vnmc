import abc


class LTLVisitor(abc.ABC):

    @abc.abstractmethod
    def visit_true(self, element):
        pass

    @abc.abstractmethod
    def visit_false(self, element):
        pass

    @abc.abstractmethod
    def visit_atomic_proposition(self, element: object) -> object:
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
    def visit_until(self, element, phi1, phi2):
        pass


class LTLFormula(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: LTLVisitor):
        pass

    @abc.abstractmethod
    def negate(self):
        pass


class TrueLTL(LTLFormula):

    def __eq__(self, other):
        return isinstance(other, TrueLTL)

    def __hash__(self):
        return hash(True) + 1

    def negate(self):
        return FalseLTL()

    def __str__(self):
        return "true"

    def accept(self, visitor: LTLVisitor):
        return visitor.visit_true(self)


class FalseLTL(LTLFormula):

    def __eq__(self, other):
        return isinstance(other, FalseLTL)

    def __hash__(self):
        return hash(False) + 1

    def negate(self):
        return TrueLTL()

    def __str__(self):
        return "false"

    def accept(self, visitor: LTLVisitor):
        return visitor.visit_false(self)


class AtomicPropositionLTL(LTLFormula):

    def __init__(self, symbol):
        self.symbol = symbol

    def accept(self, visitor: LTLVisitor):
        return visitor.visit_atomic_proposition(self)

    def __eq__(self, other):
        if isinstance(other, AtomicPropositionLTL):
            return other.symbol == self.symbol
        return False

    def __hash__(self):
        return hash(self.symbol)

    def negate(self):
        return NegationLTL(self)

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return f"AP({self.symbol})"


class ConjunctionLTL(LTLFormula):

    def __init__(self, phi1: LTLFormula, phi2: LTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: LTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_conjunction(element=self, phi1=phi1, phi2=phi2)

    def __eq__(self, other):
        if isinstance(other, ConjunctionLTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 1

    def negate(self):
        return NegationLTL(self)

    def __str__(self):
        return f"({str(self.phi1)} ∧ {str(self.phi2)})"


class DisjunctionLTL(LTLFormula):

    def __init__(self, phi1: LTLFormula, phi2: LTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: LTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_disjunction(element=self, phi1=phi1, phi2=phi2)

    def __eq__(self, other):
        if isinstance(other, DisjunctionLTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 2

    def negate(self):
        return NegationLTL(self)

    def __str__(self):
        return f"({str(self.phi1)} ∨ {str(self.phi2)})"


class NegationLTL(LTLFormula):

    def __init__(self, phi: LTLFormula):
        self.phi = phi

    def accept(self, visitor: LTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_negation(self, phi)

    def __eq__(self, other):
        if isinstance(other, NegationLTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 3

    def negate(self):
        return self.phi

    def __str__(self):
        return f"¬({str(self.phi)})"


class NextLTL(LTLFormula):

    def __init__(self, phi: LTLFormula):
        self.phi = phi

    def accept(self, visitor: LTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_next(self, phi)

    def __eq__(self, other):
        if isinstance(other, NextLTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 4

    def negate(self):
        return NegationLTL(self)

    def __str__(self):
        return f"X ({str(self.phi)})"


class UntilLTL(LTLFormula):

    def __init__(self, phi1: LTLFormula, phi2: LTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: LTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_until(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, UntilLTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 5

    def negate(self):
        return NegationLTL(self)

    def __str__(self):
        return f"{str(self.phi1)} 𝐔 {str(self.phi2)}"
