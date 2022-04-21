import numpy
cimport numpy
cimport cython
from math import sqrt
VISITED = 5
T_C = 5

class Node:
    def __init__(self, coords, level, parent=None):
        self.parent = parent
        self.children = []
        self.coords = coords
        self.is_branching_node = False
        self.level = level


def post_proces(node, existing_node_in_tree, feature):
    if node.is_branching_node:
        for child in node.children:
            if len(node.children) > 1:
                if len(child.children) == 0:
                    node.children.remove(child)
                    euclidean_distance = sqrt(sum([(node.coords[i] - child.coords[i])**2 for i in range(3)]))
                    feature["lv"] -= euclidean_distance
                    try:
                        existing_node_in_tree.remove(child)
                    except ValueError:
                        print("Element not in list")

    if len(node.children) < 2 and node.is_branching_node:
        node.is_branching_node = False
        feature["nb"] -= 1

    for child in node.children:
        try:
            post_proces(child, existing_node_in_tree, feature)
        except:
            print("Too deepth")


def bfs(image, coords):
    root = Node(coords, 0, None)
    present_parent = root
    next_parent = []
    que = [root.coords]
    existing_node_in_tree = [root]
    existing_node_in_tree_coords = [root.coords]
    feature = {
        "lv" : 0.0,
        "nb" : 0,
        "nc" : 0,
    }

    while que:
        node_coords = que.pop(0)
        count = True
        all_neighbour, prev_visited = neighbour_of_pixel(image, node_coords)

        for node in existing_node_in_tree:
            if node.coords in prev_visited:
                if present_parent.level - node.level > T_C:
                    print("dodaje 1")
                    feature["nc"] += 1
                    print(feature["nc"])
                    break

        if len(all_neighbour) > 2:
            present_parent.is_branching_node = True
            feature["nb"] += 1


        for neighbour in all_neighbour:
            if neighbour not in existing_node_in_tree_coords and neighbour not in que:
                que.append(neighbour)
                existing_node_in_tree_coords.append(neighbour)
                child = Node(coords=neighbour, level=present_parent.level + 1, parent=present_parent)
                existing_node_in_tree.append(child)
                euclidean_distance = sqrt(sum([(present_parent.coords[i] - child.coords[i])**2 for i in range(3)]))
                feature["lv"] += euclidean_distance
                next_parent.append(child)
                present_parent.children.append(child)

        image[node_coords[0], node_coords[1], node_coords[2]] = VISITED # in order to mark point which was added to tree
        if next_parent:
            present_parent = next_parent.pop(0)

    try:
        post_proces(root, existing_node_in_tree, feature)
    except:
        print("Too deepth ")
    if len(existing_node_in_tree) <= 4:
        return None, None
    else:
        return root, feature


def range_of_neighbours(coords, image):
    if coords[0] == 0:
        panel_start = coords[0]
    else:
        panel_start = coords[0] - 1
    if coords[0] == image.shape[0] - 1:
        panel_end = coords[0] + 1
    else:
        panel_end = coords[0] + 2

    if coords[1] == 0:
        row_start = coords[1]
    else:
        row_start = coords[1] - 1
    if coords[1] == image.shape[1] - 1:
        row_end = coords[1] + 1
    else:
        row_end = coords[1] + 2

    if coords[2] == 0:
        col_start = coords[2]
    else:
        col_start = coords[2] - 1
    if coords[2] == image.shape[2] - 1:
        col_end = coords[2] + 1
    else:
        col_end = coords[2] + 2

    return [(panel_start, panel_end), (row_start, row_end), (col_start, col_end)]


def neighbour_of_pixel(image, coords):
    neighbour = []
    prev_visited = []
    range_neighbour = range_of_neighbours(coords, image)

    for panel in range(range_neighbour[0][0], range_neighbour[0][1]):
        for row in range(range_neighbour[1][0], range_neighbour[1][1]):
            for col in range(range_neighbour[2][0], range_neighbour[2][1]):
                if image[panel, row, col] == 1 and coords != (panel, row, col):
                    neighbour.append((panel, row, col))
                if image[panel, row, col] == VISITED and coords != (panel, row, col):
                    prev_visited.append((panel, row, col))

    return neighbour, prev_visited


def is_line_end_point(image, coords):
    range_neighbour = range_of_neighbours(coords, image)
    array_to_sum = image[range_neighbour[0][0]:range_neighbour[0][1],
                   range_neighbour[1][0]:range_neighbour[1][1],
                   range_neighbour[2][0]:range_neighbour[2][1]]

    return numpy.sum(array_to_sum) == 2


def form_array_of_skeleton_make_spanning_trees(image):
    trees = []
    indexes_of_possible_line_end_points = numpy.where(image == 1)
    coords_of_possible_line_end_points = list(zip(*indexes_of_possible_line_end_points))
    lv_feature = 0.0
    nb_feature = 0
    nc_feature = 0
    for coords in coords_of_possible_line_end_points:
        if is_line_end_point(image, coords):
            tree, feature = bfs(image, coords)
            if tree is not None:
                trees.append(tree)
                lv_feature += feature["lv"]
                nb_feature += feature["nb"]
                nc_feature += feature["nc"]
    return trees, lv_feature, nb_feature, nc_feature