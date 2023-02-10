from vnmc.timp.parser import imp_parser, TIMPTransformer
from vnmc.timp.preprocessing import VariableCollector, Simplifier

with open("source.txt", "r") as f:
    program_str = "".join(f.readlines())

module = TIMPTransformer().transform(imp_parser.parse(program_str))
module.transform(Simplifier())

variables = module.command.accept_visitor(VariableCollector())

state = {v: False for v in variables}

print(state)

print(module.pretty())

module.run(state)