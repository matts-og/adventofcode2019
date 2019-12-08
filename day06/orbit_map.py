import sys
import anytree

def load_orbits(filename):
    node_map = {}
    with open(filename) as f:
        line = f.readline().strip()
        while len(line) > 0:
            item = line.split(')')
            parent_name = item[0]
            child_name = item[1]
            if parent_name in node_map:
                parent = node_map[parent_name]
            else:
                parent = anytree.Node(parent_name)
                node_map[parent_name] = parent
            if child_name in node_map:
                child = node_map[child_name]
            else:
                child = anytree.Node(child_name)
                node_map[child_name] = child
            child.parent = parent
            line = f.readline().strip()
    node_key = next(iter(node_map))
    return node_map[node_key].root

def sum_orbits(root):
    res = 0
    for node in anytree.PreOrderIter(root):
        res += node.depth
    return res

assert len(sys.argv) >= 2
filename = sys.argv[1]
print(sum_orbits(load_orbits(filename)))
