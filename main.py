import matplotlib.pyplot as plt
import pydicom
import sys
import cv2
import math
import numpy as np
import os
from PIL import Image

# !!! Useful code !!!

# time measure !
# import timeit
# t = timeit.Timer("your_way()", "from __main__ import your_way")
# print t.timeit(number=1)

# print all result in console
# np.set_printoptions(threshold=sys.maxsize)

####

def fast_threshold(image):
    R = [(120, 255), (0, 105), (0, 255)]
    for panel in range(39):
        red_range = np.logical_and(R[0][0] < image[panel, :, :, 0], image[panel, :, :, 0] < R[0][1])
        green_range = np.logical_and(R[1][0] < image[panel, :, :, 1], image[panel, :, :, 1] < R[1][1])
        blue_range = np.logical_and(R[2][0] < image[panel, :, :, 2], image[panel, :, :, 2] < R[2][1])
        valid_range = np.logical_and(red_range, green_range, blue_range)

        image[panel][valid_range] = [255, 255, 255]
        image[panel][np.logical_not(valid_range)] = [0, 0, 0]

        outim = Image.fromarray(image[panel, :, 100:])
        outim.save(fr".\images\fast_threshold\fast_{panel}.png")


filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
dcm_image = pydicom.dcmread(filepath)

fast_threshold(dcm_image.pixel_array)





