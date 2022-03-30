import numpy
cimport numpy
cimport cython

VISITED = 5

class Node:
    def __init__(self, coords, parent=None):
        self.parent = parent
        self.children = []
        self.coords = coords
        self.is_branching_node = False


def post_proces(node):
    if node.is_branching_node:
        for child in node.children:
            if len(node.children) > 1:
                if len(child.children) == 0:
                    node.children.remove(child)

    for child in node.children:
        post_proces(child)


def bfs(image, coords):
    root = Node(coords, None)
    present_parent = root
    next_parent = [present_parent]
    que = [root.coords]
    existing_node_in_tree_coords = [root.coords]

    while que:
        node_coords = que.pop(0)
        count = True
        all_neighbour = neighbour_of_pixel(image, node_coords)

        if len(all_neighbour) > 2:
            present_parent.is_branching_node = True

        for neighbour in neighbour_of_pixel(image, node_coords):
            if neighbour not in existing_node_in_tree_coords and neighbour not in que:
                que.append(neighbour)
                existing_node_in_tree_coords.append(neighbour)
                child = Node(neighbour, parent=node_coords)
                next_parent.append(child)
                present_parent.children.append(child)

        image[node_coords[0], node_coords[1], node_coords[2]] = VISITED # in order to mark point which was added to tree
        present_parent = next_parent.pop(0)

    post_proces(root)
    return root if len(existing_node_in_tree_coords) > 4 else None


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
    range_neighbour = range_of_neighbours(coords, image)

    for panel in range(range_neighbour[0][0], range_neighbour[0][1]):
        for row in range(range_neighbour[1][0], range_neighbour[1][1]):
            for col in range(range_neighbour[2][0], range_neighbour[2][1]):
                if image[panel, row, col] == 1 and coords != (panel, row, col):
                    neighbour.append((panel, row, col))

    return neighbour


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

    for coords in coords_of_possible_line_end_points:
        if is_line_end_point(image, coords):
            tree = bfs(image, coords)
            if tree is not None:
                trees.append(tree)

    return trees