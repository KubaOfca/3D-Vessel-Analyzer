import numpy
cimport numpy
cimport cython
import numpy as np
from cpython cimport array
ctypedef numpy.uint8_t IMAGE3D_UINT8_t
ctypedef numpy.int32_t BORDERPOINTS_INT32_t

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
    cdef numpy.ndarray[BORDERPOINTS_INT32_t, ndim=2] border_points
    cdef char sign = 'U'
    cdef int n = 5
    cdef int _

    for _ in range(n):
        border_points = determine_border_points(image3D)
        delete_border_points(sign, border_points, image3D)
        #delete_border_points("D", border_index, image3D)
    return image3D
