import sys
import moon_simulator
import math

#import logging
#logging.getLogger("moon_simulator").setLevel(logging.DEBUG)

filename = sys.argv[1]
steps = int(sys.argv[2])
moons = moon_simulator.load_moons(filename)
sim = moon_simulator.MoonSimulator(moons)
for s in range(0, steps):
    do_debug = False
    if steps < 10:
        do_debug = True
    elif s % math.floor(steps / 10) == (math.floor(steps / 10) - 1):
        do_debug = True
    sim.step(do_debug)
print(sim.energy())

