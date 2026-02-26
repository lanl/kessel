from argparse import Namespace

from kessel.workflows import default_ci_message, environment
from kessel.workflows.base.pip import Pip


class Format(Pip):
    steps = ["setup", "autopep8", "isort", "flake8", "mypy"]

    env = environment("format")

    def ci_message(self, args: Namespace) -> str:
        return default_ci_message("kessel", workflow="format")

    def setup(self, args: Namespace) -> None:
        """Setup"""
        self.requirements = self.workflow_dir / "requirements.txt"
        super().setup(args)

    def autopep8(self, args: Namespace) -> None:
        """Autoformat"""
        self.source(self.workflow_dir / "autopep8.sh")

    def isort(self, args: Namespace) -> None:
        """Import sorting"""
        self.source(self.workflow_dir / "isort.sh")

    def flake8(self, args: Namespace) -> None:
        """Linting"""
        self.source(self.workflow_dir / "flake8.sh")

    def mypy(self, args: Namespace) -> None:
        """Type checking"""
        self.source(self.workflow_dir / "mypy.sh")
