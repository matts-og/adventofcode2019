import sys

def calc_layer_size(width, height):
    return width * height


def load_raw_layers(filename, width, height):
    layer_size = calc_layer_size(width, height)
    layers = []
    with open(filename) as f:
        buf = f.read(layer_size).strip()
        while len(buf) == layer_size:
            layers.append(buf)
            buf = f.read(layer_size).strip()
        if len(buf) > 0 and len(buf) < layer_size:
            print("Partial buffer: {}".format(buf))
    return layers


def count_n(raw_layer, n):
    return len([p for p in raw_layer if p == n])


def get_layer_with_least_0(raw_layers):
    least_0 = None
    least_0_layer_idx = None
    num_layers = len(raw_layers)
    for idx in range(0,num_layers):
        count0 = count_n(raw_layers[idx], '0')
        if least_0 == None or count0 < least_0:
            least_0 = count0
            least_0_layer_idx = idx
    return least_0_layer_idx



filename = sys.argv[1]
width = int(sys.argv[2])
height = int(sys.argv[3])

raw_layers = load_raw_layers(filename, width, height)
print(len(raw_layers))
idx0 = get_layer_with_least_0(raw_layers)
print(idx0)
print(count_n(raw_layers[idx0],'1') * count_n(raw_layers[idx0],'2'))
