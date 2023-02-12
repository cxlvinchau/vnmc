from vnmc.logics.ltl import X, AP, G, Implies
from vnmc.model_checking.ltl_model_checking import model_check_ltl
from vnmc.timp.parser import imp_parser, TIMPTransformer

with open("source.txt", "r") as f:
    program_str = "".join(f.readlines())

module = TIMPTransformer().transform(imp_parser.parse(program_str))

phi = G(Implies(AP("a"), X(AP("b"))))

result, cex = model_check_ltl(module=module, phi=phi)

print(f"Model checking result: {result}")

if not result:
    for config in cex:
        print(str(config))