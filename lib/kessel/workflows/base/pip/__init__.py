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

from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.workflows import Workflow, collapsed, environment


class Pip(Workflow):
    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    pip_env = environment("default")
    requirements = environment("requirements.txt")

    def setup_args(self, parser: ArgumentParser) -> None:
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.pip_env, dest="pip_env")
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)

    @collapsed
    def setup(self, args: Namespace) -> None:
        """Setup"""
        self.source(self.kessel_root / "lib/kessel/workflows/base/pip/setup.sh")
