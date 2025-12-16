from kessel.workflows import *
from kessel.workflows.pip import Pip

class Docs(Pip):
    steps = ["setup", "html"]

    env = environment("docs")

    def ci_message(self, args):
        return default_ci_message("kessel", workflow="docs")

    def setup(self, args):
        """Setup"""
        self.requirements = self.source_dir / "doc" / "sphinx" / "requirements.txt"
        super().setup(args)

    def html(self, args):
        """Build HTML Documentation"""
        self.shenv.source(self.workflow_dir / "html.sh")
