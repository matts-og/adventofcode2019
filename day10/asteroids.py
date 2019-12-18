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


def score_asteroid(grid, row_idx, col_idx):
    score = 0
    row_idx2 = 0
    for row in grid:
        col_idx2 = 0
        for col in row:
            if col:
                if can_see(grid, row_idx, col_idx, row_idx2, col_idx2):
                    score += 1
            col_idx2 += 1
        row_idx2 += 1
    logger.debug("({},{}) score = {}".format(row_idx, col_idx, score))
    return score

def check_grid(grid):
    score_grid = []
    row_idx = 0
    best = (None, None, None)
    for row in grid:
        col_idx = 0
        score_grid.append([0]*len(row))
        for col in row:
            if col:
                score = score_asteroid(grid, row_idx, col_idx)
                score_grid[row_idx][col_idx] = score
                if best[2] == None or score > best[2]:
                    best = (row_idx, col_idx, score)
            col_idx += 1
        row_idx += 1
    logger.debug(score_grid)
    logger.debug(best)
    print(best)
    return best

check_grid(load_asteroids(sys.argv[1]))
