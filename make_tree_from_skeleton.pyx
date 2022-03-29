import numpy
cimport numpy
cimport cython
from cpython cimport array
import array

change_color = 5

class Node:
    def __init__(self, coords, parent=None):
        self.parent = parent
        self.child = []
        self.coords = coords


def bfs(image, coords):
    tree = Node(coords, None)
    present_parent = tree
    next_parent = [present_parent]
    que = [tree.coords]
    tree_node_list = [tree.coords]
    global change_color
    while que:
        v = que.pop(0)
        count = True
        for w in neighbour_of_pixel(image, v):
            if w not in tree_node_list and w not in que:
                tree_node_list.append(w)
                que.append(w)
                child = Node(w, parent=v)
                next_parent.append(child)
                present_parent.child.append(child)
        present_parent = next_parent.pop(0)
        image[v[0], v[1], v[2]] = change_color
    change_color += 1
    return tree


def range_of_neighboor(pixel, image):
    if pixel[0] == 0:
        panel_start = pixel[0]
    else:
        panel_start = pixel[0] - 1
    if pixel[0] == image.shape[0] - 1:
        panel_end = pixel[0] + 1
    else:
        panel_end = pixel[0] + 2

    if pixel[1] == 0:
        row_start = pixel[1]
    else:
        row_start = pixel[1] - 1
    if pixel[1] == image.shape[1] - 1:
        row_end = pixel[1] + 1
    else:
        row_end = pixel[1] + 2

    if pixel[2] == 0:
        col_start = pixel[2]
    else:
        col_start = pixel[2] - 1
    if pixel[2] == image.shape[2] - 1:
        col_end = pixel[2] + 1
    else:
        col_end = pixel[2] + 2

    return [(panel_start, panel_end), (row_start, row_end), (col_start, col_end)]


def neighbour_of_pixel(image, pixel):
    neighbour = []
    range_neighboor = range_of_neighboor(pixel, image)

    for panel in range(range_neighboor[0][0], range_neighboor[0][1]):
        for row in range(range_neighboor[1][0], range_neighboor[1][1]):
            for col in range(range_neighboor[2][0], range_neighboor[2][1]):
                if image[panel, row, col] == 1 and pixel != (panel, row, col):
                    neighbour.append((panel, row, col))

    return neighbour


def is_line_end_point(image, point):
    range_neighboor = range_of_neighboor(point, image)
    array_to_sum = image[range_neighboor[0][0]:range_neighboor[0][1], range_neighboor[1][0]:range_neighboor[1][1],
                   range_neighboor[2][0]:range_neighboor[2][1]]
    return numpy.sum(array_to_sum) == 2


def form_array_of_skeleton_make_spanning_trees(image):
    trees = []
    indexes_of_value_one = numpy.where(image == 1)
    coords_of_value_one = list(zip(*indexes_of_value_one))
    for point in coords_of_value_one:
        if is_line_end_point(image, point):
            trees.append(bfs(image, point))

    return trees