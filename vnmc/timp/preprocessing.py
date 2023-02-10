from vnmc.timp.command import CommandVisitor, AssignmentCommand, SkipCommand, SequentialCompositionCommand, \
    IfElseCommand
from vnmc.timp.expr import BooleanExpressionVisitor, Constant


class Linearizer(CommandVisitor):
    def visit_skip(self, element):
        return [element]

    def visit_assignment(self, element, variable, expr):
        return [element]

    def visit_sequential_composition(self, element, command1, command2):
        return command1 + command2

    def visit_if_else(self, element, expr, command1, command2):
        return [element]


class _ExprVariableCollector(BooleanExpressionVisitor):

    def visit_conjunction(self, element, expr1, expr2):
        return expr1.union(expr2)

    def visit_disjunction(self, element, expr1, expr2):
        return expr1.union(expr2)

    def visit_negation(self, element, expr):
        return expr

    def visit_brackets(self, element, expr):
        return expr

    def visit_variable(self, element):
        return set([element])

    def visit_constant(self, element):
        return set()


class VariableCollector(CommandVisitor):

    def __init__(self):
        super().__init__(_ExprVariableCollector())

    def visit_skip(self, element):
        return set()

    def visit_assignment(self, element, variable, expr):
        return variable.union(expr)

    def visit_sequential_composition(self, element, command1, command2):
        return command1.union(command2)

    def visit_if_else(self, element, expr, command1, command2):
        return expr.union(command1.union(command2))


class _ExprSimplifier(BooleanExpressionVisitor):

    def visit_variable(self, element):
        return element

    def visit_constant(self, element):
        return element

    def visit_conjunction(self, element, expr1, expr2):
        if expr1 == expr2:
            return expr1
        if isinstance(expr1, Constant):
            if expr1.value:
                return expr2
            return expr1
        if isinstance(expr2, Constant):
            if expr2.value:
                return expr1
            return expr2
        return element

    def visit_disjunction(self, element, expr1, expr2):
        if expr1 == expr2:
            return expr1
        if isinstance(expr1, Constant):
            if expr1.value:
                return expr1
            return expr2
        if isinstance(expr2, Constant):
            if expr2.value:
                return expr2
            return expr1
        return element

    def visit_negation(self, element, expr):
        if isinstance(expr, Constant):
            if expr.value:
                return Constant(value=False)
            return Constant(value=True)
        return element

    def visit_brackets(self, element, expr):
        return expr


class Simplifier(CommandVisitor):

    def __init__(self):
        super().__init__(_ExprSimplifier())
    def visit_skip(self, element):
        return element

    def visit_assignment(self, element, variable, expr):
        return AssignmentCommand(variable=variable, expr=expr)

    def visit_sequential_composition(self, element, command1, command2):
        if command1 == SkipCommand():
            return command2
        if command2 == SkipCommand():
            return command1
        return SequentialCompositionCommand(command1=command1, command2=command2)

    def visit_if_else(self, element, expr, command1, command2):
        if isinstance(expr, Constant):
            if expr.value:
                return command1
            return command2
        return IfElseCommand(expr=expr, command1=command1, command2=command2)