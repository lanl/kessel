from kessel.workflows import *
from kessel.workflows.pip import Pip

class Docs(Pip):
    steps = ["setup", "html"]

    state("environment", default="docs")

    #def init():
    #    kessel_ci_message "kessel" "$KESSEL_SYSTEM" "$KESSEL_INIT" "$KESSEL_WORKFLOW" $@

    def setup(self, args):
        """Setup"""
        self.requirements = self.source_dir / "doc" / "sphinx" / "requirements.txt"
        super().setup(args)

    def html(self, args):
        """Build HTML Documentation"""
        self.shenv.source(self.workflow_dir / "html.sh")
