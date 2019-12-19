import sys
import math

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def load_asteroids(filename):
    grid = []
    with open(filename) as f:
        line = f.readline().strip()
        while len(line) > 0:
            logger.debug(line)
            row = [(c == '#') for c in line]
            grid.append(row)
            line = f.readline().strip()
    logger.debug(grid)
    return grid


def make_signed_range(distance, step = 1):
    return range(
        step * int(math.copysign(1, distance)),
        int(distance),
        step * int(math.copysign(1, distance))
    )


def common_factors(a, b):
    res = []
    for x in range(2, max(a,b) + 1):
        if b % x == 0 and a % x == 0:
            res.append(x)
    logger.debug("common_factors({}, {}) = {}".format(a,b,res))
    return res


def can_see(grid, row_idx, col_idx, row_idx2, col_idx2):
    logger.debug("can_see ({},{}) -> ({},{})".format(row_idx, col_idx, row_idx2, col_idx2))
    if row_idx == row_idx2 and col_idx == col_idx2:
        # Can't see itself
        logger.debug("* False (Can't see itself)")
        return False

    row_distance = row_idx2 - row_idx
    col_distance = col_idx2 - col_idx
    logger.debug("row_distance = {}, col_distance = {}".format(row_distance, col_distance))
    if abs(col_distance) == 1 or abs(row_distance) == 1:
        # nothing can block since no asteroids can be in-between coordinates
        logger.debug("* True (distance < 1 in row or column)")
        return True

    if abs(col_distance) == 0:
        # special case - same col
        logger.debug("Same col")
        for row_distance2 in make_signed_range(row_distance):
            row_idx3 = row_idx + row_distance2
            col_idx3 = col_idx
            logger.debug("Check ({},{})".format(row_idx3, col_idx3))
            if grid[row_idx3][col_idx3]:
                # there is an asteroid blocking
                logger.debug("* False (blocked)")
                return False
        logger.debug("* True")
        return True

    if abs(row_distance) == 0:
        # special case - same row
        logger.debug("Same row")
        for col_distance2 in make_signed_range(col_distance):
            col_idx3 = col_idx + col_distance2
            row_idx3 = row_idx
            logger.debug("Check ({},{})".format(row_idx3, col_idx3))
            if grid[row_idx3][col_idx3]:
                # there is an asteroid blocking
                logger.debug("* False (blocked)")
                return False
        logger.debug("* True")
        return True

    factors = common_factors(abs(col_distance), abs(row_distance))
    if len(factors) == 0:
        logger.debug("* True (row and col distance have no common factors)")
        return True

    if abs(row_distance) >= abs(col_distance):
        logger.debug("columns step")
        for f in factors:
            step = int(abs(col_distance / f))
            logger.debug("factor = {}, step = {}".format(f, step))
            for col_distance2 in make_signed_range(col_distance, step):
                col_idx3 = col_idx + col_distance2
                row_idx3 = row_idx + int(row_distance * col_distance2 / col_distance)
                logger.debug("Check ({},{})".format(row_idx3, col_idx3))
                if grid[row_idx3][col_idx3]:
                    # there is an asteroid blocking
                    logger.debug("* False (blocked)")
                    return False
    else:
        # step through the rows
        logger.debug("rows step")
        for f in factors:
            step = int(abs(row_distance / f))
            logger.debug("factor = {}, step = {}".format(f, step))
            for row_distance2 in make_signed_range(row_distance, step):
                row_idx3 = row_idx + row_distance2
                col_idx3 = col_idx + int(col_distance * row_distance2 / row_distance)
                logger.debug("Check ({},{})".format(row_idx3, col_idx3))
                if grid[row_idx3][col_idx3]:
                    # there is an asteroid blocking
                    logger.debug("* False (blocked)")
                    return False
    logger.debug("* True")
    return True


def laser_asteroids(grid, ms_row, ms_col, laser_limit):
    destroyed = []
    while len(destroyed) < laser_limit:
        wave = []
        for row_idx in range(0, len(grid)):
            row = grid[row_idx]
            for col_idx in range(0, len(row)):
                col = row[col_idx]
                if col:
                    if can_see(grid, ms_row, ms_col, row_idx, col_idx):
                        # flip row coordinates to be more cartesian
                        # Reverse angle for clockwise +ve from 12 oclock
                        angle = math.pi / 2.0 - math.atan2(ms_row - row_idx, col_idx - ms_col)
                        while angle < 0:
                            angle += 2 * math.pi
                        # convert to hours
                        angle = angle * 6.0 / math.pi
                        logger.debug("angle: {}, {}, {}".format(row_idx, col_idx, angle))
                        wave.append((row_idx, col_idx, angle))
        assert len(wave) > 0, "Ran out of asteroids before hitting the limit"
        wave.sort(key = lambda a: a[2])
        for a in wave:
            # Blast asteroids out of the grid
            grid[a[0]][a[1]] = False
            logger.debug("destroyed: {}, {}, {}".format(a[0], a[1], a[2]))
        destroyed += wave
    return destroyed[laser_limit-1]


filename = sys.argv[1]
monitoring_station = int(sys.argv[2]) # 1820 (row * 100 + col)
ms_row = math.floor(monitoring_station / 100)
ms_col = monitoring_station % 100
laser_limit = int(sys.argv[3])
nth_asteroid = laser_asteroids(load_asteroids(filename), ms_row, ms_col, laser_limit)
print(nth_asteroid)
