import sys
import game_renderer
import intcode
import player

filename = sys.argv[1]

player = player.Follower()
game = game_renderer.GameRenderer(player)
p = intcode.Intcode(filename)
p.program[0] = 2
p.run(game, game)
