from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize(r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\VesselsAnalyzer\cython_scripts\tree_from_skeleton_image.pyx"),
    include_dirs=[numpy.get_include()]
)
