from kessel.workflows import Workflow
import shlex


class CMake(Workflow):
    steps = ["build", "test", "install"]

    def build(self, env, cmake_args=[]):
        """Build"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/build.sh", *cmake_args)

    def test(self, env):
        """Test"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/test.sh")

    def install(self, env):
        """Install"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/install.sh")

    def define(self, arg, value):
        if isinstance(value, bool):
            return f"-D{arg}={'ON' if value else 'OFF'}"
        else:
            return f"-D{arg}={value}"
