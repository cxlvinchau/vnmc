from typing import Dict
from vnmc.timp.command import Command, CommandVisitor, Configuration, SkipCommand
from vnmc.timp.expr import Variable
from vnmc.timp.preprocessing import VariableCollector
from collections import deque


class Module:

    def __init__(self, name: str, command: Command):
        self._name = name
        self._command = command
        self._variables = None

    def pretty(self):
        return f"module {self.name}:\n{self.command.pretty(depth=1)}"

    @property
    def variables(self):
        if self._variables is None:
            self._variables = self._command.accept_visitor(VariableCollector())
        return self._variables

    @property
    def name(self):
        return self._name

    @property
    def command(self):
        return self._command

    def transform(self, visitor: CommandVisitor):
        self._command = self._command.accept_visitor(visitor)

    def run(self, state: Dict[Variable, bool]):
        queue = deque([Configuration(command=self.command, state=state)])
        while queue:
            current = queue.popleft()
            print(current)
            if isinstance(current.command, SkipCommand):
                break
            for succ in current.get_successors():
                queue.append(succ)




