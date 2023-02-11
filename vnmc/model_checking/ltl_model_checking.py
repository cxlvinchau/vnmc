from vnmc.automata.automaton import ProductGBA
from vnmc.graph.graph_algorithms import tarjan
from vnmc.ltl.syntax import LTLFormula, AtomicPropositionLTL
from vnmc.ltl.utils import ltl_to_gba, compute_closure
from vnmc.timp.module import Module
from vnmc.timp.preprocessing import AnnotationCollector
from vnmc.timp.utils import timp_to_gba


def model_check(module: Module, phi: LTLFormula):
    """
    Checks whether the module statisfies the LTL formula

    Parameters
    ----------
    module: Module
        The model to be verified
    phi: LTLFormula
        The formula to be satisfied

    Returns
    -------

    """
    module_aps = [AtomicPropositionLTL(a) for a in module.command.accept_visitor(AnnotationCollector())]
    phi_aps = [ap for ap in compute_closure(phi) if isinstance(ap, AtomicPropositionLTL)]

    if not set(phi_aps).issubset(module_aps):
        raise ValueError("The atomic propositions in the LTL formula have to be part of the modules annotations")

    module_gba = timp_to_gba(module)
    neg_phi_gba = ltl_to_gba(phi.negate(), atomic_propositions=list(module_aps))

    product = ProductGBA(gba1=module_gba, gba2=neg_phi_gba)
    product.create_single_initial_state()

    print(module_gba.to_dot(letter_formatter=lambda l: "{" + ", ".join(map(str, l)) + "}"))
    print()
    print(neg_phi_gba.to_dot(letter_formatter=lambda l: "{" + ", ".join(map(str, l)) + "}"))
    print()
    print(product.to_dot(letter_formatter=lambda l: "{" + ", ".join(map(str, l)) + "}"))

    sccs = tarjan(product, product.get_initial_state())

    if len(sccs) > 0 and len(neg_phi_gba.accepting_state_sets) == 0:
        return False

    for scc in sccs:
        states = [s.props["p"] for s in scc]
        for accepting_set in neg_phi_gba.accepting_state_sets:
            if len(accepting_set.intersection(states)) > 0:
                return False

    return True