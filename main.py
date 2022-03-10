import matplotlib.pyplot as plt
import pydicom
import sys
import cv2
import math
import numpy as np
import os
from PIL import Image
# np.set_printoptions(threshold=sys.maxsize)


def slow_threshold_image(image):
    number_of_panels, number_of_rows, number_of_columns, rgb = image.pixel_array.shape
    for panel in range(number_of_panels):
        print(f"Changing panel no. {panel}")
        for row in range(number_of_rows):
            if row % 50 == 0:
                print(f"Row no: {row}")
            for col in range(number_of_columns):
                if image.pixel_array[panel, row, col, 0] >= 120 and image.pixel_array[panel, row, col, 1] <= 105:
                    image.pixel_array[panel, row, col] = 255
                else:
                    image.pixel_array[panel, row, col] = 0
        plt.axis("off")
        plt.imshow(image.pixel_array[panel, :, 100:].astype(np.uint8))
        plt.savefig(f"{panel}.png")

def fast_threshold(image):
    R = [(120, 255), (0, 105), (0, 255)]
    for panel in range(39):
        red_range = np.logical_and(R[0][0] < image[panel, :, :, 0], image[panel, :, :, 0] < R[0][1])
        green_range = np.logical_and(R[1][0] < image[panel, :, :, 1], image[panel, :, :, 1] < R[1][1])
        blue_range = np.logical_and(R[2][0] < image[panel, :, :, 2], image[panel, :, :, 2] < R[2][1])
        valid_range = np.logical_and(red_range, green_range, blue_range)

        image[panel][valid_range] = [255, 255, 255]
        image[panel][np.logical_not(valid_range)] = [0, 0, 0]

        outim = Image.fromarray(image[panel])
        outim.save(f"fast_{panel}.jpg")

filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
dcm_image = pydicom.dcmread(filepath)

#slow_threshold_image(dcm_image)
fast_threshold(dcm_image.pixel_array)





