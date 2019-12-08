import sys

with open(sys.argv[1]) as f:
    program = [int(x) for x in f.readline().split(',')]
    idx = 0
    if len(sys.argv) >= 3:
        program[1] = int(sys.argv[2])
    if len(sys.argv) >= 4:
        program[2] = int(sys.argv[3])
    while program[idx] != 99:
        opcode = program[idx]
        input_idx1 = program[idx + 1]
        input_idx2 = program[idx + 2]
        output_idx = program[idx + 3]
        if opcode == 1:
            program[output_idx] = program[input_idx1] + program[input_idx2]
        elif opcode == 2:
            program[output_idx] = program[input_idx1] * program[input_idx2]
        idx += 4
    print("Result: {}".format(program[0]))

