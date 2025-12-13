from kessel.workflows import *
from kessel.workflows.pip import Pip

class Format(Pip):
    steps = ["setup", "autopep8", "flake8", "mypy"]

    env = environment("format")
    system = environment("local")

    def ci_message(self):
        self.shenv.eval("kessel_ci_message", "kessel", self.system, "", "docs")

    def setup(self, args):
        """Setup"""
        self.requirements = self.workflow_dir / "requirements.txt"
        super().setup(args)

    def autopep8(self, args):
        """Autoformat"""
        self.shenv.source(self.workflow_dir / "autopep8.sh")

    def flake8(self, args):
        """Linting"""
        self.shenv.source(self.workflow_dir / "flake8.sh")

    def mypy(self, args):
        """Type checking"""
        self.shenv.source(self.workflow_dir / "mypy.sh")
