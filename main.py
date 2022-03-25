import pydicom
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize_3d

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)

# global var
ROI = [(115, 1032), (169, 702)]


def threshold(image):
    background = np.logical_and(image[:, :, :, 0] == image[:, :, :, 1], image[:, :, :, 1] == image[:, :, :, 2])
    image[background] = [0, 0, 0]
    image[np.logical_not(background)] = [1, 0, 0]


def make_RGB_image_binary(image):
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image


def save_one_2D_binary_image(image, name):
    im = Image.fromarray(image*255)
    im.save(f"{name}.png")


def save_series_2D_binary_image(image, basename):
    n = image.shape[0]
    for i in range(n):
        im = Image.fromarray(image[i]*255)
        im.save(f"{basename}{i}.png")


def main():
    filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
    dcm_image = pydicom.dcmread(filepath)
    data = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
    threshold(data)
    data = make_RGB_image_binary(data)
    save_series_2D_binary_image(data, "binarka")
    data_with_black_panel_start_end = skeletonize_3d(data)
    save_series_2D_binary_image(data_with_black_panel_start_end, "szkielet_nowy")


main()


