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

    def pretty(self):
        return f"{'='*30}\n{self.command.pretty()}\n{'-'*30}\n{str(self.state)}\n{'='*30}"

    def __eq__(self, other):
        if isinstance(other, Configuration):
            return other.command == self.command and other.state == self.state
        return False

    def __hash__(self):
        return hash(self.command)


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

    @abc.abstractmethod
    def visit_repeat(self, element, command):
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

    @abc.abstractmethod
    def get_annotations(self, state: Dict[Variable, bool]):
        pass


class SkipCommand(Command):

    def accept_visitor(self, visitor: CommandVisitor):
        return visitor.visit_skip(self)

    def pretty(self, depth=0) -> str:
        return depth * "  " + "skip"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        return [Configuration(command=self, state=copy.copy(state))]

    def __eq__(self, other):
        return isinstance(other, SkipCommand) and other.annotations == self.annotations

    def __hash__(self):
        return hash(frozenset(self.annotations))

    def get_annotations(self, state: Dict[Variable, bool]):
        return self.annotations


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
        return depth * "  " + f"{self.variable.pretty()} = {self.expr.pretty()}"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        succ = copy.copy(state)
        succ[self.variable] = self.expr.accept(ExpressionEvaluator(state))
        return [Configuration(command=SkipCommand(), state=succ)]

    def __eq__(self, other):
        if isinstance(other, AssignmentCommand):
            return other.variable == self.variable and other.expr == self.expr and other.annotations == self.annotations
        return False

    def __hash__(self):
        return hash(self.variable) + hash(self.expr)

    def get_annotations(self, state: Dict[Variable, bool]):
        return self.annotations


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
            return self.command2.get_successors(state)
        command1_successors = self.command1.get_successors(state)
        successors = []
        for config in command1_successors:
            if isinstance(config.command, SkipCommand):
                command = self.command2
            else:
                command = SequentialCompositionCommand(command1=config.command, command2=self.command2)
            successors.append(Configuration(command, config.state))
        return successors

    def get_annotations(self, state: Dict[Variable, bool]):
        return self.command1.get_annotations(state).union(self.annotations)

    def __eq__(self, other):
        if isinstance(other, SequentialCompositionCommand):
            return other.command1 == self.command1 and other.command2 == self.command2 and \
                other.annotations == self.annotations
        return False

    def __hash__(self):
        return hash(self.command1) + hash(self.command2)


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
        return depth * "  " + f"if {self.expr.pretty()} then\n{self.command1.pretty(depth=depth + 1)}\n" \
                              f"{depth * '  '}else\n{self.command2.pretty(depth=depth + 1)}\n{depth * '  '}endif"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        if self.expr.accept(ExpressionEvaluator(state)):
            return self.command1.get_successors(state)
        return self.command2.get_successors(state)

    def __eq__(self, other):
        if isinstance(other, IfElseCommand):
            return other.expr == self.expr and other.command1 == self.command1 and other.command2 == self.command2 and\
                self.annotations == other.annotations
        return False

    def __hash__(self):
        return hash(self.expr) + hash(self.command1) + hash(self.command2)

    def get_annotations(self, state: Dict[Variable, bool]):
        if self.expr.accept(ExpressionEvaluator(state)):
            return self.command1.get_annotations(state)
        return self.command2.get_annotations(state)


class RepeatCommand(Command):

    def __init__(self, command: Command):
        super().__init__()
        self.command = command

    def accept_visitor(self, visitor: CommandVisitor):
        command = self.command.accept_visitor(visitor)
        return visitor.visit_repeat(self, command)

    def pretty(self, depth=0) -> str:
        return f"{depth*' '}repeat\n{self.command.pretty(depth=depth+1)}\n{depth*'  '}endrepeat"

    def get_successors(self, state: Dict[Variable, bool]) -> List[Configuration]:
        unfolding = SequentialCompositionCommand(command1=self.command, command2=RepeatCommand(self.command))
        return unfolding.get_successors(state)

    def __eq__(self, other):
        if isinstance(other, RepeatCommand):
            return other.command == self.command and other.annotations == self.annotations
        return False

    def __hash__(self):
        return hash(self.command) + 1

    def get_annotations(self, state: Dict[Variable, bool]):
        return self.command.get_annotations(state).union(self.annotations)

