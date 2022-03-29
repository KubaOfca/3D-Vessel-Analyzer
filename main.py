import pydicom
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize_3d
import time

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)

# global var
ROI = [(115, 1032), (169, 702)]
COLORS = {
    0: [50, 0, 0],
    1: [50, 0, 0],
    2: [50, 0, 0],
    3: [50, 0, 0],
    4: [50, 0, 0],
    5: [255, 0, 0],
    6: [0, 255, 0],
    7: [0, 0, 255],
    8: [255, 255, 0],
    9: [0, 255, 255],
    10: [255, 0, 255],
    11: [128, 128, 128],
    12: [128, 0, 0],
    13: [128, 128, 0],
    14: [0, 128, 0],
    15: [128, 0, 128],
    16: [0, 128, 128],
    17: [0, 0, 128],
    18: [128, 0, 128],
    19: [139, 69, 19],
    20: [152, 251, 152],
}

change_color = 5


class Node:
    def __init__(self, coords, parent=None):
        self.parent = parent
        self.child = []
        self.coords = coords

    def add_child(self, parent_coords, child_node):
        parent_node = self.find(parent_coords)
        parent_node.child.append(child_node)

    def is_node_in_tree(self, x):
        if self.coords == x:
            return True
        for node in self.child:
            n = node.find(x)
            if n:
                return True
        return False

    def find(self, x):
        if self.coords == x:
            return self
        for node in self.child:
            n = node.find(x)
            if n:
                return n
        return None


def bfs(image, coords):
    tree = Node(coords, None)
    que = [tree.coords]
    tree_node_list = [tree.coords]
    global change_color

    while que:
        v = que.pop(0)
        for w in neighbour_of_pixel(image, v):
            if w not in tree_node_list and w not in que:
                que.append(w)
                tree_node_list.append(w)
                child = Node(w, parent=v)
                tree.add_child(v, child)
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
                   range_neighboor[2][0]:range_neighboor[2][1]].ravel()
    return sum(array_to_sum) == 2


def form_array_of_skeleton_make_spanning_trees(image):
    trees = []
    indexes_of_value_one = np.where(image == 1)
    coords_of_value_one = list(zip(*indexes_of_value_one))
    for point in coords_of_value_one:
        if is_line_end_point(image, point):
            trees.append(bfs(image, point))

    return trees


def threshold(image):
    background = np.logical_and(image[:, :, :, 0] == image[:, :, :, 1], image[:, :, :, 1] == image[:, :, :, 2])
    image[background] = [0, 0, 0]
    image[np.logical_not(background)] = [1, 0, 0]


def make_RGB_image_binary(image):
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image


def save_one_2D_binary_image(image, name):
    im = Image.fromarray(image * 255)
    im.save(f"{name}.png")


def save_series_2D_binary_image(image, basename):
    n = image.shape[0]
    for i in range(n):
        im = Image.fromarray(image[i], "RGB")
        im.save(f"{basename}{i}.png")


def main():
    filepath = r"C:\Users\bkuba\PycharmProjects\PracaLicencjacka\zdj.dcm"
    dcm_image = pydicom.dcmread(filepath)
    data = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
    print(data.dtype)
    threshold(data)
    data = make_RGB_image_binary(data)
    data_skeleton = skeletonize_3d(data)
    s = time.time()
    trees = form_array_of_skeleton_make_spanning_trees(data_skeleton)
    print(f'{time.time() - s} END')
    color_array = np.zeros(shape=(data_skeleton.shape[0], data_skeleton.shape[1], data_skeleton.shape[2], 3),
                           dtype=np.uint8)
    for panel in range(data_skeleton.shape[0]):
        for row in range(data_skeleton.shape[1]):
            for col in range(data_skeleton.shape[2]):
                if data_skeleton[panel, row, col] > 0:
                    print(COLORS[data_skeleton[panel, row, col] % 20])
                    color_array[panel, row, col] = COLORS[data_skeleton[panel, row, col] % 20]
                    print(color_array[panel, row, col])
    print(color_array)
    save_series_2D_binary_image(color_array, "Kolorwe")


main()
