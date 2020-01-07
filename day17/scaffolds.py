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
        self.debug_grid()

    def debug_grid(self):
        data = { 's': "", 'prev_row': -1 }
        def debug_coord(data, row, col, val):
            if data['prev_row'] != row:
                data['s'] += '\n'
            if isinstance(val, str):
                data['s'] += val
            data['prev_row'] = row
        self.grid.visit(debug_coord, data)
        logger.debug(data['s'])
