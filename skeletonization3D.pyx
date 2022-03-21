import numpy
cimport numpy
cimport cython
import numpy as np
from cpython cimport array
ctypedef numpy.uint8_t IMAGE3D_UINT8_t
ctypedef numpy.int32_t BORDERPOINTS_INT32_t
# from PIL import Image
# import matplotlib.pyplot as plt
# import pydicom
# import time
# slow mask structure 120 sek
# cdef numpy.ndarray MASKS = numpy.array([[[[0, 0, 0],
#                                           [2, 2, 2],
#                                           [2, 2, 2]],
#                                          [[0, 0, 0],
#                                           [2, 1, 2],
#                                           [2, 1, 2]],
#                                          [[0, 0, 0],
#                                           [2, 2, 2],
#                                           [2, 2, 2]]]], dtype=numpy.uint8)

# MASKS = {
#     "U" : [{ "0" : [(0,0,0), (0,0,1), (0,0,2),
#                    (1,0,0), (1,0,1), (1,0,2),
#                    (2,0,0), (2,0,1), (2,0,2)],
#             "1" : [(1,1,1), (1,2,1)],
#             "X" : [(0,1,0), (0,1,1), (0,1,2),
#                    (0,2,0), (0,2,1), (0,2,2),
#                    (1,1,0), (1,1,2), (1,2,0),
#                    (1,2,2), (2,1,0), (2,1,1),
#                    (2,1,2), (2,2,0), (2,2,1),
#                    (2,2,2)]},]
#
# }
cdef array.array a = array.array('i', [0, 0, 0, 0, 0, 1, 0, 0, 2,
         1, 0, 0, 1, 0, 1, 1, 0, 2,
         2, 0, 0, 2, 0, 1, 2, 0, 2])
cdef int[:] ZEROS = a
cdef array.array b = array.array('i', [1, 1, 1, 1, 2, 1])
cdef int[:] ONES = b
cdef array.array c = array.array('i', [0, 1, 0, 0, 1, 1, 0, 1, 2,
     0, 2, 0, 0, 2, 1, 0, 2, 2,
     1, 1, 0, 1, 1, 2, 1, 2, 0,
     1, 2, 2, 2, 1, 0, 2, 1, 1,
     2, 1, 2, 2, 2, 0, 2, 2, 1,
     2, 2, 2])
cdef int[:] X = c

# slow version 120 sek
# @cython.wraparound(False)
# @cython.boundscheck(False)
# def check_single_mask(unsigned char [:, :, :] arr, int num_mask, bint x):
#     cdef int n = 3
#     for panel in range(n):
#         for row in range(n):
#             for col in range(n):
#                 if MASKS[num_mask, panel, row, col] != arr[panel, row, col] and MASKS[num_mask, panel, row, col] != 3:
#                     if (MASKS[num_mask, panel, row, col] == 0 and arr[panel, row, col] == 1) \
#                             or (MASKS[num_mask, panel, row, col] == 1 and arr[panel, row, col] == 0):
#                         return False
#                     if MASKS[num_mask, panel, row, col] == 2 and x == False and arr[panel, row, col] == 1:
#                         x = True
#     return x
#
# @cython.wraparound(False)
# @cython.boundscheck(False)
# def check_if_in(int num_mask):
#     for panel in range(3):
#         for row in range(3):
#             for col in range(3):
#                 if MASKS[num_mask, panel, row, col] == 2:
#                     return True
#     return False

@cython.wraparound(False)
@cython.boundscheck(False)
def is_match_mask(numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] arr):

    cdef int base_maks, i, j
    cdef int flaga = 0
    cdef int panel
    cdef int row
    cdef int col
    cdef int size_zeros
    cdef int size_ones
    cdef numpy.ndarray[BORDERPOINTS_INT32_t, ndim=1] zeros
    cdef numpy.ndarray[BORDERPOINTS_INT32_t, ndim=1] ones

    zeros = numpy.zeros(shape=(81), dtype=numpy.int32)
    ones = numpy.zeros(shape=(81), dtype=numpy.int32)

    for panel in range(3):
        for row in range(3):
            for col in range(3):
                if arr[panel, row, col] == 1:
                    zeros[size_zeros] = panel
                    zeros[size_zeros + 1] = row
                    zeros[size_zeros + 2] = col
                    size_zeros = size_zeros + 3
                else:
                    ones[size_ones] = panel
                    ones[size_ones + 1] = row
                    ones[size_ones + 2] = col
                    size_ones = size_ones + 3

    for i in range(0, len(ZEROS), 3):
        flaga = 0
        for j in range(0, len(zeros), 3):
            if zeros[j] == ZEROS[i] and zeros[j+1] == ZEROS[i+1] and zeros[j+2] == ZEROS[i+2]:
                flaga = 1
                break
        if flaga == 0:
            return False

    for i in range(0, len(ONES), 3):
        flaga = 0
        for j in range(0, len(ones), 3):
            if ones[j] == ONES[i] and ones[j + 1] == ONES[i + 1] and ones[j + 2] == ONES[i + 2]:
                flaga = 1
                break
        if flaga == 0:
            return False

    for i in range(0, len(X), 3):
        for j in range(0, len(ones), 3):
            if ones[j] == X[i] and ones[j + 1] == X[i + 1] and ones[j + 2] == X[i + 2]:
                return True
    return False


# slow version 120 sek
# def match_mask(unsigned char [:, :, :] arr):
#     """
#     Check if border points match to at least one given mask
#     :param arr:
#     :param side:
#     :return: True if match False if not
#     """
#     cdef int num_of_masks = MASKS.shape[0]
#     cdef bint x_condition = False
#     for mask_type in range(num_of_masks):
#         if check_if_in(mask_type):
#             x_condition = False
#         else:
#             x_condition = True
#         if check_single_mask(arr, mask_type, x_condition):
#             return True

@cython.wraparound(False)
@cython.boundscheck(False)
def delete_border_points(char which_side, numpy.ndarray[BORDERPOINTS_INT32_t, ndim=2] border_points,
                         numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):

    cdef int z
    cdef int y
    cdef int x
    cdef numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] border_point_and_neighborhood_3x3x3
    cdef int i

    for i in range(border_points.shape[0]):
        z = border_points[i][0]
        y = border_points[i][1]
        x = border_points[i][2]
        border_point_and_neighborhood_3x3x3 = image3D[z-1:z+2, y-1:y+2, x-1:x+2]
        if is_match_mask(border_point_and_neighborhood_3x3x3):
            image3D[z, y, x] = 0


@cython.wraparound(False)
@cython.boundscheck(False)
def is_border_point(int z, int y, int x, numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):

    if image3D[z, y, x - 1] == 0 or image3D[z, y, x + 1] == 0 \
       or image3D[z, y - 1, x] == 0 or image3D[z, y + 1, x] == 0 \
       or image3D[z - 1, y, x] == 0 or image3D[z + 1, y, x] == 0:

        return True

    return False


@cython.wraparound(False)
@cython.boundscheck(False)
def determine_border_points(numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):
    """
    Retrun a indexes of border points
    :param image:
    :return: list of tuples List[tuples()]
    """

    cdef numpy.ndarray[BORDERPOINTS_INT32_t, ndim=2] border_points
    cdef int number_of_foreground_points
    cdef int number_of_border_points
    cdef int i
    cdef int p = image3D.shape[0]
    cdef int r = image3D.shape[1]
    cdef int c = image3D.shape[2]
    cdef int panel, row, col

    border_points = numpy.zeros(shape=(2_000_000, 3), dtype=numpy.int32)

    for panel in range(p):
        for row in range(r):
            for col in range(c):
                if image3D[panel, row, col] == 1:
                    if is_border_point(panel, row, col, image3D):
                        border_points[number_of_border_points, 0] = panel
                        border_points[number_of_border_points, 1] = row
                        border_points[number_of_border_points, 2] = col
                        number_of_border_points = number_of_border_points + 1

    return border_points[:number_of_border_points]


@cython.wraparound(False)
@cython.boundscheck(False)
def make_3D_skeleton(numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):
    # jaki jest po zwroceniu typ border pointsa ? lista czy numpy array
    cdef numpy.ndarray[BORDERPOINTS_INT32_t, ndim=2] border_points
    cdef char sign = 'U' # because str is default
    cdef int n = 5
    cdef int _

    for _ in range(n):
        border_points = determine_border_points(image3D)
        delete_border_points(sign, border_points, image3D)
        #delete_border_points("D", border_index, image3D)
    return image3D

# def fast_threshold(image):
#
#     RGB_threshold = [(120, 255), (0, 105), (0, 255)]
#
#     red_range = numpy.logical_and(RGB_threshold[0][0] < image[:, :, :, 0], image[:, :, :, 0] < RGB_threshold[0][1])
#     green_range = numpy.logical_and(RGB_threshold[1][0] < image[:, :, :, 1], image[:, :, :, 1] < RGB_threshold[1][1])
#     blue_range = numpy.logical_and(RGB_threshold[2][0] < image[:, :, :, 2], image[:, :, :, 2] < RGB_threshold[2][1])
#     valid_range = numpy.logical_and(red_range, green_range, blue_range)
#
#     image[valid_range] = [255, 255, 255]
#     image[numpy.logical_not(valid_range)] = [0, 0, 0]
#
#     binary = numpy.logical_and(200 < image[:, :, :, 0], 255 >= image[:, :, :, 0])
#
#     image[binary] = [1, 1, 1]
#     image[numpy.logical_not(binary)] = [0, 0, 0]
#
#     return image[:, :, 100:]
#
#
# def reduce_RGB_to_binary(image):
#     image = numpy.delete(image, numpy.s_[1:3], 3).squeeze()
#     return image
#
# print("KURWAMAC")
# filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
# dcm_image = pydicom.dcmread(filepath)
# data = fast_threshold(dcm_image.pixel_array)
# data_with_black_panel_start_end = numpy.zeros(shape=(data.shape[0] + 2, data.shape[1], data.shape[2]), dtype=numpy.uint8)
# data_with_black_panel_start_end[1:data_with_black_panel_start_end.shape[0]-1] = reduce_RGB_to_binary(data)
# # check exec tim
# start_time = time.time()
# data = make_3D_skeleton(data_with_black_panel_start_end)
# end_time = time.time() - start_time
# print('\r', f"[Skeletonization] Exec time {end_time}")