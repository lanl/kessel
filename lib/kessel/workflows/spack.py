from kessel.workflows import Workflow, collapsed, environment
from pathlib import Path
import argparse
import shlex
import sys
import getpass
import grp
import os


class BuildEnvironment(Workflow):
    steps = ["env", "configure"]

    spack_env = environment("default")
    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    install_dir = environment(Path.cwd() / "build" / "install")
    project_spec = environment()

    def init(self):
        super().init()
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack/init.sh")

    def ci_message(self):
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack/ci_message.sh", *sys.argv)

    def prepare_env(self, args):
        self.spack_env = args.env
        self.source_dir = args.source_dir
        self.build_dir = args.build_dir
        if args.spec:
            self.project_spec = args.spec
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack/prepare_env.sh")

    def install_env(self, args):
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack/install_env.sh")

    def env_args(self, parser):
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.spack_env)
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)
        parser.add_argument("spec", nargs=argparse.REMAINDER, default=self.project_spec)

    @collapsed
    def env(self, args):
        """Prepare Environment"""
        self.prepare_env(args)
        self.install_env(args)

    def configure_args(self, parser):
        parser.add_argument("-I", "--install-dir", default=self.install_dir)

    def configure(self, args):
        """Configure"""
        self.install_dir = args.install_dir
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack/configure.sh")


class Deployment(Workflow):
    steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]

    deployment_config = environment(Path.cwd())
    deployment = environment(Path.cwd() / "build")
    permissions = environment("u=rwX,g=rX,o=")
    user = environment(getpass.getuser())
    group = environment(grp.getgrgid(os.getgid()).gr_name)
    system = environment("local")

    spack_url = "https://github.com/spack/spack.git"
    spack_ref = "develop"
    build_roots = False
    env_views = False
    require_git_mirrors = False
    mirror_exclude: list[str] = []
    build_exclude: list[str] = []

    def setup_args(self, parser):
        parser.add_argument("-D", "--deployment", default=self.deployment)
        parser.add_argument("system", default=self.system)

    def setup(self, args):
        """Setup"""
        self.deployment = args.deployment
        self.system = args.system

        os.umask(0o007)
        self.deployment.mkdir(parents=True, exist_ok=True)

        with open(self.deployment_config / "spack.yaml", "r") as f:
            for line in f:
                if line.startswith("git:"):
                    self.spack_url = line[line.find(':') + 1:].strip()
                elif line.startswith("ref:"):
                    self.spack_ref = line[line.find(':') + 1:].strip()

        self.shenv["SPACK_CHECKOUT_URL"] = self.spack_url
        self.shenv["SPACK_CHECKOUT_REF"] = self.spack_ref

        # generate activate.sh for deployment
        activate_template = self.kessel_root / "libexec" / "kessel" / \
            "workflows" / "spack_deployment" / "activate.sh.in"

        with open(activate_template, "r") as src, open(self.deployment / "activate.sh", "w") as dst:
            for line in src:
                line = line.replace("@KESSEL_PARENT_DEPLOYMENT@", "$KESSEL_DEPLOYMENT")
                line = line.replace("@KESSEL_SYSTEM@", self.system)
                print(line.rstrip(), file=dst)

        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack_deployment/setup.sh")

    def bootstrap(self, args):
        """Bootstrap"""
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack_deployment/bootstrap.sh")

    def mirror(self, args):
        """Create Source Mirror"""

        mirror_exclude_file = self.deployment / "config" / "mirror.exclude"
        self.shenv.eval(f'mirror_exclude_file="{mirror_exclude_file}"')

        if self.mirror_exclude:
            with open(mirror_exclude_file, "w") as f:
                for pkg in self.mirror_exclude:
                    print(pkg, file=f)
        elif mirror_exclude_file.is_file():
            mirror_exclude_file.unlink()

        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack_deployment/mirror.sh")

    def envs(self, args):
        """Build Environments"""
        self.shenv["KESSEL_BUILD_ROOTS"] = "true" if self.build_roots else "false"
        self.shenv["KESSEL_ENV_VIEWS"] = "true" if self.env_views else "false"
        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack_deployment/envs.sh")

    def finalize(self, args):
        """Finalize"""
        for pkg in self.build_exclude:
            self.shenv.eval(f"spack uninstall -y --all --dependents {shlex.quote(pkg)} || true")

        self.shenv.source(self.kessel_root / "libexec/kessel/workflows/spack_deployment/finalize.sh")
