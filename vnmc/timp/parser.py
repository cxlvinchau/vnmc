import lark
from lark import Lark, v_args

from vnmc.timp.command import AssignmentCommand, SkipCommand, IfElseCommand, SequentialCompositionCommand
from vnmc.timp.expr import Constant, Variable, Disjunction, Conjunction, Negation
from vnmc.timp.preprocessing import Linearizer, VariableCollector
from vnmc.timp.module import Module

imp_parser = Lark(r"""
    ?module: "module" name ":" command -> module_def

    ?command: "skip" -> command_skip
            | "if" expr "then" command "else" command "endif" -> command_if_else
            | command "\n" command -> command_seq
            | variable "=" expr -> command_assign
            | "#" WORD " "* "\n" command -> comment_left
            | command "#" WORD -> comment_right
            | command " "*
            | command "@" WORD

    variable : WORD
    ?name: WORD
    
    ?expr: "true" -> expr_true
         | "false" -> expr_false
         | disj
         | "(" expr ")"
         | variable
    
    ?disj: expr "or" expr -> expr_or
         | conj
        
    ?conj: expr "and" expr -> expr_and
         | neg
        
    neg: "!" expr -> expr_neg

    %import common.WORD
    %import common.WS
    %ignore WS

    """, start='module')


@v_args(inline=True)
class TIMPTransformer(lark.Transformer):

    def expr_true(self):
        return Constant(value=True)

    def expr_false(self):
        return Constant(value=False)

    def variable(self, name):
        return Variable(name=name.value)

    def expr_or(self, expr1, expr2):
        return Disjunction(expr1=expr1, expr2=expr2)

    def expr_and(self, expr1, expr2):
        return Conjunction(expr1=expr1, expr2=expr2)

    def expr_neg(self, expr):
        return Negation(expr=expr)

    def command_assign(self, variable, expr):
        return AssignmentCommand(variable=variable, expr=expr)

    def command_skip(self):
        return SkipCommand()

    def command_if_else(self, expr, command1, command2):
        return IfElseCommand(expr=expr, command1=command1, command2=command2)

    def command_seq(self, command1, command2):
        return SequentialCompositionCommand(command1=command1, command2=command2)

    def module_def(self, module_name, command):
        return (module_name.value, command)

    def comment_left(self, comment, command):
        return command

    def comment_right(self, command, comment):
        return command

    def module_def(self, name, command):
        return Module(name=name, command=command)


if __name__ == "__main__":
    tree = imp_parser.parse("module test:\nif x then x = z else y = z endif\nx = z\nx=y")
    transformer = IMPTransformer()
    module = transformer.transform(tree)
    print(module.pretty())
    print(module.command.accept_visitor(VariableCollector()))
