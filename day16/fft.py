import math

import logging
logger = logging.getLogger("fft")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


PATTERN_SEED = [0, 1, 0, -1]


class FFT:
    def __init__(self, filename, repeat=1):
        self.input = []
        with open(filename) as f:
            buf = f.read(1024).strip()
            while len(buf) > 0:
                new_elements = [int(x) for x in buf]
                self.input += new_elements
                buf = f.read(1024).strip()
        new_input = []
        for _ in range(0, repeat):
            new_input += self.input
        self.input = new_input
        # message offset is integer represented by the first 7 digits
        if repeat == 1:
            self.message_offset = 0
        else:
            self.message_offset = int("".join([str(x) for x in self.input[0:7]]))

    def process(self, phases):
        logger.debug("process phases = {}".format(phases))
        # prepare an array to cache results for elements in phases
        self.results = []  # [phase][element]
        self.results.append(self.input)
        for phase in range(1, phases+1):
            self.results.append([0] * len(self.input))
        logger.debug("Starting main loop")
        # each element is only dependent on the elements that come after it so 
        # if we work backwards, we can calculate all the phases for an element
        # reusing the results as we go. Also we can stop as soon as we get to
        # the message offset
        progress = []
        progress_check_mod = int((len(self.input) - self.message_offset) / 100)
        for element in reversed(range(self.message_offset, len(self.input))):
            for phase in range(1, phases+1):
                val = 0
                for idx in range(element, len(self.input)):
                    val += self.results[phase-1][idx] * self.get_pattern(element, idx)
                self.results[phase][element] = abs(val) % 10
            if element % progress_check_mod == 0:
                percent_done = 100 - math.floor((element - self.message_offset) 
                                            / (len(self.input) - self.message_offset)
                                            * 100)
                if len(progress) < percent_done:
                    logger.debug("Progress {} %".format(percent_done))
                    progress.append(percent_done)

        return "".join([str(x) for x in self.results[phases][self.message_offset:self.message_offset+8]])

    def slow_process(self, phases):
        self.gen_patterns()
        for _ in range(0, phases):
            new_phase = []
            for outidx in range(0, len(self.input)):
                output = 0
                for idx in range(0, len(self.input)):
                    output += self.input[idx] * self.patterns[outidx][idx]
                new_phase.append(abs(output) % 10)
            self.input = new_phase
        return "".join([str(x) for x in self.input[self.message_offset:self.message_offset+8]])

    def get_pattern(self, element, idx):
        return PATTERN_SEED[math.floor(idx/(element + 1)) + 1]

    def gen_patterns(self):
        logger.debug("gen_patterns")
        self.patterns = []
        for element in range(0, len(self.input)):
            pattern = []
            while len(pattern) < len(self.input) + 1:
                for p in [0, 1, 0, -1]:
                    pattern += [p] * (element + 1)
            self.patterns.append(pattern[1:len(self.input)+1])
