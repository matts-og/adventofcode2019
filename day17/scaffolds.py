import grid
import queue

import logging
logger = logging.getLogger("scaffolds")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class Scaffolds:
    def __init__(self, inputbuf):
        self.inputbuf = inputbuf


    def get_calibration(self):
        isum = 0
        for intersection in self.get_intersections():
            isum += intersection['row'] * intersection['col']
        return isum


    def get_intersections(self):
        self.get_scaffold()
        def check_coord(data, row, col, val):
            if val == '#' and row > 0 and col > 0:
                if self.grid.get(row - 1, col) == '#' \
                        and self.grid.get(row + 1, col) == '#' \
                        and self.grid.get(row, col - 1) == '#' \
                        and self.grid.get(row, col + 1) == '#':
                    coord = {'row': row, 'col': col}
                    data['intersections'].append(coord)
        data = { 'intersections': [] }
        self.grid.visit(check_coord, data)
        return data['intersections']


    def get_scaffold(self):
        self.grid = grid.Grid()
        row = 0
        col = 0
        try:
            while True:
                ch = chr(self.inputbuf.get(timeout=5))
                if ch == '\n':
                    row += 1
                    col = 0
                else:
                    self.grid.put(row, col, ch)
                    col += 1
        except queue.Empty:
            pass
        self.debug_grid(self.grid)


    def debug_grid(self, grid):
        data = { 's': "", 'prev_row': -1 }
        def debug_coord(data, row, col, val):
            if data['prev_row'] != row:
                data['s'] += '\n'
            if isinstance(val, str):
                data['s'] += val
            data['prev_row'] = row
        grid.visit(debug_coord, data)
        logger.debug(data['s'])


    def navigate(self, program):
        """
        Output the instructions for the intcode program to visit the whole scaffold
        """
        parts = self.compose_movement_routine(
            self.solve_path())
        for part in parts:
            for i in [ord(x) for x in part]:
                program.put(i)
        program.put(ord('y'))
        program.put(ord('\n'))


    def report_space_dust(self):
        """
        Read from the intcode program either grids or until a large number is received.
        """
        i = 0
        row = -5  # The intcode program seems to have a bug where it outputs 5 rows at the start
        while i < 127:
            video_grid = grid.Grid()
            col = 0
            while i < 127 and row < self.grid.num_rows() + 1:
                i = self.inputbuf.get(timeout=5)
                if i < 127:
                    ch = chr(i)
                    if ch == '\n':
                        row += 1
                        col = 0
                    else:
                        video_grid.put(row, col, ch)
                        col += 1
            if video_grid.num_rows() > 0:
                self.debug_grid(video_grid)
            row = 0
        return i


    def find_robot(self):
        data = {}
        def is_robot(data, row, col, val):
            if val == '^' \
                    or val == '>' \
                    or val == 'v' \
                    or val == '<' \
                    or val == 'X':
                data['row'] = row
                data['col'] = col
                data['val'] = val
        self.grid.visit(is_robot, data)
        assert 'row' in data
        return data


    def walk_line(self, cur_row, cur_col, vector):
        next_row = cur_row + vector[0]
        next_col = cur_col + vector[1]
        next_val = self.grid.get(next_row, next_col)
        steps = 0
        while next_val == '#':
            steps += 1
            cur_row = next_row
            cur_col = next_col
            next_row = cur_row + vector[0]
            next_col = cur_col + vector[1]
            next_val = self.grid.get(next_row, next_col)
        return (steps, cur_row, cur_col)


    def turn_left(self, cur_dir):
        if cur_dir == 'v':
            return '>'
        elif cur_dir == '>':
            return '^'
        elif cur_dir == '^':
            return '<'
        elif cur_dir == '<':
            return 'v'
        else:
            raise "Bad direction"


    def turn_right(self, cur_dir):
        if cur_dir == 'v':
            return '<'
        elif cur_dir == '<':
            return '^'
        elif cur_dir == '^':
            return '>'
        elif cur_dir == '>':
            return 'v'
        else:
            raise "Bad direction"


    def solve_path(self):
        """
        Find the movement commands that will make the robot visit every point on the scaffold.
        """
        # heuristic: Go straight ahead unless there is no option but to turn
        start_point = self.find_robot()
        cur_row = start_point['row']
        cur_col = start_point['col']
        cur_dir = start_point['val']
        assert cur_dir != 'X'

        the_end = False
        path = []
        tried_left = False
        tried_right = False
        while not the_end:
            # How far can we go forward?
            if cur_dir == 'v':
                steps, cur_row, cur_col = self.walk_line(cur_row, cur_col, (1, 0))
            elif cur_dir == '^':
                steps, cur_row, cur_col = self.walk_line(cur_row, cur_col, (-1, 0))
            elif cur_dir == '>':
                steps, cur_row, cur_col = self.walk_line(cur_row, cur_col, (0, 1))
            elif cur_dir == '<':
                steps, cur_row, cur_col = self.walk_line(cur_row, cur_col, (0, -1))
            if steps > 0:
                # note we need to check for tried _right first since
                # we try left first when we get a dead end.
                # Possibilities are: we tried left and then right, so both are set
                # OR we have tried left but haven't tried right yet
                if tried_right:
                    path.append('R')
                elif tried_left:
                    path.append('L')
                path.append(str(steps))
                tried_left = False
                tried_right = False
            else:
                if not tried_left:
                    cur_dir = self.turn_left(cur_dir)
                    tried_left = True
                elif not tried_right:
                    # turn right twice since we just turned left
                    cur_dir = self.turn_right(self.turn_right(cur_dir))
                    tried_right = True
                else:
                    the_end = True
        logger.debug("Path: %s", str(path))
        return path


    def compose_movement_routine(self, path):
        """
        Break up path into repeated segments and record the pattern of repetition in the main
        movement routine. Maximum number of functions is 3. Maximum size of each part
        is 20 characters not including new line
        Return: tuple ( main_movement_routine, func_a, func_b, func_c )
        """

        failed = True
        matches_a = None
        matches_b = None
        matches_c = None
        func_a_len = None
        func_b_start = None
        func_c_len = None
        func_c_start = None

        max_length = 11
        max_length_a = max_length
        max_length_b = max_length
        max_length_c = max_length
        while failed and max_length_b >= 1:
            used = ['.'] * len(path)

            func_a_len, matches = find_best_matches(path, 0, max_length_a, used, 'A')
            matches_a = [(x, 'A') for x in matches]

            func_b_start = func_a_len
            while used[func_b_start] != '.':
                func_b_start += 1
            func_b_len, matches = find_best_matches(path, func_b_start, max_length_b, used, 'B')
            matches_b = [(x, 'B') for x in matches]

            func_c_start = func_a_len
            while used[func_c_start] != '.':
                func_c_start += 1
            func_c_len, matches = find_best_matches(path, func_c_start, max_length_c, used, 'C')
            matches_c = [(x, 'C') for x in matches]

            failed = ('.' in used)
            max_length_a -= 1
            if max_length_a < 1:
                max_length_b -= 1
                max_length_a = max_length
            logger.debug("max_lengths %d, %d, %d", max_length_a, max_length_b, max_length_c)

        logger.debug("func_a: %s", path[0:func_a_len])
        logger.debug("func_b: %s", path[func_b_start:func_b_start+func_b_len])
        logger.debug("func_c: %s", path[func_c_start:func_c_start+func_c_len])
        logger.debug("used: %s", used)

        matches = matches_a + matches_b + matches_c
        matches = sorted(matches, key=lambda m: m[0])
        program = [x[1] for x in matches]
        logger.debug("program: %s", program)

        return (
            (",".join(program)) + "\n",
            (",".join(path[0:func_a_len])) + "\n",
            (",".join(path[func_b_start:func_b_start+func_b_len])) + "\n",
            (",".join(path[func_c_start:func_c_start+func_c_len])) + "\n"
        )


def find_best_matches(path, start_idx, max_length, used, mark_chr):
    subpath_len = 1
    matches = find_matches(path, start_idx, subpath_len, used)
    memory = len(",".join(path[start_idx:start_idx+subpath_len]))
    path_free = len([x for x in used[start_idx:start_idx+subpath_len] if x != '.']) == 0
    while subpath_len <= max_length and memory <= 20 and path_free:
        subpath_len += 1
        path_free = len([x for x in used[start_idx:start_idx+subpath_len] if x != '.']) == 0
        matches = find_matches(path, start_idx, subpath_len, used)
        memory = len(",".join(path[start_idx:start_idx+subpath_len]))
    subpath_len -= 1  # previous length satisfied limits
    matches = find_matches(path, start_idx, subpath_len, used)
    matches.append(start_idx)  # subpath is a match with itself
    for match in matches:
        for midx in range(match, match + subpath_len):
            used[midx] = mark_chr
    return (subpath_len, matches)


def find_matches(path, start_idx, length, used):
    subpath = { "start": start_idx, "length": length, "matches": [] }
    for idx in range(subpath["start"] + subpath["length"], len(path)):
        if path[idx] == path[subpath["start"]]:
            is_match = True
            for sub_idx in range(0, subpath["length"]):
                if idx + sub_idx >= len(path):
                    is_match = False
                    break
                elif used[idx + sub_idx] != '.':
                    is_match = False
                    break
                elif path[idx + sub_idx] != path[subpath["start"] + sub_idx]:
                    is_match = False
                    break
            if is_match:
                subpath["matches"].append(idx)
    return subpath["matches"]
