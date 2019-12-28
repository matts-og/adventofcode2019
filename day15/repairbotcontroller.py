from grid import Grid
from collections import defaultdict

import logging
logger = logging.getLogger("repairbotcontroller")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def coord_to_str(coord):
    return "{},{}".format(coord[0], coord[1])

def str_to_coord(s):
    return [int(x) for x in s.split(",")]

class RepairBotController:
    def __init__(self, movements, statuses):
        self.movements = movements
        self.statuses = statuses
        self.grid = Grid(-1)
        self.row = 0
        self.col = 0

    def find_oxygen(self):
        self.grid.put(self.row, self.col, 1)
        self.unexplored = []
        done = False
        while not done:
            mvmt, new_row, new_col = self.find_oxygen_move()
            self.movements.put(mvmt)
            status = self.statuses.get()
            if status == 0:
                # hit a wall
                self.grid.put(new_row, new_col, 0)
            elif status == 1:
                # moved
                self.grid.put(new_row, new_col, 1)
                self.row = new_row
                self.col = new_col
            elif status == 2:
                # moved, found oxygen
                self.grid.put(new_row, new_col, 2)
                self.row = new_row
                self.col = new_col
                done = True
            else:
                raise "Unknown status {}".format(status)
            logger.debug(self.grid_to_str())

    def find_oxygen_move(self):
        north = (1, self.row - 1, self.col)
        south = (2, self.row + 1, self.col)
        west = (3, self.row, self.col - 1)
        east = (4, self.row, self.col + 1)
        can_go = []
        for mvmt in [north, south, east, west]:
            grid_status = self.grid.get(mvmt[1], mvmt[2])
            if grid_status == -1:
                can_go.append(mvmt)
                if len(can_go) > 1:
                    # Make a list of coordinates we'll come back to later if we get to a dead end
                    self.unexplored.append((mvmt[1], mvmt[2]))
        if len(can_go) > 0:
            return can_go.pop(0)
        else:
            self.path = self.nav_to(self.unexplored.pop())
            return self.path_next()

    def nav_to(self, target):
        self.nav_target = target
        start =  coord_to_str((self.row, self.col))
        # The set of discovered nodes that may need to be (re-)expanded.
        # Initially, only the start node is known.
        open_set = [start]

        # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from
        # start to n currently known.
        came_from = {}

        # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
        g_score = defaultdict(lambda: 1e10)
        g_score[start] = 0

        # For node n, fScore[n] := gScore[n] + h(n).
        f_score = defaultdict(lambda: 1e10)
        f_score[start] = self.astar_heuristic(str_to_coord(start))

        while len(open_set) > 0:
            #current = the node in openSet having the lowest fScore[] value
            current = None
            for n in open_set:
                if current == None or f_score[n] < current:
                    current = n
            if current == coord_to_str(self.nav_target):
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            for n_coord in self.neighbors(str_to_coord(current)):
                n = coord_to_str(n_coord)
                # d(current,n) is the weight of the edge from current to neighbor
                # tentative_gScore is the distance from start to the neighbor through current
                tentative_g_score = g_score[current] + self.distance(current, n)
                if tentative_g_score < g_score[n]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[n] = current
                    g_score[n] = tentative_g_score
                    f_score[n] = g_score[n] + self.astar_heuristic(n_coord)
                    if not n in open_set:
                        open_set.append(n)
        return [] # path not found

    def astar_heuristic(self, coord):
        # squared absolute distance from target
        a = self.nav_target[0] - coord[0]
        b = self.nav_target[1] - coord[1]
        return a * a + b * b

    def neighbors(self, current):
        north = (current[0] - 1, current[1])
        south = (current[0] + 1, current[1])
        west = (current[0], current[1] - 1)
        east = (current[0], current[1] + 1)
        res = []
        for mvmt in [north, south, east, west]:
            if self.grid.get(mvmt[0], mvmt[1]) > 0:
                res.append(mvmt)
        return res

    def distance(self, a, b):
        return 1

    def reconstruct_path(self, came_from, current):
        total_path = [str_to_coord(current)]
        while current in came_from:
            current = came_from[current]
            total_path = [str_to_coord(current)] + total_path
        return total_path

    def path_next(self):
        n = self.path.pop(0)
        d = None
        if self.row - n[0] == 1:
            d = 1  # north
        elif self.row - n[0] == -1:
            d = 2  # south
        elif self.col - n[1] == 1:
            d = 3  # west
        elif self.col - n[1] == -1:
            d = 4  # east
        else:
            raise "Got lost"
        return (d, n[0], n[1])

    def get_grid(self):
        return self.grid

    def grid_to_str_point(self, data, row, col, value):
        if row != self.grid_to_str_prev_row:
            self.grid_str += "\n"
        if row == self.row and col == self.col:
            # Paint cursor
            self.grid_str += "D"
        else:
            if value == -1:
                self.grid_str += " "
            elif value == 0:
                self.grid_str += "#"
            elif value == 1:
                self.grid_str += "."
            elif value == 2:
                self.grid_str += "o"
            else:
                assert "Unexpected value in grid: {}".format(value)
        self.grid_to_str_prev_row = row

    def grid_to_str(self):
        self.grid_str = ""
        self.grid_to_str_prev_row = None
        self.grid.visit(self.grid_to_str_point, None)
        return self.grid_str

