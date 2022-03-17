import matplotlib.pyplot as plt
import pydicom
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize_3d

# np.set_printoptions(threshold=sys.maxsize)

# const

MASKS = {
    "U" : [{ "0" : [(0,0,0), (0,0,1), (0,0,2),
                   (1,0,0), (1,0,1), (1,0,2),
                   (2,0,0), (2,0,1), (2,0,2)],
            "1" : [(1,1,1), (1,2,1)],
            "X" : [(0,1,0), (0,1,1), (0,1,2),
                   (0,2,0), (0,2,1), (0,2,2),
                   (1,1,0), (1,1,2), (1,2,0),
                   (1,2,2), (2,1,0), (2,1,1),
                   (2,1,2), (2,2,0), (2,2,1),
                   (2,2,2)]},]
}

def fast_threshold(image):
    """
    Change red component of picture to white color (1) and makes everything else black (0)
    :param image:
    :return: ndarray 4D
    """
    RGB_threshold = [(120, 255), (0, 105), (0, 255)]

    red_range = np.logical_and(RGB_threshold[0][0] < image[:, :, :, 0], image[:, :, :, 0] < RGB_threshold[0][1])
    green_range = np.logical_and(RGB_threshold[1][0] < image[:, :, :, 1], image[:, :, :, 1] < RGB_threshold[1][1])
    blue_range = np.logical_and(RGB_threshold[2][0] < image[:, :, :, 2], image[:, :, :, 2] < RGB_threshold[2][1])
    valid_range = np.logical_and(red_range, green_range, blue_range)

    image[valid_range] = [255, 255, 255]
    image[np.logical_not(valid_range)] = [0, 0, 0]

    binary = np.logical_and(200 < image[:, :, :, 0], 255 >= image[:, :, :, 0])

    image[binary] = [1, 1, 1]
    image[np.logical_not(binary)] = [0, 0, 0]

    return image[:, :, 100:]

def reduce_RGB_to_Binary(image):
    """
    Reduce RGB dimention from 4D array to 3D array with values 1 for white, 0 for black
    :param image: 4D ndarray
    :return: 3D ndarray
    """
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image

def plot_3D_from_3D_binary_image(image, save_to_file_from_diff_view=False):
    """
    Plot only values of pixel == 1
    point size == 0.3
    :param image: 3D ndarray
    :return: None
    """
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    z, x, y = image.nonzero()
    ax.scatter(y, z, x, c="black", alpha=1, s=0.3)
    if(save_to_file_from_diff_view):
        for angle in range(0,360,20):
            ax.view_init(elev=50., azim=angle)
            plt.savefig(f"angle{angle}.png")
    plt.show()

def is_border_point(z, y, x, whole_3D_image):
    """
    Check if given point is border point (white point have at least 6-adj with black point)
    :param z:
    :param y:
    :param x:
    :param whole_3D_image:
    :return:
    """
    if whole_3D_image[z, y, x-1] == 0 or whole_3D_image[z, y, x+1] == 0 or whole_3D_image[z, y-1, x] == 0 or \
            whole_3D_image[z, y+1, x] == 0:
        return True

    if z != 0 and z != whole_3D_image.shape[0] - 1:
        if whole_3D_image[z-1, y, x] == 0 or whole_3D_image[z+1, y, x] == 0:
            return True
    elif z == 0:
        if whole_3D_image[z+1, y, x] == 0:
            return True
    else:
        if whole_3D_image[z-1, y, x] == 0:
            return True

    return False


def make_help_array(z, y, x, image):
    """
    Crate an 3x3x3 array and fill it with point p and its neighborhood
    :param z:
    :param y:
    :param x:
    :param image:
    :return: 3x3x3 array with p and its neighborhood
    """
    arr = np.zeros((3, 3, 3))
    if z != 0 and z != image.shape[0] - 1:
        arr[:, :, :] = image[z-1:z+2, y-1:y+2, x-1:x+2]  # ?
    elif z == image.shape[0] - 1:
        arr[:2, :, :] = image[z - 1:z + 1, y - 1:y + 2, x - 1:x + 2]
        arr[2, :, :] = 0
    else:
        arr[1:3, :, :] = image[z:z + 2, y - 1:y + 2, x - 1:x + 2]
        arr[0, :, :] = 0
    return arr

def match_mask(arr, side):
    """
    Check if border points match to at least one given mask
    :param arr:
    :param side:
    :return: True if match False if not
    """
    for i in range(len(MASKS[side])):
        z, y, x = np.where(arr == 0)
        zeros_index_list = [(z[i], y[i], x[i]) for i in range(len(x))]
        if not all(x in zeros_index_list for x in MASKS[side][i]["0"]):
            continue
        z, y, x = np.where(arr == 1)
        one_index_list = [(z[i], y[i], x[i]) for i in range(len(x))]
        if not all(x in one_index_list for x in MASKS[side][i]["1"]):
            continue
        if MASKS[side][i]["X"] and not any(x in one_index_list for x in MASKS[side][i]["X"]):
            continue

        return True

    return False


def delete_border_points(which_side, indexes, image):
    """
    From given list of potential border points to delete, choose this witch match the conditions
    :param which_side: kind of subiteration like U D S N W E
    :param indexes: indexes of border points
    :param image:
    :return: None
    """
    for point in indexes:
        z, y, x = point[0], point[1], point[2]
        border_neighboor = make_help_array(z, y, x, image)
        if match_mask(border_neighboor, which_side):
            image[z, y, x] = 0
            indexes.remove(point)


def determine_index_of_border_points(image):
    """
    Retrun a indexes of border points
    :param image:
    :return: list of tuples List[tuples()]
    """
    border_indexes = []
    z, y, x = np.where(image == 1)
    [border_indexes.append((z[i], y[i], x[i])) for i in range(len(x)) if is_border_point(z[i], y[i], x[i], image)]
    return border_indexes


def my_skeleton(image3D):
    """
    Make from 3D image a skeleton form of it
    :param image3D:
    :return: 3D ndarray
    """
    n = 5
    while n > 0:
        border_index = determine_index_of_border_points(image3D)
        delete_border_points("U", border_index, image3D)
        n -= 1
        #delete_border_points("D", border_index, image3D)

# def contour(image):
#     row, col, rgb = image.shape
#
#     for i in range(row):
#         for j in range(col):
#             if image[i, j, 0] == 255:
#                 if image[i + 1, j, 0] != 255 or image[i - 1, j, 0] != 255 or image[i, j + 1, 0] != 255 or image[i, j - 1, 0] \
#                         != 255:
#                     image[i, j] = [255, 0, 0]
#
#     outim = Image.fromarray(image)
#     outim.save(f"contour.png")

def save_2D_binary_image(image, name):
    im = Image.fromarray(image * 255)
    im.save(f"{name}.png")

# Main

filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
dcm_image = pydicom.dcmread(filepath)
print('\r', "Threshold...", sep="", end="")
data = fast_threshold(dcm_image.pixel_array)
print('\r',"Into Binary...", sep="", end="")
data_ready = reduce_RGB_to_Binary(data)
save_2D_binary_image(data_ready[0], "BinarneZdjecie")
save_2D_binary_image(data_ready[1], "BinarneZdjecie1")
save_2D_binary_image(data_ready[2], "BinarneZdjecie2")
save_2D_binary_image(data_ready[3], "BinarneZdjecie3")
my_skeleton(data_ready)
save_2D_binary_image(data_ready[0], "BBB")
save_2D_binary_image(data_ready[1], "BBB1")
save_2D_binary_image(data_ready[2], "BBB2")
save_2D_binary_image(data_ready[3], "BBB3")

# print('\r',"Skeletonize...", sep="", end="")
# data = skeletonize_3d(data)
# print('\r',"Plotting...", sep="", end="")
# plot_3D_from_3D_binary_image(data, False)


