import sys
import math
import multiprocessing


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


def run_intcode(filename, threadname, inputbuf, outputbuf):
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
                    # opcode == 2
                    # multiply
                    program[output_idx] = value0 * value1
            elif opcode == 3:
                # input
                output_idx = program[idx]
                idx += 1
                program[output_idx] = inputbuf.get()
                #print("[{}] Input: {} -> {}".format(threadname, program[output_idx], output_idx))
            elif opcode == 4:
                #output
                value0 = read_value(program, idx, get_mode(param_modes, 0))
                idx += 1
                outputbuf.put(value0)
                #print("[{}] Output: {}".format(threadname, value0))
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


def run_amplifier(filename, amplifier_name, inputbuf, outputbuf):
    p = multiprocessing.Process(target=run_intcode,
        args=(filename, amplifier_name, inputbuf, outputbuf),
        name=amplifier_name)
    p.start()
    return p


def run_amplifiers(filename, phase_settings):
    num_amplifiers = len(phase_settings)
    amplifiers = []
    # initialise buffers with phase settings
    buffers = []
    for idx in range(0,num_amplifiers):
        buf = multiprocessing.SimpleQueue()
        buf.put(phase_settings[idx])
        buffers.append(buf)

    for idx in range(0,num_amplifiers):
        amplifier_name = chr(ord('A') + idx)
        input_buf = buffers[idx]
        if idx == num_amplifiers - 1:
            # output of last amplifier is fed back to first amplifier
            output_buf = buffers[0]
        else:
            output_buf = buffers[idx + 1]
        amplifiers.append(run_amplifier(filename, amplifier_name, input_buf, output_buf))
    # start input
    buffers[0].put(0)
    for a in amplifiers:
        a.join()
    #print("Amplifiers done")
    return buffers[0].get()


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
available_phases = [5, 6, 7, 8, 9]
for phase_settings in get_combinations(available_phases):
    signal = run_amplifiers(filename, phase_settings)
    if max_signal == None or signal > max_signal:
        max_signal = signal
        best_phase_settings = phase_settings
    #print("{}, {}, {}, {}".format(phase_settings, signal, max_signal, best_phase_settings))
print(max_signal)
print(best_phase_settings)
