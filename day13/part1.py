import sys
import game_renderer
import intcode

filename = sys.argv[1]

game = game_renderer.GameRenderer()
p = intcode.Intcode(filename)
p.run(game, game)
block_count_data = [0]
def count_func(data, row, col, val):
    if val == 2:
        data[0] += 1
game.get_grid().visit(count_func, block_count_data)
print(block_count_data[0])
