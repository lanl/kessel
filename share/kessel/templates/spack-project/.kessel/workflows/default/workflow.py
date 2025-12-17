from kessel.workflows import *
from kessel.workflows.spack import BuildEnvironment
from kessel.workflows.cmake import CMake

class Default(BuildEnvironment, CMake):
    steps = ["env", "configure", "build", "test", "install"]
