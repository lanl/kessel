from kessel.workflows import *
from kessel.workflows.cmake import CMake
from kessel.workflows.spack import BuildEnvironment


class Default(BuildEnvironment, CMake):
    steps = ["env", "configure", "build", "test", "install"]
