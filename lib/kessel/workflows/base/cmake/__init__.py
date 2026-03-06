# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.workflows import Workflow, environment


class CMake(Workflow):
    steps = ["configure", "build", "test", "install"]

    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    install_dir = environment(Path.cwd() / "build" / "install")

    def configure(self, args: Namespace, cmake_args: list[str] = []) -> None:
        """Configure"""
        self.source(self.kessel_root /
                    "lib" / "kessel" / "workflows" / "base" / "cmake" / "cmake" / "configure.sh", *cmake_args)

    def build(self, args: Namespace, cmake_args: list[str] = [], targets: list[str] = []) -> None:
        """Build"""
        if targets:
            self.environ["KESSEL_CMAKE_TARGETS"] = "--target " + " ".join(targets)
        self.source(self.kessel_root /
                    "lib" / "kessel" / "workflows" / "base" / "cmake" / "cmake" / "build.sh", *cmake_args)
        if targets:
            self.environ["KESSEL_CMAKE_TARGETS"] = None

    def test(self, args: Namespace, ctest_args: list[str] = []) -> None:
        """Test"""
        self.source(self.kessel_root /
                    "lib" / "kessel" / "workflows" / "base" / "cmake" / "cmake" / "test.sh", *ctest_args)

    def install(self, args: Namespace) -> None:
        """Install"""
        self.source(self.kessel_root / "lib" / "kessel" / "workflows" / "base" / "cmake" / "cmake" / "install.sh")

    def define(self, arg: str, value: bool | str) -> str:
        if isinstance(value, bool):
            return f"-D{arg}={'ON' if value else 'OFF'}"
        else:
            return f"-D{arg}={value}"


class CTest(CMake):
    steps = ["build", "test", "install", "submit"]
    ctest_driver_script = environment(Path(os.environ["KESSEL_ROOT"]) /
                                      "share" / "kessel" / "cmake" / "ctest_driver.cmake")
    ctest_mode = environment("Continuous", variable="CTEST_MODE")
    submit_on_error = environment("true", variable="CTEST_SUBMIT_ON_ERROR")
    build_name = environment("default", variable="CTEST_BUILD_NAME")

    def build(self, args: Namespace, cmake_args: list[str] = [], targets: list[str] = []) -> None:
        """Build"""
        self.environ["REPORT_ERRORS"] = "ReportErrors" if self.submit_on_error == "true" else ""
        self.source(self.kessel_root / "lib" / "kessel" / "workflows" / "base" / "cmake" / "ctest" / "build.sh")

    def test(self, args: Namespace, ctest_args: list[str] = []) -> None:
        """Test"""
        self.environ["REPORT_ERRORS"] = "ReportErrors" if self.submit_on_error == "true" else ""
        self.source(self.kessel_root / "lib" / "kessel" / "workflows" / "base" / "cmake" / "ctest" / "test.sh")

    def submit_args(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", "--build-name", default=self.build_name)

    def submit(self, args: Namespace) -> None:
        """Submit"""
        if hasattr(self, "build_dir"):
            sanitize_script = self.kessel_root / \
                "lib" / "kessel" / "workflows" / "base" / "cmake" / "ctest" / "sanitize-xml"
            self.exec(f"{sanitize_script} {self.build_dir}")

        self.source(self.kessel_root / "lib" / "kessel" / "workflows" / "base" / "cmake" / "ctest" / "submit.sh")
