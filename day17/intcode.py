import sys
import math
import multiprocessing
import logging


logger = logging.getLogger("intcode")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_mode(modes, position):
    return math.floor(modes / pow(10, position)) % 10


def read_idx(program, idx):
    try:
        return program[idx]
    except IndexError:
        return 0


def write_idx(program, idx, value):
    try:
        program[idx] = value
    except IndexError:
        program += [0] * (idx - len(program) + 1)
        program[idx] = value


def read_value(program, idx, mode, relative_base):
    #logger.debug("read_value: idx={}, mode={}, relative_base={}".format(idx, mode, relative_base))
    param = read_idx(program, idx)
    if mode == 0:
        # positional mode
        return read_idx(program, param)
    elif mode == 1:
        # immediate mode
        return param
    elif mode == 2:
        # relative mode
        return read_idx(program, relative_base + param)
    else:
        raise "Invalid mode"


def write_value(value, program, idx, mode, relative_base):
    #logger.debug("write_value: value={}, idx={}, mode={}, relative_base={}".format(value, idx, mode, relative_base))
    assert mode != 1, "Parameters that an instruction writes to will never be in immediate mode"
    param = read_idx(program, idx)
    if mode == 0:
        # positional mode
        write_idx(program, param, value)
    elif mode == 2:
        # relative mode
        write_idx(program, relative_base + param, value)
    else:
        raise "Invalid mode"


class UserInput:
    def get(self):
        return int(input("> "))


class UserOutput:
    def put(self, value):
        print(value)


class Intcode:
    def __init__(self, filename, name = "main"):
        self.load(filename)
        self.name = name

    def load(self, filename):
        with open(filename) as f:
            self.program = [int(x) for x in f.readline().split(',')]

    def run(self, inputbuf, outputbuf):
        idx = 0
        relative_base = 0
        while self.program[idx] != 99:
            opcode = self.program[idx] % 100
            param_modes = math.floor(self.program[idx] / 100)
            idx += 1
            if opcode == 1 or opcode == 2:
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                value1 = read_value(self.program, idx + 1, get_mode(param_modes, 1), relative_base)
                if opcode == 1:
                    # add
                    write_value(value0 + value1, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                else:
                    # opcode == 2
                    # multiply
                    write_value(value0 * value1, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                idx += 3
            elif opcode == 3:
                # input
                write_value(inputbuf.get(), self.program, idx, get_mode(param_modes, 0), relative_base)
                idx += 1
                #print("[{}] Input: {} -> {}".format(threadname, self.program[output_idx], output_idx))
            elif opcode == 4:
                #output
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                outputbuf.put(value0)
                idx += 1
                logger.debug("[{}] Output: {}".format(self.name, value0))
            elif opcode == 5:
                # jump-if-true
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                value1 = read_value(self.program, idx + 1, get_mode(param_modes, 1), relative_base)
                idx += 2
                if value0 != 0:
                    idx = value1
            elif opcode == 6:
                # jump-if-false
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                value1 = read_value(self.program, idx + 1, get_mode(param_modes, 1), relative_base)
                idx += 2
                if value0 == 0:
                    idx = value1
            elif opcode == 7:
                # less than
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                value1 = read_value(self.program, idx + 1, get_mode(param_modes, 1), relative_base)
                # if the first parameter is less than the second parameter,
                if value0 < value1:
                    # it stores 1 in the position given by the third parameter.
                    write_value(1, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                else:
                    # Otherwise, it stores 0
                    write_value(0, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                idx += 3
            elif opcode == 8:
                # equals
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                value1 = read_value(self.program, idx + 1, get_mode(param_modes, 1), relative_base)
                # if the first parameter is equal to the second parameter,
                if value0 == value1:
                    # it stores 1 in the position given by the third parameter.
                    write_value(1, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                else:
                    # Otherwise, it stores 0
                    write_value(0, self.program, idx + 2, get_mode(param_modes, 2), relative_base)
                idx += 3
            elif opcode == 9:
                # Adjust relative base
                value0 = read_value(self.program, idx, get_mode(param_modes, 0), relative_base)
                idx += 1
                relative_base += value0
            else:
                raise "Unknown opcode"
