import abc
from typing import Dict, List

from vnmc.timp.expr import Variable, BooleanExpression, ExpressionEvaluator

import copy


class Configuration:

    def __init__(self, command, state):
        self.command = command
        self.state = state

    def get_successors(self) -> List:
        return self.command.get_successors(self.state)

    def __str__(self):
        return f"({type(self.command)}, {str(self.state)})"


class CommandVisitor(abc.ABC):

    def __init__(self, expr_visitor=None):
        self.expr_visitor = expr_visitor

    @abc.abstractmethod
    def visit_skip(self, element):
        pass

    @abc.abstractmethod
    def visit_assignment(self, element, variable, expr):
        pass

    @abc.abstractmethod
    def visit_sequential_composition(self, element, command1, command2):
        pass

    @abc.abstractmethod
    def visit_if_else(self, element, expr, command1, command2):
        pass


class Command(abc.ABC):

    def __init__(self):
        self.annotations = set()

    def accept_visitor(self, visitor: CommandVisitor):
        pass

    @abc.abstractmethod
    def pretty(self, depth=0) -> str:
        pass

    @abc.abstractmethod
    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        pass


class SkipCommand(Command):

    def accept_visitor(self, visitor: CommandVisitor):
        return visitor.visit_skip(self)

    def pretty(self, depth=0) -> str:
        return depth*"  " + "skip"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        return [Configuration(command=self, state=copy.copy(state))]


class AssignmentCommand(Command):

    def __init__(self, variable: Variable, expr: BooleanExpression):
        super().__init__()
        self.variable = variable
        self.expr = expr

    def accept_visitor(self, visitor: CommandVisitor):
        v = self.variable.accept(visitor.expr_visitor) if visitor.expr_visitor is not None else None
        e = self.expr.accept(visitor.expr_visitor) if visitor.expr_visitor is not None else None
        return visitor.visit_assignment(self, v, e)

    def pretty(self, depth=0) -> str:
        return depth*"  " + f"{self.variable.pretty()} = {self.expr.pretty()}"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        succ = copy.copy(state)
        succ[self.variable] = self.expr.accept(ExpressionEvaluator(state))
        return [Configuration(command=SkipCommand(), state=succ)]


class SequentialCompositionCommand(Command):

    def __init__(self, command1: Command, command2: Command):
        super().__init__()
        self.command1 = command1
        self.command2 = command2

    def accept_visitor(self, visitor: CommandVisitor):
        c1, c2 = self.command1.accept_visitor(visitor), self.command2.accept_visitor(visitor)
        return visitor.visit_sequential_composition(self, c1, c2)

    def pretty(self, depth=0) -> str:
        return f"{self.command1.pretty(depth=depth)}" + "\n" + f"{self.command2.pretty(depth=depth)}"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        if isinstance(self.command1, SkipCommand):
            return [Configuration(command=self.command2, state=copy.copy(state))]
        command1_successors = self.command1.get_successors(state)
        successors = []
        for config in command1_successors:
            command = SequentialCompositionCommand(command1=config.command, command2=self.command2)
            successors.append(Configuration(command, config.state))
        return successors


class IfElseCommand(Command):

    def __init__(self, expr: BooleanExpression, command1: Command, command2: Command):
        super().__init__()
        self.expr = expr
        self.command1 = command1
        self.command2 = command2

    def accept_visitor(self, visitor: CommandVisitor):
        e = self.expr.accept(visitor.expr_visitor) if visitor.expr_visitor is not None else None
        c1 = self.command1.accept_visitor(visitor)
        c2 = self.command2.accept_visitor(visitor)
        return visitor.visit_if_else(self, e, c1, c2)

    def pretty(self, depth=0) -> str:
        return depth*"  " + f"if {self.expr.pretty()} then\n{self.command1.pretty(depth=depth+1)}\n" \
                           f"{depth*'  '}else\n{self.command2.pretty(depth=depth+1)}\n{depth*'  '}endif"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        if self.expr.accept(ExpressionEvaluator(state)):
            return [Configuration(command=self.command1, state=copy.copy(state))]
        return [Configuration(command=self.command2, state=copy.copy(state))]
