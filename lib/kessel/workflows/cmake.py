from kessel.workflows import Workflow


class CMakeWorkflow(Workflow):
    steps = ["build", "test", "install"]

    def build(self, env):
        """Build"""
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/cmake/build.sh")

    def test(self, env):
        """Test"""
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/cmake/test.sh")

    def install(self, env):
        """Install"""
        self.shenv.source("$KESSEL_ROOT/libexec/kessel/workflows/cmake/install.sh")
