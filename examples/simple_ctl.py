from vnmc.logics.ctl.ctl_factory import AG, Implies, AP, AX
from vnmc.model_checking.ctl_model_checking import model_check_ctl
from vnmc.timp.parser import imp_parser, TIMPTransformer

with open("source.txt", "r") as f:
    program_str = "".join(f.readlines())

module = TIMPTransformer().transform(imp_parser.parse(program_str))

phi = AG(Implies(AP("a"), AX(AP("b"))))

print(phi)

print(f"CTL model checking result: {model_check_ctl(module=module, phi=phi)}")