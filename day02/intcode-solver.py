import sys

def run(filename, noun, verb):
    with open(filename) as f:
        program = [int(x) for x in f.readline().split(',')]
        idx = 0
        program[1] = noun
        program[2] = verb
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
    return program[0]

assert len(sys.argv) >= 3
target = int(sys.argv[2])
for noun in range(0,100):
    for verb in range(0, 100):
        if run(sys.argv[1], noun, verb) == target:
            print(noun * 100 + verb)
            break
