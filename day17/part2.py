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
s.get_scaffold()
ip.terminate()
ip.join()

s.navigate(iinput)

i = intcode.Intcode(filename)
i.program[0] = 2
ip = multiprocessing.Process(target=i.run, args=(iinput, asciibuf))
ip.start()
print(s.report_space_dust())
ip.terminate()
ip.join()
