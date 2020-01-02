import fft
import sys

filename = sys.argv[1]
f = fft.FFT(filename)
print(f.process(100))

