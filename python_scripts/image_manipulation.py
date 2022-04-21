import numpy as np
from PIL import Image


def vr(image):
    foreground = np.count_nonzero(image == 1)
    depth, height, width = image.shape
    return foreground/(depth*height*width)


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
        im = Image.fromarray(image[i])
        im.save(f"{basename}{i}.png")