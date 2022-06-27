import numpy
import numpy as np
from PIL import Image


def vr(image, tumor):
    foreground = np.count_nonzero(image == 1)
    return (foreground/tumor) * 100


def threshold(image):
    tumor = np.logical_and(image[:, :, :, 0] != 0,
                           image[:, :, :, 1] != 0,
                           image[:, :, :, 2] != 0,)
    tumor_volume = np.count_nonzero(image[tumor])
    background = np.logical_and(image[:, :, :, 0] == image[:, :, :, 1],
                                image[:, :, :, 1] == image[:, :, :, 2])
    image[background] = [0, 0, 0]
    image[np.logical_not(background)] = [1, 0, 0]
    return tumor_volume


def make_RGB_image_binary(image):
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image


def save_one_2D_binary_image(image, name):
    im = Image.fromarray(image)
    im.save(f"{name}.png")


def save_series_2D_binary_image(image, basename):
    n = image.shape[0]
    for i in range(n):
        im = Image.fromarray(image[i]*255)
        im.save(f"{basename}{i}.png")
