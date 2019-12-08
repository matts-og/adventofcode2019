import sys


def line_to_path(line):
    #print(line.strip())
    return [(x[0],int(x[1:])) for x in line.split(',')]


def path_to_coordinates(path):
    coordinates = [(0,0)]
    cur = (0,0)
    for vector in path:
        direction = vector[0]
        length = vector[1]
        for _ in range(0,length):
            if direction == 'R':
                cur = (cur[0] + 1, cur[1])
            elif direction == 'L':
                cur = (cur[0] - 1, cur[1])
            elif direction == 'U':
                cur = (cur[0], cur[1] + 1)
            elif direction == 'D':
                cur = (cur[0], cur[1] - 1)
            #print("({},{})".format(cur[0],cur[1]))
            coordinates.append(cur)
    return coordinates


def corners(coordinates):
    min_corner = [0, 0]
    max_corner = [0, 0]
    for c in coordinates:
        if c[0] < min_corner[0]:
            min_corner[0] = c[0]
        if c[1] < min_corner[1]:
            min_corner[1] = c[1]
        if c[0] > max_corner[0]:
            max_corner[0] = c[0]
        if c[1] > max_corner[1]:
            max_corner[1] = c[1]
    #print("({},{}) -> ({},{})".format(min_corner[0], min_corner[1], max_corner[0], max_corner[1]))
    return (min_corner, max_corner)


def coordinates_to_grid(coordinates):
    min_corner, max_corner = corners(coordinates)
    width = max_corner[0] - min_corner[0] + 1
    height = max_corner[1] - min_corner[1] + 1
    grid = [ [ False for w in range(0, width)] for h in range(0, height) ] # [row][col]
    for c in coordinates:
        x = c[0] - min_corner[0]
        y = c[1] - min_corner[1]
        grid[y][x] = True
    return (min_corner, max_corner, grid)


def find_intersections(min_corner, grid, coordinates):
    #print("intersections")
    intersections = []
    for c in coordinates:
        x = c[0] - min_corner[0]
        y = c[1] - min_corner[1]
        try:
            if grid[y][x]:
                intersections.append(c)
                #print("({},{})".format(c[0],c[1]))
        except IndexError:
            # If it's not on path1's grid then it's not intersecting
            pass
    return intersections


def distance(c):
    x = c[0]
    y = c[1]
    return abs(x) + abs(y)


def find_min_distance(coordinates):
    min_distance = None
    for c in coordinates:
        dist = distance(c)
        if dist > 0 and (min_distance == None or dist < min_distance):
            min_distance = dist
    return min_distance


def print_grid(grid):
    for row in reversed(grid):
        line = ""
        for col in row:
            if col:
                line += " * "
            else:
                line += " . "
        print(line)


with open(sys.argv[1]) as f:
    print("Converting path1 to grid")
    min_corner, max_corner, grid = coordinates_to_grid(
        path_to_coordinates(
            line_to_path(f.readline())))
    print("Finding intersections")
    min_distance = find_min_distance(find_intersections(
        min_corner, grid, path_to_coordinates(
            line_to_path(f.readline()))))
    print("Min manhattan distance to wire crossing is {}".format(min_distance))
