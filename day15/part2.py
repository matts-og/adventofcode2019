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
print(bot.find_oxygen_fill_time())
intcode_computer.terminate()
intcode_computer.join()

