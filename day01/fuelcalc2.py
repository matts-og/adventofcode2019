import math

def fuel_fuel(fuel):
    new_fuel = math.floor(fuel / 3.0) - 2
    if new_fuel <= 0:
        return 0
    else:
        return new_fuel + fuel_fuel(new_fuel)

fuelsum = 0
with open('input.txt') as f:
    for line in f:
        mass = float(line)
        fuel = math.floor(mass / 3.0) - 2
        fuelsum += fuel + fuel_fuel(fuel)
    print("fuel sum: {}".format(fuelsum))
