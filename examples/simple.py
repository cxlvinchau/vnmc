from vnmc.timp.parser import imp_parser, TIMPTransformer
from vnmc.timp.preprocessing import VariableCollector, Simplifier, Linearizer

with open("source.txt", "r") as f:
    program_str = "".join(f.readlines())

module = TIMPTransformer().transform(imp_parser.parse(program_str))

linearized = module.command.accept_visitor(Linearizer())

for cmd in linearized:
    print(cmd.annotations)
    print(cmd.pretty())