from kessel.workflows import environment, default_ci_message
from kessel.workflows.pip import Pip
from argparse import Namespace

class Docs(Pip):
    steps = ["setup", "html"]

    env = environment("docs")

    def ci_message(self, args: Namespace) -> None:
        return default_ci_message("kessel", workflow="docs")

    def setup(self, args: Namespace) -> None:
        """Setup"""
        self.requirements = self.source_dir / "doc" / "sphinx" / "requirements.txt"
        super().setup(args)

    def html(self, args: Namespace) -> None:
        """Build HTML Documentation"""
        self.shenv.source(self.workflow_dir / "html.sh")
