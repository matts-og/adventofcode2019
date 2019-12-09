import sys

def calc_layer_size(width, height):
    return width * height


def layer_to_grid(raw_layer, width, height):
    grid = []
    for row_idx in range(0, height):
        row = []
        for col_idx in range(0, width):
            row.append(int(raw_layer[width * row_idx + col_idx]))
        grid.append(row)
    return grid


def load_layers(filename, width, height):
    layer_size = calc_layer_size(width, height)
    layers = []
    with open(filename) as f:
        buf = f.read(layer_size).strip()
        while len(buf) == layer_size:
            layers.append(layer_to_grid(buf, width, height))
            buf = f.read(layer_size).strip()
        if len(buf) > 0 and len(buf) < layer_size:
            print("Partial buffer: {}".format(buf))
    return layers


def get_pixel(layers, row, col):
    for layer in layers:
        val = layer[row][col]
        if val == 0 or val == 1:
            return val
        assert val == 2
    return 2 # Shouldn't get here I think


def flatten(layers):
    image = []
    for row_idx in range(0, len(layers[0])):
        row = []
        for col_idx in range(0, len(layers[0][0])):
            row.append(get_pixel(layers, row_idx, col_idx))
        image.append(row)
    return image


def render(image):
    for row_idx in range(0, len(image)):
        line = ""
        for col_idx in range(0, len(image[0])):
            val = image[row_idx][col_idx]
            if val == 0:
                line += ' '
            elif val == 1:
                line += '#'
            else:
                line += '.'
        print(line)


filename = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])

render(flatten(load_layers(filename, width, height)))
