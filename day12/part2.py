import sys
import moon_simulator
import math

#import logging
#logging.getLogger("moon_simulator").setLevel(logging.DEBUG)

filename = sys.argv[1]
moons = moon_simulator.load_moons(filename)
sim = moon_simulator.MoonSimulator(moons)
print(sim.get_period())
