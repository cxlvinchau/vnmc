from vnmc.graph.graph_algorithms import tarjan
from vnmc.ltl.utils import LTLFormatter, LTLClosure, compute_closure, compute_subformulae, compute_elementary_sets, \
    Until, X, And, AP, Neg, Or, ltl_to_gba, F, Implies, G

phi = Until(And(AP("a"), AP("b")), X(Neg(AP("c"))))
phi = Until(AP("a"), AP("b"))
phi = X(AP("a"))
phi = G(Implies(AP("a"), X(AP("b")))).negate()

print(phi.accept(LTLFormatter()))

gba = ltl_to_gba(phi)
gba.create_single_initial_state()
# print(gba.accepting_state_sets)
sccs, pred = tarjan(gba, gba.get_initial_state())
for scc in sccs:
    print(scc)
# print(gba.to_dot(letter_formatter=lambda l: "{" + ", ".join(map(str, l)) + "}"))

