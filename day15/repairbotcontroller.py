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
        self.path = None
        self.oxygen = None
        self.unexplored = set()
        self.grid.put(self.row, self.col, 1)

    def find_oxygen_fill_time(self):
        self.explore(False)
        all_g_scores = defaultdict(lambda: 1e10)
        def func(self, row, col, value):
            if self.grid.get(row, col) < 1:
                # don't bother with unreachable locations
                return
            if not coord_to_str((row, col)) in all_g_scores.keys():
                self.nav(self.oxygen, (row, col), self.astar_neighbors_in_grid, self.astar_arrived_exact)
                all_g_scores.update(self.g_score)
        self.grid.visit(func, self)
        #logger.debug("g_scores = {}".format(all_g_scores))
        max_g = None
        for g in all_g_scores.values():
            if max_g == None or g > max_g:
                max_g = g
        return max_g

    def find_oxygen_best_path(self):
        # use a-star to find the best path from the oxygen to the origin
        self.explore(False)
        res = self.nav(self.oxygen, (0,0), self.astar_neighbors_in_grid, self.astar_arrived_exact)
        logger.debug(self.grid_to_str())
        return res

    def find_oxygen(self):
        self.explore(True)
        assert self.oxygen != None
        logger.debug("Oxygen found ({})".format(coord_to_str(self.oxygen)))

    def explore(self, stop_at_oxygen = True):
        done = False
        while not done:
            mvmt, new_row, new_col = self.explore_move()
            if mvmt == None:
                # We've explored everywhere
                break
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
                self.oxygen = (new_row, new_col)
                done = stop_at_oxygen
            else:
                raise "Unknown status {}".format(status)
            logger.debug(self.grid_to_str())
            logger.debug("position = {}".format(coord_to_str([self.row, self.col])))

    def explore_move(self):
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
                    self.unexplored.add(coord_to_str([mvmt[1], mvmt[2]]))
        res = None
        if len(can_go) > 0:
            res = can_go.pop(0)
            self.path = None
        else:
            if self.path == None and len(self.unexplored) > 0:
                target = self.unexplored.pop()
                self.unexplored.add(target)
                self.path = self.nav((self.row, self.col), str_to_coord(target),
                                        self.astar_neighbors_in_grid,
                                        self.astar_arrived_near_enough)
            res = self.path_next()
        if res[0] != None:
            self.remove_from_unexplored([res[1], res[2]])
        return res

    def nav(self, start_coord, target, neighbors_func, arrived_func):
        # a-star based on wikipedia
        logger.debug("nav_to {}".format(target))
        self.nav_target = target
        start = coord_to_str(start_coord)
        logger.debug("start = {}".format(start))

        # The set of discovered nodes that may need to be (re-)expanded.
        # Initially, only the start node is known.
        open_set = [start]

        # For node n, cameFrom[n] is the node immediately preceding it on the cheapest path from
        # start to n currently known.
        came_from = {}

        # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
        self.g_score = defaultdict(lambda: 1e10)
        self.g_score[start] = 0

        # For node n, fScore[n] := gScore[n] + h(n).
        f_score = {}
        f_score[start] = self.astar_heuristic(str_to_coord(start))

        while len(open_set) > 0:
            #current = the node in openSet having the lowest fScore[] value
            current = None
            for n in open_set:
                if not n in f_score:
                    f_score[n] = self.g_score[n] + self.astar_heuristic(str_to_coord(n))
                if current == None or f_score[n] < f_score[current]:
                    current = n
            #logger.debug("current = {}".format(current))
            if arrived_func(current):
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            for n_coord in neighbors_func(str_to_coord(current)):
                n = coord_to_str(n_coord)
                # d(current,n) is the weight of the edge from current to neighbor
                # tentative_gScore is the distance from start to the neighbor through current
                tentative_g_score = self.g_score[current] + self.distance(current, n)
                if tentative_g_score < self.g_score[n]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[n] = current
                    self.g_score[n] = tentative_g_score
                    f_score[n] = self.g_score[n] + self.astar_heuristic(n_coord)
                    if not n in open_set:
                        open_set.append(n)
        return [] # path not found

    def remove_from_unexplored(self, coord):
        coord_str = None
        if isinstance(coord, str):
            coord_str = coord
        else:
            coord_str = coord_to_str([coord[0], coord[1]])
        if coord_str in self.unexplored:
            self.unexplored.remove(coord_str)

    def astar_heuristic(self, coord):
        # squared absolute distance from target
        a = self.nav_target[0] - coord[0]
        b = self.nav_target[1] - coord[1]
        return a * a + b * b

    def is_next_to(self, a, b):
        if isinstance(a, str):
            a = str_to_coord(a)
        if isinstance(b, str):
            b = str_to_coord(b)
        row_adjacent = (abs(a[0] - b[0]) == 1) and (a[1] == b[1])
        col_adjacent = (abs(a[1] - b[1]) == 1) and (a[0] == b[0])
        return row_adjacent or col_adjacent

    def astar_neighbors_in_grid(self, current):
        """a-star neighbors function that gets only previously explored items from the grid"""
        north = (current[0] - 1, current[1])
        south = (current[0] + 1, current[1])
        west = (current[0], current[1] - 1)
        east = (current[0], current[1] + 1)
        res = []
        for mvmt in [north, south, east, west]:
            if self.grid.get(mvmt[0], mvmt[1]) > 0:
                res.append(mvmt)
        return res

    def astar_arrived_near_enough(self, current):
        return current == coord_to_str(self.nav_target) or self.is_next_to(current, self.nav_target)

    def astar_neighbors_explore(self, current):
        """a-star neighbors function that explores as it goes"""
        north = (1, current[0] - 1, current[1])
        south = (2, current[0] + 1, current[1])
        west = (3, current[0], current[1] - 1)
        east = (4, current[0], current[1] + 1)
        res = []
        for mvmt in [north, south, east, west]:
            grid_status = self.grid.get(mvmt[1], mvmt[2])
            if grid_status == -1:
                # explore this unknown location
                self.movements.put(mvmt[0])
                grid_status = self.statuses.get()
                self.grid.put(mvmt[1], mvmt[2], grid_status)
                logger.debug("Explored {} -> {}".format(coord_to_str((mvmt[1], mvmt[2])), grid_status))
                if grid_status > 0:
                    # move back so we can check the other neighbors
                    backwards = None
                    if mvmt[0] == 1:
                        backwards = 2
                    elif mvmt[0] == 2:
                        backwards = 1
                    elif mvmt[0] == 3:
                        backwards = 4
                    elif mvmt[0] == 4:
                        backwards = 3
                    else:
                        raise "invalid mvmt {}".format(mvmt)
                    self.movements.put(backwards)
                    _ = self.statuses.get()
            if grid_status > 0:
                res.append((mvmt[1], mvmt[2]))
        return res

    def astar_arrived_exact(self, current):
        return current == coord_to_str(self.nav_target)

    def distance(self, a, b):
        return 1

    def reconstruct_path(self, came_from, current):
        total_path = [str_to_coord(current)]
        while current in came_from:
            current = came_from[current]
            total_path = [str_to_coord(current)] + total_path
        total_path.pop(0)
        #logger.debug("total_path = {}".format(total_path))
        return total_path

    def path_next(self):
        if self.path != None and len(self.path) > 0:
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
        else:
            return (None, None, None)

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

