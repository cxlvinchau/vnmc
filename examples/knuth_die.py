import numpy as np

from vnmc.common.graph_algorithms import graph_to_dot
from vnmc.logics.pctl.pctl_factory import P, X, AP, U
from vnmc.model_checking.pctl_model_checking import model_check_pctl
from vnmc.probabilistic import DTMC
import time

dtmc = DTMC()

# Create states
s0 = dtmc.create_state("s0", atomic_propositions=set([AP("a")]))
s123 = dtmc.create_state("s123", reward=1, atomic_propositions=set([AP("a")]))
s23 = dtmc.create_state("s23", atomic_propositions=set([AP("a")]))
s123_prime = dtmc.create_state("s123_prime", atomic_propositions=set([AP("a")]))
s456 = dtmc.create_state("s456", reward=1, atomic_propositions=set([AP("b")]))
s456_prime = dtmc.create_state("s456_prime")
s45 = dtmc.create_state("s56")
s = dict()
for outcome in range(1, 7):
    s[outcome] = dtmc.create_state(name=f"s{outcome}", atomic_propositions=set([AP("t")]))

# Create transitions
dtmc.create_transition(s0, 0.5, s123)
dtmc.create_transition(s0, 0.5, s456)
dtmc.create_transition(s123, 0.5, s123_prime)
dtmc.create_transition(s123, 0.5, s23)
dtmc.create_transition(s456, 0.5, s456_prime)
dtmc.create_transition(s456, 0.5, s45)
dtmc.create_transition(s123_prime, 0.5, s123)
dtmc.create_transition(s123_prime, 0.5, s[1])
dtmc.create_transition(s456_prime, 0.5, s456)
dtmc.create_transition(s456_prime, 0.5, s[6])
dtmc.create_transition(s23, 0.5, s[2])
dtmc.create_transition(s23, 0.5, s[3])
dtmc.create_transition(s45, 0.5, s[4])
dtmc.create_transition(s45, 0.5, s[5])
for outcome in range(1, 7):
    dtmc.create_transition(s[outcome], 1, s[outcome])

dtmc.build(engine="dense")

print(graph_to_dot(dtmc, s0))

distribution = dtmc.compute_transient_distribution({s0: 1}, t=100)
print(distribution)

rewards = dtmc.compute_expected_reward(set(s.values()))
print(rewards)

phi = P(U(AP("a"), AP("t")), 0.5, 1)
print(phi)

result = model_check_pctl(model=dtmc, phi=phi, state=s0)
print(f"PCTL model checking result: {result}")