from kessel.workflows import Workflow, environment
import shlex
import os
from pathlib import Path


class CMake(Workflow):
    steps = ["build", "test", "install"]

    def build(self, args, cmake_args=[]):
        """Build"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/build.sh", *cmake_args)

    def test(self, args, ctest_args=[]):
        """Test"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/test.sh", *ctest_args)

    def install(self, args):
        """Install"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/cmake/install.sh")

    def define(self, arg, value):
        if isinstance(value, bool):
            return f"-D{arg}={'ON' if value else 'OFF'}"
        else:
            return f"-D{arg}={value}"


class CTest(CMake):
    steps = ["build", "test", "install", "submit"]
    ctest_driver_script = environment(Path(os.environ["KESSEL_ROOT"]) / "share/kessel/cmake/ctest_driver.cmake")
    ctest_mode = environment("Continuous", variable="CTEST_MODE")
    submit_on_error = environment("true", variable="CTEST_SUBMIT_ON_ERROR")
    build_name = environment("default", variable="CTEST_BUILD_NAME")

    def build(self, args):
        """Build"""
        self.shenv["REPORT_ERRORS"] = "ReportErrors" if self.submit_on_error == "true" else ""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/ctest/build.sh")

    def test(self, args, ctest_args=[]):
        """Test"""
        self.shenv["REPORT_ERRORS"] = "ReportErrors" if self.submit_on_error == "true" else ""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/ctest/test.sh")

    def submit_args(self, parser):
        parser.add_argument("-n", "--build-name", default=self.build_name)

    def submit(self, args):
        """Submit"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/ctest/submit.sh")
