import matplotlib.pyplot as plt
import pydicom
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize_3d

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

    return image

def reduce_RGB_to_Binary(image):
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

def contour(image):
    row, col, rgb = image.shape

    for i in range(row):
        for j in range(col):
            if image[i, j, 0] == 255:
                if image[i + 1, j, 0] != 255 or image[i - 1, j, 0] != 255 or image[i, j + 1, 0] != 255 or image[i, j - 1, 0] \
                        != 255:
                    image[i, j] = [255, 0, 0]

    outim = Image.fromarray(image)
    outim.save(f"contour.png")

filepath = r"C:\Users\bkuba\Downloads\PracaLicencjacka-20220312T183334Z-002\PracaLicencjacka\Dane\dane_07.03.2022\Metformin_262p1_Power.dcm"
dcm_image = pydicom.dcmread(filepath)
print("Threshold..")
data = fast_threshold(dcm_image.pixel_array)
print("Into Binary..")
data = reduce_RGB_to_Binary(data)
print("Skeletonize...")
data = skeletonize_3d(data)
print("Plotting...")
plot_3D_from_3D_binary_image(data)


