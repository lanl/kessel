from kessel.workflows import *

class Default(Workflow):
    steps = ["configure", "build"]

    @collapsed
    def configure(self, args):
        """Configure"""
        self.shenv.eval("rm -rf build")
        self.shenv.eval("cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug")

    def build(self, args):
        """Build"""
        self.shenv.eval("cmake --build build --parallel")
