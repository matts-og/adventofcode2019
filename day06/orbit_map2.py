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

def calc_transfer(root, src_name, dest_name):
    src = anytree.search.find(root, filter_=lambda node: node.name == src_name)
    dest = anytree.search.find(root, filter_=lambda node: node.name == dest_name)
    #print(src)
    #print(dest)
    common_ancestors = anytree.util.commonancestors(src,dest)
    max_depth_ancestor = common_ancestors[0]
    for a in common_ancestors[1:]:
        if a.depth > max_depth_ancestor.depth:
            max_depth_ancestor = a
    #print(max_depth_ancestor)
    return (src.depth - 1 - max_depth_ancestor.depth) + (dest.depth - 1 - max_depth_ancestor.depth)


assert len(sys.argv) >= 4
filename = sys.argv[1]
src = sys.argv[2]
dest = sys.argv[3]
print(calc_transfer(load_orbits(filename), src, dest))
