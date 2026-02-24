from kessel.workflows import *
from kessel.workflows.base.cmake import CMake

class Default(CMake):
    steps = ["configure", "build", "test"]
