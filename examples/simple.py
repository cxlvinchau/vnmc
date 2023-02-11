from vnmc.automata.automaton import ProductGBA
from vnmc.graph.graph_algorithms import tarjan
from vnmc.ltl.utils import X, AP, ltl_to_gba, Until, Neg
from vnmc.model_checking.ltl_model_checking import model_check
from vnmc.timp.parser import imp_parser, TIMPTransformer
from vnmc.timp.preprocessing import VariableCollector, Simplifier, Linearizer
from vnmc.timp.utils import timp_to_gba

with open("source.txt", "r") as f:
    program_str = "".join(f.readlines())

module = TIMPTransformer().transform(imp_parser.parse(program_str))

phi = X(AP("a"))

result = model_check(module=module, phi=phi)

print(f"Model checking result: {result}")