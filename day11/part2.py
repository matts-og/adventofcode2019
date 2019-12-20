import sys
import painterbot
import intcode


filename = sys.argv[1]
bot = painterbot.PainterBot()
bot.get_grid().put(0,0,1)
intcode.run(filename, "main", bot, bot)
print(bot.grid_to_str())