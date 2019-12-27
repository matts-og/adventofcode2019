import math

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

    def produce_recurse(self, chem_number, chem_name, required_chems, surplus_chems):
        if chem_name == 'ORE':
            return
        logger.debug("Produce {} {}".format(chem_number, chem_name))
        assert chem_name in self.rules
        r = self.rules[chem_name]
        logger.debug("Rule: {}".format(r))
        multiplier = math.floor(chem_number / r.output.count)
        if chem_number % r.output.count != 0:
            multiplier += 1
        logger.debug("Multiplier = {}".format(multiplier))
        for i in r.inputs:
            require = i.count * multiplier
            logger.debug("Input: {} require {}".format(i.name, require))
            if i.name in surplus_chems and surplus_chems[i.name] > 0:
                surplus = surplus_chems[i.name]
                if surplus > require:
                    require = 0
                    surplus_chems[i.name] -= require
                else:
                    require -= surplus
                    surplus_chems[i.name] = 0
                logger.debug("Found {} in surplus".format(surplus))
                logger.debug("Surplus for {} is now {}".format(i.name, surplus_chems[i.name]))
            if require > 0:
                if not i.name in required_chems:
                    required_chems[i.name] = require
                else:
                    required_chems[i.name] += require
                self.produce_recurse(require, i.name, required_chems, surplus_chems)
        output_surplus = 0
        if chem_number % r.output.count != 0:
            output_surplus = r.output.count * multiplier - chem_number
            logger.debug("{} output_surplus = {}".format(r.output.name, output_surplus))
            if not r.output.name in surplus_chems:
                surplus_chems[r.output.name] = output_surplus
            else:
                surplus_chems[r.output.name] += output_surplus

    def produce(self, chem_number, chem_name):
        required_chems = {}
        surplus_chems = {}
        self.produce_recurse(chem_number, chem_name, required_chems, surplus_chems)
        logger.debug("Required chems:")
        logger.debug(required_chems)
        logger.debug("Surplus chems:")
        logger.debug(surplus_chems)
        return required_chems['ORE']

