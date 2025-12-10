from kessel.workflows import Workflow, state, collapsed
from pathlib import Path
import argparse


class SpackWorkflow(Workflow):
    steps = ["env", "configure"]

    state("environment", default="default")
    state("source_dir", default=Path.cwd())
    state("build_dir", default=Path.cwd() / "build")
    state("install_dir", default=Path.cwd() / "build" / "install")
    state("project_name")
    state("project_spec")

    def options(self, step_idx, step_name, parser, env):
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.environment)
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)
        parser.add_argument("-I", "--install-dir", default=self.install_dir)
        parser.add_argument("spec", nargs=argparse.REMAINDER, default=self.project_spec)

    def prepare_env(self, args):
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/spack/prepare_env.sh")

    def install_env(self, args):
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/spack/install_env.sh")

    @collapsed
    def env(self, args):
        """Prepare Environment"""
        self.prepare_env(args)
        self.install_env(args)

    def configure(self, args):
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/spack/configure.sh")
