import fft
import sys

filename = sys.argv[1]
f = fft.FFT(filename, 10000)
print(f.process(100))
