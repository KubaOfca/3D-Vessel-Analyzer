import matplotlib.pyplot as plt
import pydicom
import numpy as np
from PIL import Image
import time
# from skimage.morphology import skeletonize_3d

import skeletonization3D

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)


def fast_threshold(image):

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


def reduce_RGB_to_binary(image):
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image


def plot_3D_from_3D_binary_image(image, save_to_file_from_diff_view=False):

    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    z, x, y = image.nonzero()
    ax.scatter(y, z, x, c="black", alpha=1, s=0.3)
    if save_to_file_from_diff_view:
        for angle in range(0, 360, 20):
            ax.view_init(elev=50., azim=angle)
            plt.savefig(f"angle{angle}.png")
    plt.show()


def save_2D_binary_image(image, name):
    im = Image.fromarray(image * 255)
    im.save(f"{name}.png")


def main():
    filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
    dcm_image = pydicom.dcmread(filepath)
    print('\r', "Threshold...", sep="", end="")
    data = fast_threshold(dcm_image.pixel_array)
    print('\r', "Into Binary...", sep="", end="")
    data_with_black_panel_start_end = np.zeros(shape=(data.shape[0] + 2, data.shape[1], data.shape[2]), dtype=np.uint8)
    data_with_black_panel_start_end[1:data_with_black_panel_start_end.shape[0]-1] = reduce_RGB_to_binary(data)
    print('\r', "Skeletonization...", sep="", end="")
    # check exec time
    start_time = time.time()
    data = skeletonization3D.make_3D_skeleton(data_with_black_panel_start_end)
    end_time = time.time() - start_time
    print('\r', f"[Skeletonization] Exec time {end_time}", sep="", end="")


main()


