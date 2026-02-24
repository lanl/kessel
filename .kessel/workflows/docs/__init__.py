from argparse import Namespace

from kessel.workflows import default_ci_message, environment
from kessel.workflows.base.pip import Pip


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
