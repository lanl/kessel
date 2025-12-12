from kessel.workflows import *
from kessel.workflows.pip import Pip

class Docs(Pip):
    steps = ["setup", "html"]

    state("environment", default="docs")
    state("system", default="local")

    def ci_message(self):
        self.shenv.eval("kessel_ci_message", "kessel", self.system, "", "docs")

    def setup(self, args):
        """Setup"""
        self.requirements = self.source_dir / "doc" / "sphinx" / "requirements.txt"
        super().setup(args)

    def html(self, args):
        """Build HTML Documentation"""
        self.shenv.source(self.workflow_dir / "html.sh")
