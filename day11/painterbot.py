import logging
logger = logging.getLogger("painterbot")
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
        for row in range(0, self.num_rows()):
            for col in range(0, self.max_col + 1):
                val = self.get(row + self.min_row, col + self.min_col)
                func(data, row + self.min_row, col + self.min_col, val)


class PainterBot:
    def __init__(self):
        self.put_state = 0
        self.grid = Grid(-1)
        self.row = 0
        self.col = 0
        # Direction is stored as two multipliers one for the row direction and one for the col
        # direction. Movement is done by multiplying the direction vectors by the magnitude of the
        # vector in the row and col directions.
        self.row_dir = -1
        self.col_dir = 0
        self.put_count = 0

    def get(self):
        return 1 if self.grid.get(self.row, self.col) == 1 else 0

    def put(self, value):
        if self.put_state == 0:
            self.grid.put(self.row, self.col, value)
            self.put_state = 1
        else:
            self.move(value)
            self.put_state = 0
            self.put_count += 1
        # For debugging it helps to stop after a few steps
        #assert self.put_count < 20


    def move(self, direction):
        assert isinstance(direction, int) and direction >= 0 and direction <= 1
        new_row_dir = None
        new_col_dir = None
        if direction == 0:
            # turn left
            if self.row_dir == 0:
                new_row_dir = -1 * self.col_dir
            else:
                new_row_dir = 0
            if self.col_dir == 0:
                new_col_dir = self.row_dir
            else:
                new_col_dir = 0
        else:
            # turn right
            if self.row_dir == 0:
                new_row_dir = self.col_dir
            else:
                new_row_dir = 0
            if self.col_dir == 0:
                new_col_dir = -1 * self.row_dir
            else:
                new_col_dir = 0
        self.row += new_row_dir
        self.col += new_col_dir
        self.row_dir = new_row_dir
        self.col_dir = new_col_dir
        logger.debug("moved to row={}, col={}, {}".format(self.row, self.col, self.paint_cursor()))
        # Uncomment the following grid dump for very verbose debugging
        #logger.debug(self.grid_to_str())

    def get_grid(self):
        return self.grid

    def paint_cursor(self):
        if self.row_dir == -1 and self.col_dir == 0:
            return "^"
        elif self.row_dir == 0 and self.col_dir == 1:
            return ">"
        elif self.row_dir == 1 and self.col_dir == 0:
            return "V"
        elif self.row_dir == 0 and self.col_dir == -1:
            return "<"
        else:
            assert "Invalid row_dir {} or col_dir {}".format(self.row_dir, self.col_dir)

    def grid_to_str_point(self, data, row, col, value):
        if row != self.grid_to_str_prev_row:
            self.grid_str += "\n"
        if row == self.row and col == self.col:
            # Paint cursor
            self.grid_str += self.paint_cursor() + " "
        else:
            if value == -1:
                self.grid_str += ". "
            elif value == 0:
                self.grid_str += "- "
            elif value == 1:
                self.grid_str += "# "
            else:
                assert "Unexpected value in grid: {}".format(value)
        self.grid_to_str_prev_row = row

    def grid_to_str(self):
        self.grid_str = ""
        self.grid_to_str_prev_row = None
        self.grid.visit(self.grid_to_str_point, None)
        return self.grid_str

