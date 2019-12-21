class Follower:
    def __init__(self):
        self.ball_diff = 0

    def get(self):
        if self.ball_diff == 0:
            return 0
        elif self.ball_diff > 0:
            return -1
        elif self.ball_diff < 0:
            return 1

    def update(self, grid):
        ball_data = []
        def find_ball(data, row, col, value):
            if value == 4:
                data.append(col)
        grid.visit(find_ball, ball_data)
        bat_data = []
        def find_bat(data, row, col, value):
            if value == 3:
                data.append(col)
        grid.visit(find_bat, bat_data)
        if len(bat_data) > 0 and len(ball_data) > 0:
            self.ball_diff = bat_data[0] - ball_data[0]


