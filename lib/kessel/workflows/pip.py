from kessel.workflows import Workflow, state, collapsed
from pathlib import Path


class Pip(Workflow):
    state("source_dir", default=Path.cwd())
    state("build_dir", default=Path.cwd() / "build")
    state("environment", default="default")
    state("requirements", default="requirements.txt")

    def setup_args(self, parser):
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.environment)
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)

    @collapsed
    def setup(self, args):
        """Setup"""
        self.source_dir = args.source_dir
        self.build_dir = args.build_dir
        self.environment = args.env
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/pip_env/setup.sh")
