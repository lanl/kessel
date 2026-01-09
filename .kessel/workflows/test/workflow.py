from kessel.workflows import *

class Test(Workflow):
    steps = ["tutorials"]

    def tutorials(self, args):
        """Tutorials"""
        self.shenv["CTEST_OUTPUT_ON_FAILURE"] = "1"
        self.exec("rm -rf build_tutorials")
        self.exec("cmake -B build_tutorials -S examples/tutorials")
        self.exec("ctest --test-dir build_tutorials --output-junit tests.xml")
