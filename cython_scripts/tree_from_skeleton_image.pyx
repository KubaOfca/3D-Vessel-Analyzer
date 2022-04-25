import numpy
cimport numpy
cimport cython
from math import sqrt
from math import acos
from math import sin
VISITED = 5
T_C = 5

class Node:
    def __init__(self, coords, level, parent=None):
        self.parent = parent
        self.children = []
        self.coords = coords
        self.is_branching_node = False
        self.is_cycle_check_branching_node = False
        self.level = level


def soam(root, feature):
    que = [root.children[0]] # start from child of root
    while que:
        curr = que.pop(0)
        t1 = tuple(numpy.subtract(curr.coords, curr.parent.coords))
        t1_magnitude = sqrt(numpy.dot(t1, t1))
        if curr.children:
            for child in curr.children:
                t2 = tuple(numpy.subtract(child.coords, curr.coords))
                t2_magnitude = sqrt(numpy.dot(t2, t2))
                if child.children:
                    for child_child in child.children:
                        t3 = tuple(numpy.subtract(child_child.coords, child.coords))
                        t3_magnitude = sqrt(numpy.dot(t3, t3))
                        ip_t1_t2_temp = (numpy.dot(t1, t2)/(t1_magnitude * t2_magnitude))
                        ip_t1_t2 = acos(round(ip_t1_t2_temp, 10))
                        ip_t2_t3_temp = (numpy.dot(t2, t3)/(t2_magnitude * t3_magnitude))
                        ip_t2_t3 = acos(round(ip_t2_t3_temp, 10))
                        t1_t2_cross_magnitude = t1_magnitude * t2_magnitude * sin(ip_t1_t2)
                        t2_t3_cross_magnitude = t2_magnitude * t3_magnitude * sin(ip_t2_t3)
                        if t1_t2_cross_magnitude == 0.0 or t2_t3_cross_magnitude == 0.0:
                            tp = acos(0)
                        else:
                            tp_temp = numpy.dot(numpy.cross(t1, t2)/t1_t2_cross_magnitude,
                                            numpy.cross(t2, t3)/t2_t3_cross_magnitude)
                            tp = acos(round(tp_temp, 10))
                        cp = sqrt(ip_t1_t2**2 + tp**2)
                        feature["cp"] += cp
                que.append(child)


def is_cycle(curr):
    end_of_cycle = curr
    x = curr.parent
    while x is not None:
        if x.is_branching_node == True and x.is_cycle_check_branching_node == False:
            x.is_cycle_check_branching_node = True
            if end_of_cycle.level - x.level > T_C:
                return True
            else:
                return False
        x = x.parent
    return False


def print_tree_bfs(root):
    que = [root]
    while que:
        parent = que.pop(0)
        print("Parent: ", parent.coords)
        print("Children: ")
        for child in parent.children:
            print(child.coords)
            que.append(child)
        print("-----------------------------------")


def post_proces(root, feature):
    que = [root]
    while que:
        parent = que.pop(0)
        if parent.is_branching_node:
            for child in parent.children:
                if child.children:
                    que.append(child)
                else:
                    feature["pc"] -= 1
                    feature["lv"] -= sqrt(sum([(parent.coords[i] - child.coords[i])**2 for i in range(3)]))
                    parent.children.remove(child)
            if len(parent.children) == 1:
                parent.is_branching_node = False
                feature["nb"] -= 1
        elif len(parent.children) == 1:
            que.append(parent.children[0])



def build_spanning_tree_bfs_and_extract_features(image, coords):
    root = Node(coords=coords, level=0)
    image[root.coords[0], root.coords[1], root.coords[2]] = VISITED  # in order to mark point which was added to tree
    que = [root]
    feature = {
        "lv": 0.0,
        "nb": 0,
        "nc": 0,
        "pc": 1,
        "dm": 0,
        "cp": 0,
    }

    while que:
        curr = que.pop(0)
        unvisited_neighbors_coords, prev_visited_neighbors_coords = coords_of_neighbors_of_pixel(image, curr.coords)

        # not working well
        if len(prev_visited_neighbors_coords) > 1:
            if is_cycle(curr):
                feature["nc"] += 1

        if len(unvisited_neighbors_coords) > 1:
            curr.is_branching_node = True
            # parameter calc
            feature["nb"] += 1


        for neighbour_coords in unvisited_neighbors_coords:
            if all(neighbour_coords != node.coords for node in que):
                child = Node(coords=neighbour_coords, level=curr.level + 1, parent=curr)
                curr.children.append(child)
                feature["pc"] += 1 # save amount of tree nodes
                que.append(child)
                image[child.coords[0], child.coords[1], child.coords[2]] = VISITED
                # parameter calc
                curr_child_vector = tuple(numpy.subtract(curr.coords, child.coords))
                euclidean_distance = sqrt(numpy.dot(curr_child_vector, curr_child_vector))
                feature["lv"] += euclidean_distance

    post_proces(root, feature)

    if feature["pc"] < 5:
        return None, None

    soam(root, feature)
    last_node_coords = curr.coords # for readability
    root_last_vector = tuple(numpy.subtract(root.coords, last_node_coords))
    feature["dm"] = sqrt(numpy.dot(root_last_vector, root_last_vector)) / feature["lv"]

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


def coords_of_neighbors_of_pixel(image, coords):
    unvisited_neighbors = []
    prev_visited_neighbors = []
    range_of_neighbors = range_of_neighbours(coords, image)

    for panel in range(range_of_neighbors[0][0], range_of_neighbors[0][1]):
        for row in range(range_of_neighbors[1][0], range_of_neighbors[1][1]):
            for col in range(range_of_neighbors[2][0], range_of_neighbors[2][1]):
                if image[panel, row, col] == 1 and coords != (panel, row, col):
                    unvisited_neighbors.append((panel, row, col))
                if image[panel, row, col] == VISITED and coords != (panel, row, col):
                    prev_visited_neighbors.append((panel, row, col))

    return unvisited_neighbors, prev_visited_neighbors


def is_line_end_point(image, coords):
    range_neighbour = range_of_neighbours(coords, image)
    array_to_sum = image[range_neighbour[0][0]:range_neighbour[0][1],
                   range_neighbour[1][0]:range_neighbour[1][1],
                   range_neighbour[2][0]:range_neighbour[2][1]]

    return numpy.sum(array_to_sum) == 2


def form_array_of_skeleton_make_spanning_trees(image):
    trees = []
    coords_of_possible_line_end_points = list(zip(*numpy.where(image == 1)))
    lv_feature = 0.0
    nb_feature = 0
    nc_feature = 0
    dm_feature = 0
    cp_feature = 0
    for coords in coords_of_possible_line_end_points:
        if is_line_end_point(image, coords):
            tree, feature = build_spanning_tree_bfs_and_extract_features(image, coords)
            if tree is not None:
                trees.append(tree)
                lv_feature += feature["lv"]
                nb_feature += feature["nb"]
                nc_feature += feature["nc"]
                dm_feature += feature["dm"]
                cp_feature += feature["cp"]
    return trees, lv_feature, nb_feature, nc_feature, dm_feature, cp_feature