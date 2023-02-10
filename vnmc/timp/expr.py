import abc
from typing import Dict


class BooleanExpressionVisitor(abc.ABC):

    @abc.abstractmethod
    def visit_variable(self, element):
        pass

    @abc.abstractmethod
    def visit_constant(self, element):
        pass

    @abc.abstractmethod
    def visit_conjunction(self, element, expr1, expr2):
        pass

    @abc.abstractmethod
    def visit_disjunction(self, element, expr1, expr2):
        pass

    @abc.abstractmethod
    def visit_negation(self, element, expr):
        pass

    @abc.abstractmethod
    def visit_brackets(self, element, expr):
        pass


class BooleanExpression(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: BooleanExpressionVisitor):
        pass

    @abc.abstractmethod
    def pretty(self):
        pass


class Variable(BooleanExpression):

    def __init__(self, name):
        self.name = name

    def accept(self, visitor: BooleanExpressionVisitor):
        return visitor.visit_variable(self)

    def __eq__(self, other):
        if isinstance(other, Variable):
            return other.name == self.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Variable({repr(self.name)})"

    def pretty(self):
        return self.name


class Constant(BooleanExpression):

    def __init__(self, value: bool):
        self.value = value

    def accept(self, visitor: BooleanExpressionVisitor):
        return visitor.visit_constant(self)

    def pretty(self):
        if self.value:
            return "true"
        return "false"

    def __eq__(self, other):
        if isinstance(other, Constant):
            return other.value == self.value
        return False

    def __hash__(self):
        return hash(self.value)


class Conjunction(BooleanExpression):

    def __init__(self, expr1: BooleanExpression, expr2: BooleanExpression):
        self.expr1 = expr1
        self.expr2 = expr2

    def accept(self, visitor: BooleanExpressionVisitor):
        e1 = self.expr1.accept(visitor)
        e2 = self.expr2.accept(visitor)
        return visitor.visit_conjunction(self, e1, e2)

    def pretty(self):
        return f"{self.expr1.pretty()} and {self.expr2.pretty()}"

    def __eq__(self, other):
        if isinstance(other, Conjunction):
            return other.expr1 == self.expr1 and other.expr2 == self.expr2
        return False

    def __hash__(self):
        return hash(self.expr1) + hash(self.expr2)


class Disjunction(BooleanExpression):

    def __init__(self, expr1: BooleanExpression, expr2: BooleanExpression):
        self.expr1 = expr1
        self.expr2 = expr2

    def accept(self, visitor: BooleanExpressionVisitor):
        e1 = self.expr1.accept(visitor)
        e2 = self.expr2.accept(visitor)
        return visitor.visit_disjunction(self, e1, e2)

    def pretty(self):
        return f"{self.expr1.pretty()} or {self.expr2.pretty()}"

    def __eq__(self, other):
        if isinstance(other, Disjunction):
            return other.expr1 == self.expr1 and other.expr2 == self.expr2
        return False

    def __hash__(self):
        return hash(self.expr1) + hash(self.expr2)


class Negation(BooleanExpression):

    def __init__(self, expr: BooleanExpression):
        self.expr = expr

    def accept(self, visitor: BooleanExpressionVisitor):
        e = self.expr.accept(visitor)
        return visitor.visit_negation(self, e)

    def pretty(self):
        return f"!{self.expr.pretty()}"

    def __eq__(self, other):
        if isinstance(other, Negation):
            return other.expr == self.expr
        return False

    def __hash__(self):
        return hash(self.expr) + 1


class Brackets(BooleanExpression):

    def __init__(self, expr: BooleanExpression):
        self.expr = expr

    def accept(self, visitor: BooleanExpressionVisitor):
        e = self.expr.accept(visitor)
        return visitor.visit_brackets(self, e)

    def pretty(self):
        return f"({self.expr.pretty()})"

    def __eq__(self, other):
        if isinstance(other, Brackets):
            return other.expr == self.expr
        return False

    def __hash__(self):
        return hash(self.expr) + 2


class ExpressionEvaluator(BooleanExpressionVisitor):

    def __init__(self, state: Dict[Variable, bool]):
        self.state = state

    def visit_variable(self, element):
        return self.state[element]

    def visit_constant(self, element):
        return element.value

    def visit_conjunction(self, element, expr1, expr2):
        return expr1 and expr2

    def visit_disjunction(self, element, expr1, expr2):
        return expr1 or expr2

    def visit_negation(self, element, expr):
        return not expr

    def visit_brackets(self, element, expr):
        return expr