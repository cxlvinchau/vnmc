import abc


class CTLVisitor(abc.ABC):

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
    def visit_eg(self, element, phi):
        pass

    @abc.abstractmethod
    def visit_eu(self, element, phi1, phi2):
        pass


class CTLFormula(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: CTLVisitor):
        pass