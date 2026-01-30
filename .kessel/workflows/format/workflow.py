from kessel.workflows import environment, default_ci_message
from kessel.workflows.pip import Pip
from argparse import Namespace

class Format(Pip):
    steps = ["setup", "autopep8", "flake8", "mypy"]

    env = environment("format")

    def ci_message(self, args: Namespace) -> str:
        return default_ci_message("kessel", workflow="format")

    def setup(self, args: Namespace) -> None:
        """Setup"""
        self.requirements = self.workflow_dir / "requirements.txt"
        super().setup(args)

    def autopep8(self, args: Namespace) -> None:
        """Autoformat"""
        self.shenv.source(self.workflow_dir / "autopep8.sh")

    def flake8(self, args: Namespace) -> None:
        """Linting"""
        self.shenv.source(self.workflow_dir / "flake8.sh")

    def mypy(self, args: Namespace) -> None:
        """Type checking"""
        self.shenv.source(self.workflow_dir / "mypy.sh")
