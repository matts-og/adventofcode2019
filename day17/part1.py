import sys
import multiprocessing
import queue
import intcode
import scaffolds


import logging
logging.getLogger("scaffolds").setLevel(logging.DEBUG)
#logging.getLogger("grid").setLevel(logging.DEBUG)
#logging.getLogger("intcode").setLevel(logging.DEBUG)


filename = sys.argv[1]

i = intcode.Intcode(filename)
asciibuf = multiprocessing.Queue()
iinput = multiprocessing.Queue()
ip = multiprocessing.Process(target=i.run, args=(iinput, asciibuf))
s = scaffolds.Scaffolds(asciibuf)
ip.start()
print(s.get_calibration())
ip.terminate()
ip.join()
