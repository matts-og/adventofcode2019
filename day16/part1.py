import fft
import sys

filename = sys.argv[1]
f = fft.FFT(filename)
res = f.process(100)
print("".join([str(x) for x in res[0:8]]))
