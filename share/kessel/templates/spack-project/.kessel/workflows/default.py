from kessel.workflows import *
from kessel.workflows.base.cmake import CMake
from kessel.workflows.base.spack import BuildEnvironment


class Default(BuildEnvironment, CMake):
    steps = ["env", "configure", "build", "test", "install"]
