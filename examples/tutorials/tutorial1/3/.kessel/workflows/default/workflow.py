from kessel.workflows import *

class Default(Workflow):
    steps = ["configure", "build"]

    build_dir = environment("build")
    build_type = environment("Release")

    def configure_args(self, parser):
        parser.add_argument(
            "-B", "--build-dir",
            default=self.build_dir
        )
        parser.add_argument(
            "--build-type",
            default=self.build_type,
            choices=["Debug", "Release", "RelWithDebInfo"]
        )

    @collapsed
    def configure(self, args):
        """Configure"""
        self.exec(f"rm -rf {self.build_dir}")
        self.exec(f"cmake -B {self.build_dir} -S . -DCMAKE_BUILD_TYPE={args.build_type}")

    def build(self, args):
        """Build"""
        self.exec(f"cmake --build {self.build_dir} --parallel")
