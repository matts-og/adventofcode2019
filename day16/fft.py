class FFT:
    def __init__(self, filename):
        self.input = []
        with open(filename) as f:
            buf = f.read(1024).strip()
            while len(buf) > 0:
                new_elements = [int(x) for x in buf]
                self.input += new_elements
                buf = f.read(1024).strip()

    def process(self, phases):
        self.gen_patterns()
        for _ in range(0, phases):
            new_phase = []
            for outidx in range(0, len(self.input)):
                output = 0
                for idx in range(0, len(self.input)):
                    output += self.input[idx] * self.patterns[outidx][idx]
                new_phase.append(abs(output) % 10)
            self.input = new_phase
        return "".join([str(x) for x in self.input[0:8]])

    def gen_patterns(self):
        self.patterns = []
        for element in range(0, len(self.input)):
            pattern = []
            while len(pattern) < len(self.input) + 1:
                for p in [0, 1, 0, -1]:
                    pattern += [p] * (element + 1)
            self.patterns.append(pattern[1:len(self.input)+1])
