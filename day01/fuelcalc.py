import math

fuelsum = 0
with open('input.txt') as f:
    for line in f:
        mass = float(line)
        fuel = math.floor(mass / 3.0) - 2
        fuelsum += fuel
        print("fuel: {},\tsum: {}".format(fuel, fuelsum))
