import grid


class GameRenderer:
    def __init__(self, player = None):
        self.put_state = 0
        self.grid = grid.Grid(0)
        self.player = player

    def put(self, value):
        if self.put_state == 0:
            self.put_col = value
        elif self.put_state == 1:
            self.put_row = value
        elif self.put_state == 2:
            if self.put_col == -1 and self.put_row == 0:
                print("Score: " + str(value))
            else:
                self.paint(value)
                if self.player != None:
                    self.player.update(self.grid)

        self.put_state = (self.put_state + 1) % 3

    def get(self):
        if self.player != None:
            return self.player.get()
        else:
            while True:
                ch = input("> ")
                if ch == 'j':
                    return -1
                elif ch == 'k':
                    return 0
                elif ch == 'l':
                    return 1


    def grid_to_str_point(self, data, row, col, value):
        if row != self.grid_to_str_prev_row:
            self.grid_str += "\n"
        if value == 0:
            self.grid_str += " "
        elif value == 1:
            self.grid_str += "+"
        elif value == 2:
            self.grid_str += "#"
        elif value == 3:
            self.grid_str += "-"
        elif value == 4:
            self.grid_str += "."
        else:
            assert "Unexpected value in grid: {}".format(value)
        self.grid_to_str_prev_row = row

    def grid_to_str(self):
        self.grid_str = ""
        self.grid_to_str_prev_row = 0
        self.grid.visit(self.grid_to_str_point, None)
        return self.grid_str

    def paint(self, value):
        assert value >= 0 and value <= 4
        assert self.put_row >= 0
        assert self.put_col >= 0
        self.grid.put(self.put_row, self.put_col, value)
        print(self.grid_to_str())

    def get_grid(self):
        return self.grid
