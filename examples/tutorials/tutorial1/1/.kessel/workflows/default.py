from kessel.workflows import *


class Default(Workflow):
    steps = ["configure", "build"]

    build_dir = environment("build-release")

    @collapsed
    def configure(self, args):
        """Configure"""
        self.exec(f"rm -rf {self.build_dir}")
        self.exec(f"cmake -B {self.build_dir} -S . -DCMAKE_BUILD_TYPE=Debug")

    def build(self, args):
        """Build"""
        self.exec(f"cmake --build {self.build_dir} --parallel")
