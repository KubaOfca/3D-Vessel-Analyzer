import numpy
cimport numpy
cimport cython
import time


ctypedef numpy.uint8_t IMAGE3D_UINT8_t
ctypedef numpy.int64_t BORDERPOINTS_INT64_t

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

    cdef int num_base_mask = len(MASKS['U'])

    for base_maks in range(num_base_mask):
        z, y, x = numpy.where(arr == 0)
        zeros_index_list = [(z[i], y[i], x[i]) for i in range(len(x))]
        if not all(x in zeros_index_list for x in MASKS['U'][base_maks]["0"]):
            continue
        z, y, x = numpy.where(arr == 1)
        one_index_list = [(z[i], y[i], x[i]) for i in range(len(x))]
        if not all(x in one_index_list for x in MASKS['U'][base_maks]["1"]):
            continue
        if MASKS['U'][base_maks]["X"] and not any(x in one_index_list for x in MASKS['U'][base_maks]["X"]):
            continue

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
def delete_border_points(char which_side, numpy.ndarray[BORDERPOINTS_INT64_t, ndim=2] border_points,
                         numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):

    cdef int z
    cdef int y
    cdef int x
    cdef numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] border_point_and_neighborhood_3x3x3

    for i in range(border_points.shape[0]):
        z = border_points[i][0]
        y = border_points[i][1]
        x = border_points[i][2]
        border_point_and_neighborhood_3x3x3 = image3D[z-1:z+2, y-1:y+2, x-1:x+2]
        if is_match_mask(border_point_and_neighborhood_3x3x3):
            image3D[z, y, x] = 0
            #remove index ?


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

    cdef numpy.ndarray[BORDERPOINTS_INT64_t, ndim=2] border_points
    cdef int number_of_foreground_points
    cdef int number_of_border_points

    border_points = numpy.zeros(shape=(5_000_000, 3), dtype=numpy.int64)
    z, y, x = numpy.where(image3D == 1)
    number_of_foreground_points = len(x)

    for i in range(number_of_foreground_points):
        if is_border_point(z[i], y[i], x[i], image3D):
            border_points[number_of_border_points, 0] = z[i]
            border_points[number_of_border_points, 1] = y[i]
            border_points[number_of_border_points, 2] = x[i]
            number_of_border_points = number_of_border_points + 1

    return border_points[:number_of_border_points]


@cython.wraparound(False)
@cython.boundscheck(False)
def make_3D_skeleton(numpy.ndarray[IMAGE3D_UINT8_t, ndim=3] image3D):
    # jaki jest po zwroceniu typ border pointsa ? lista czy np array

    cdef char sign = 'U' # because str is default
    cdef int n = 5
    for _ in range(n):
        border_points = determine_border_points(image3D)
        delete_border_points(sign, border_points, image3D)
        #delete_border_points("D", border_index, image3D)
    return image3D


