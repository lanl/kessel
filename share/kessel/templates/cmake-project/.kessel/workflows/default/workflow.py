from kessel.workflows import *
from kessel.workflows.cmake import CMake

class Default(CMake):
    steps = ["configure", "build", "test"]
