from setuptools import setup
from Cython.Build import cythonize
import numpy


setup(
    ext_modules = cythonize("make_tree_from_skeleton.pyx"),
    include_dirs=[numpy.get_include()]
)

