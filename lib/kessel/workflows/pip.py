from kessel.workflows import Workflow, collapsed, environment
from pathlib import Path


class Pip(Workflow):
    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    pip_env = environment("default")
    requirements = environment("requirements.txt")

    def setup_args(self, parser):
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.pip_env)
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)

    @collapsed
    def setup(self, args):
        """Setup"""
        self.source_dir = args.source_dir
        self.build_dir = args.build_dir
        self.pip_env = args.env
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/pip_env/setup.sh")
