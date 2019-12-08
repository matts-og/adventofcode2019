import sys
import math


def get_input():
    return int(input("> "))


def output(n):
    print(n)


def get_mode(modes, position):
    return math.floor(modes / pow(10, position)) % 10


def read_value(program, idx, mode):
    param = program[idx]
    if mode == 0:
        # positional mode
        return program[param]
    elif mode == 1:
        # immediate mode
        return param
    else:
        raise "Invalid mode"


with open(sys.argv[1]) as f:
    program = [int(x) for x in f.readline().split(',')]
    idx = 0
    while program[idx] != 99:
        opcode = program[idx] % 100
        param_modes = math.floor(program[idx] / 100)
        idx += 1
        if opcode == 1 or opcode == 2:
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            value1 = read_value(program, idx + 1, get_mode(param_modes, 1))
            output_idx = program[idx + 2]
            assert get_mode(param_modes, 2) == 0, "Parameters that an instruction writes to will never be in immediate mode"
            idx += 3
            if opcode == 1:
                # add
                program[output_idx] = value0 + value1
            else:
                # multiply
                program[output_idx] = value0 * value1
        elif opcode == 3:
            # input
            output_idx = program[idx]
            idx += 1
            program[output_idx] = get_input()
        elif opcode == 4:
            #output
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            idx += 1
            output(value0)
        elif opcode == 5:
            # jump-if-true
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            value1 = read_value(program, idx + 1, get_mode(param_modes, 1))
            idx += 2
            if value0 != 0:
                idx = value1
        elif opcode == 6:
            # jump-if-false
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            value1 = read_value(program, idx + 1, get_mode(param_modes, 1))
            idx += 2
            if value0 == 0:
                idx = value1
        elif opcode == 7:
            # less than
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            value1 = read_value(program, idx + 1, get_mode(param_modes, 1))
            output_idx = program[idx + 2]
            # if the first parameter is less than the second parameter,
            if value0 < value1:
                # it stores 1 in the position given by the third parameter.
                program[output_idx] = 1
            else:
                # Otherwise, it stores 0
                program[output_idx] = 0
            idx += 3
        elif opcode == 8:
            # equals
            value0 = read_value(program, idx, get_mode(param_modes, 0))
            value1 = read_value(program, idx + 1, get_mode(param_modes, 1))
            output_idx = program[idx + 2]
            # if the first parameter is equal to the second parameter,
            if value0 == value1:
                # it stores 1 in the position given by the third parameter.
                program[output_idx] = 1
            else:
                # Otherwise, it stores 0
                program[output_idx] = 0
            idx += 3
        else:
            raise "Unknown opcode"

