import numpy as np

from vnmc.common.graph_algorithms import graph_to_dot
from vnmc.probabilistic.dtmc import DTMC
import time

dtmc = DTMC()

# Create states
s0 = dtmc.create_state("s0")
s123 = dtmc.create_state("s123")
s23 = dtmc.create_state("s23")
s123_prime = dtmc.create_state("s123_prime")
s456 = dtmc.create_state("s456")
s456_prime = dtmc.create_state("s456_prime")
s45 = dtmc.create_state("s56")
s = dict()
for outcome in range(1, 7):
    s[outcome] = dtmc.create_state(name=f"s{outcome}")

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

dtmc.build(engine="dense-numba")


start = time.time()
distribution = dtmc.compute_transient_distribution({s0: 1}, t=10000000)
end = time.time()
print(distribution)
print(f"{end-start} seconds")