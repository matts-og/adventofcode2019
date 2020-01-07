import logging
logger = logging.getLogger("grid")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class Grid:
    def __init__(self, default = -1):
        self.default = default
        self.grid = []
        self.min_row = 0
        self.min_col = 0
        self.max_col = 0

    # Since coordinates can be -ve, the grid needs grow in the negative direction and internally
    # store -ve coordinates as +ve array indexes. When a coordinate smaller than the minumum is
    # given we prepend data to the grid and set new minimum offsets
    def convert_coords(self, row, col):
        if row < self.min_row:
            # prepend rows
            self.grid = [None] * (self.min_row - row) + self.grid
            self.min_row = row
            logger.debug("convert_coords min_row = {}".format(self.min_row))
        if col < self.min_col:
            # prepend columns to all rows
            for row in range(0, self.num_rows()):
                row_array = self.grid[row]
                if row_array != None:
                    self.grid[row] = [self.default] * (self.min_col - col) + row_array
            self.max_col += self.min_col - col
            self.min_col = col
            logger.debug("convert_coords min_col = {}".format(self.min_col))
        new_row = row - self.min_row
        new_col = col - self.min_col
        return (new_row, new_col)

    def get(self, row, col):
        row, col = self.convert_coords(row, col)
        try:
            if self.grid[row] == None:
                value = self.default
            else:
                value = self.grid[row][col]
        except IndexError:
            value = self.default
        return value

    def put(self, row, col, value):
        logger.debug("put: row={}, col={}, value={}".format(row, col, value))
        row, col = self.convert_coords(row, col)
        self.max_col = max(self.max_col, col)
        try:
            row_array = self.grid[row]
        except IndexError:
            self.grid += [None] * (row - len(self.grid) + 1)
            row_array = self.grid[row]
        if row_array == None:
            self.grid[row] = []
            row_array = self.grid[row]
        try:
            self.grid[row][col] = value
        except IndexError:
            self.grid[row] += [self.default] * (col - len(row_array) + 1)
            self.grid[row][col] = value

    def num_rows(self):
        return len(self.grid)

    def visit(self, func, data):
        for raw_row in range(0, self.num_rows()):
            for raw_col in range(0, self.max_col + 1):
                val = self.get(raw_row + self.min_row, raw_col + self.min_col)
                func(data, raw_row + self.min_row, raw_col + self.min_col, val)
