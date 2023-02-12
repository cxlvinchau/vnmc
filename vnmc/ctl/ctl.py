import abc


class CTLVisitor(abc.ABC):

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
    def visit_ex(self, element, phi):
        pass

    @abc.abstractmethod
    def visit_eu(self, element, phi1, phi2):
        pass

    @abc.abstractmethod
    def visit_eg(self, element, phi):
        pass


class CTLFormula(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: CTLVisitor):
        pass


class AtomicPropositionCTL(CTLFormula):

    def __init__(self, symbol):
        self.symbol = symbol

    def accept(self, visitor: CTLVisitor):
        return visitor.visit_ap(self)

    def __eq__(self, other):
        if isinstance(other, AtomicPropositionCTL):
            return other.symbol == self.symbol
        return False

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol


class TrueCTL(CTLFormula):

    def accept(self, visitor: CTLVisitor):
        return visitor.visit_true(self)

    def __eq__(self, other):
        return isinstance(other, TrueCTL)

    def __hash__(self):
        return hash(True)

    def __str__(self):
        return "true"


class FalseCTL(CTLFormula):

    def accept(self, visitor: CTLVisitor):
        return visitor.visit_false(self)

    def __eq__(self, other):
        return isinstance(other, FalseCTL)

    def __hash__(self):
        return hash(False)

    def __str__(self):
        return "false"


class ConjunctionCTL(CTLFormula):

    def __init__(self, phi1: CTLFormula, phi2: CTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: CTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_conjunction(self, self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, ConjunctionCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 1

    def __str__(self):
        return f"({str(self.phi1)} ∧ {str(self.phi2)})"


class DisjunctionCTL(CTLFormula):

    def __init__(self, phi1: CTLFormula, phi2: CTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: CTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_disjunction(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, DisjunctionCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 2

    def __str__(self):
        return f"({str(self.phi1)} ∨ {str(self.phi2)})"


class NegationCTL(CTLFormula):

    def __init__(self, phi: CTLFormula):
        self.phi = phi

    def accept(self, visitor: CTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_negation(self, phi)

    def __eq__(self, other):
        if isinstance(other, NegationCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 1

    def __str__(self):
        return f"¬({str(self.phi)})"


class ExistsNextCTL(CTLFormula):

    def __init__(self, phi: CTLFormula):
        self.phi = phi

    def accept(self, visitor: CTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_ex(self, phi)

    def __eq__(self, other):
        if isinstance(other, ExistsNextCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 2

    def __str__(self):
        return f"𝐄𝐗 ({str(self.phi)})"


class ExistsUntilCTL(CTLFormula):

    def __init__(self, phi1: CTLFormula, phi2: CTLFormula):
        self.phi1 = phi1
        self.phi2 = phi2

    def accept(self, visitor: CTLVisitor):
        phi1 = self.phi1.accept(visitor)
        phi2 = self.phi2.accept(visitor)
        return visitor.visit_eu(self, phi1, phi2)

    def __eq__(self, other):
        if isinstance(other, ExistsUntilCTL):
            return other.phi1 == self.phi1 and other.phi2 == self.phi2
        return False

    def __hash__(self):
        return hash(self.phi1) + hash(self.phi2) + 3

    def __str__(self):
        return f"{str(self.phi1)} 𝐄𝐔 {str(self.phi2)}"


class ExistsGloballyCTL(CTLFormula):

    def __init__(self, phi: CTLFormula):
        self.phi = phi

    def accept(self, visitor: CTLVisitor):
        phi = self.phi.accept(visitor)
        return visitor.visit_eg(self, phi)

    def __eq__(self, other):
        if isinstance(other, ExistsGloballyCTL):
            return other.phi == self.phi
        return False

    def __hash__(self):
        return hash(self.phi) + 3

    def __str__(self):
        return f"𝐄𝐆 ({str(self.phi)})"