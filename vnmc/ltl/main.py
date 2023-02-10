from vnmc.ltl.utils import LTLFormatter, LTLClosure, compute_closure, compute_subformulae, compute_elementary_sets, \
    Until, X, And, AP, Neg, Or, ltl_to_gba

phi = Until(And(AP("a"), AP("b")), X(Neg(AP("c"))))
phi = Until(AP("a"), AP("b"))
phi = X(AP("a"))

print(phi.accept(LTLFormatter()))

gba = ltl_to_gba(phi)
print(gba.to_dot(letter_formatter=lambda l: "{" + ", ".join(map(str, l)) + "}"))
