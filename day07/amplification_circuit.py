import sys
import math


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


def run_program(filename, inputs):
    outputs = []
    with open(filename) as f:
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
                program[output_idx] = inputs.pop(0)
                #print("Input: {} -> {}".format(program[output_idx], output_idx))
            elif opcode == 4:
                #output
                value0 = read_value(program, idx, get_mode(param_modes, 0))
                idx += 1
                outputs.append(value0)
                #print("Output: {}".format(value0))
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
    return outputs


def run_amplifier(filename, phase_setting, inputval):
    outputs = run_program(filename, [phase_setting, inputval])
    return outputs[0]


def run_amplifiers(filename, phase_settings):
    inputval = 0
    for phase_setting in phase_settings:
        outputval = run_amplifier(filename, phase_setting, inputval)
        inputval = outputval
    return outputval


def base5todec(n):
    remainder = n
    result = 0
    position = 0
    while len(remainder) > 0:
        d = remainder[-1]
        v = d * pow(5, position)
        result += v
        position += 1
        remainder = remainder[:-1]
    return result


def dectobase5(n):
    remainder = n
    result = []
    position = 0
    while remainder:
        d = remainder % 5
        result = [d] + result
        position += 1
        remainder = math.floor( remainder / 5)
    return result


def pad_base5(n, pad):
    return [0]*(pad-len(n)) + n


def get_combinations(a):
    if len(a) == 1:
        yield a
    else:
        for n in a:
            tail = [ x for x in a if x != n ]
            for b in get_combinations(tail):
                yield [n] + b

filename = sys.argv[1]

max_signal = None
best_phase_settings = None
available_phases = [0, 1, 2, 3, 4]
for phase_settings in get_combinations(available_phases):
    signal = run_amplifiers(filename, phase_settings)
    if max_signal == None or signal > max_signal:
        max_signal = signal
        best_phase_settings = phase_settings
    print("{}, {}, {}, {}".format(phase_settings, signal, max_signal, best_phase_settings))
print(max_signal)
print(best_phase_settings)
