import sys
import repairbotcontroller
import intcode
import multiprocessing

#import logging
#logging.getLogger("repairbotcontroller").setLevel(logging.DEBUG)

filename = sys.argv[1]
program = intcode.Intcode(filename)
movements = multiprocessing.SimpleQueue()
statuses = multiprocessing.SimpleQueue()
intcode_computer = multiprocessing.Process(target=program.run, args=(movements, statuses))
intcode_computer.start()
bot = repairbotcontroller.RepairBotController(movements, statuses)
print(len(bot.find_oxygen_best_path()))
intcode_computer.terminate()
intcode_computer.join()

