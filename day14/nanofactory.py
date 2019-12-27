import math
import multiprocessing
import collections

import logging
logger = logging.getLogger("nanofactory")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class NanoFactoryChem:
    def __init__(self, count, name):
        self.count = count
        self.name = name

    def __repr__(self):
        return "{} {}".format(self.count, self.name)


class NanoFactoryRule:
    def __init__(self, rulestr):
        self.parse(rulestr)

    def parse(self, rulestr):
        parse_state = 0
        self.inputs = []
        self.output = None
        chem_count = None
        for token in rulestr.split(' '):
            if parse_state == 0:
                # get input chem number
                chem_count = int(token)
                parse_state = 1
            elif parse_state == 1:
                # get input chem name
                name = token
                nextstate = 2
                if name.endswith(','):
                    name = name[:-1]
                    nextstate = 0
                chem = NanoFactoryChem(chem_count, name)
                self.inputs.append(chem)
                parse_state = nextstate
            elif parse_state == 2:
                assert token == '=>'
                parse_state = 3
            elif parse_state == 3:
                # get output chem number
                chem_count = int(token)
                parse_state = 4
            elif parse_state == 4:
                name = token
                chem = NanoFactoryChem(chem_count, name)
                self.output = chem
                return

    def __repr__(self):
        input_strs = []
        for i in self.inputs:
            input_strs.append(str(i))
        return ", ".join(input_strs) + " => {}".format(self.output)



class NanoFactory:
    def __init__(self, filename):
        self.load(filename)

    def load(self, filename):
        self.rules = {}
        with open(filename) as f:
            line = f.readline().strip()
            while len(line) > 0:
                rule = NanoFactoryRule(line)
                self.rules[rule.output.name] = rule
                line = f.readline().strip()

    def __repr__(self):
        s = ""
        for r in self.rules:
            s += str(r) + "\n"
        return s


    def produce(self, chem_number, chem_name):
        supply = collections.defaultdict(int)
        orders = multiprocessing.SimpleQueue()
        orders.put(NanoFactoryChem(1, 'FUEL'))
        ore_needed = 0
        while not orders.empty():
            order = orders.get()
            if order.name == 'ORE':
                ore_needed += order.count
            elif order.count <= supply[order.name]:
                supply[order.name] -= order.count
            else:
                amount_needed = order.count - supply[order.name]
                recipe = self.rules[order.name]
                batches = math.ceil(amount_needed / recipe.output.count)
                for ingredient in recipe.inputs:
                    orders.put(NanoFactoryChem(ingredient.count * batches, ingredient.name))
                leftover_amount = recipe.output.count * batches - amount_needed
                supply[order.name] = leftover_amount
        return ore_needed


