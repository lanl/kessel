from kessel.workflows import *


class Default(Workflow):
    steps = ["configure", "build"]

    @collapsed
    def configure(self, args):
        """Configure"""
        self.exec("rm -rf build")
        self.exec("cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug")

    def build(self, args):
        """Build"""
        self.exec("cmake --build build --parallel")
