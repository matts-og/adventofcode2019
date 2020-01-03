import fft
import sys

import logging
logging.getLogger("fft").setLevel(logging.DEBUG)

filename = sys.argv[1]
f = fft.FFT(filename, 10000)
print(f.process(100))
