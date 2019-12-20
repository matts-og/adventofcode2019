import sys
import painterbot
import intcode
import logging

#logging.getLogger("painterbot").setLevel(logging.DEBUG)

filename = sys.argv[1]
bot = painterbot.PainterBot()
intcode.run(filename, "main", bot, bot)
panel_count = [0]
def count_func(data, row, col, val):
    data[0] += (1 if val == 1 or val == 0 else 0)
bot.get_grid().visit(count_func, panel_count)
print(panel_count[0])
