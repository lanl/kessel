from kessel.workflows import Workflow, collapsed, environment, default_ci_message
from pathlib import Path
import argparse
import shlex
import sys
import getpass
import grp
import os
import shutil
import subprocess


def get_project_name_from_spec(spec):
    return subprocess.check_output(
        ["spack-python", "-c", f"spec = spack.spec.Spec('{spec}');print(spec.name)"]).decode('utf-8').strip()


class BuildEnvironment(Workflow):
    steps = ["env", "configure"]

    spack_env = environment("default")
    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    install_dir = environment(Path.cwd() / "build" / "install")
    project_spec = environment()

    def init(self):
        super().init()
        if ("KESSEL_DEPLOYMENT" not in os.environ or not Path(
                os.environ["KESSEL_DEPLOYMENT"]).exists()) and "SPACK_ROOT" not in os.environ:
            raise Exception("No active Spack installation!")

    def ci_message(self, parsed_args, pre_alloc_init="", post_alloc_init=""):
        if parsed_args.project_spec:
            project = get_project_name_from_spec(parsed_args.project_spec)
        else:
            project = get_project_name_from_spec(self.project_spec)
        system = os.environ.get("KESSEL_SYSTEM", default="local")
        return default_ci_message(
            project=project,
            system=system,
            workflow=self.workflow,
            pre_alloc_init=pre_alloc_init,
            post_alloc_init=post_alloc_init)

    def prepare_env(self, args):
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "prepare_env.sh"))

    def install_env(self, args):
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "install_env.sh"))

    def env_args(self, parser):
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.spack_env, dest="spack_env")
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)
        parser.add_argument("project_spec", nargs=argparse.REMAINDER, default=self.project_spec)

    @collapsed
    def env(self, args):
        """Prepare Environment"""
        self.prepare_env(args)
        self.install_env(args)

    def configure_args(self, parser):
        parser.add_argument("-I", "--install-dir", default=self.install_dir)

    @collapsed
    def configure(self, args):
        """Configure"""
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "configure.sh"))


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
    git_mirrors: list[str] = []
    mirror_exclude: list[str] = []
    build_exclude: list[str] = []

    def setup_args(self, parser):
        parser.add_argument("-D", "--deployment", default=self.deployment)
        parser.add_argument("system", default=self.system)

    def clone_and_sync(self, src_checkout, dest):
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "clone_and_sync.sh"), src_checkout, dest)

    def setup(self, args):
        """Setup"""
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

        # clone git mirrors
        for path in self.git_mirrors:
            self.clone_and_sync(self.deployment_config / path, self.deployment / path)

        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "setup.sh"))

    def bootstrap(self, args):
        """Bootstrap"""
        self.shenv.source(
            self.kessel_root.joinpath(
                "libexec",
                "kessel",
                "workflows",
                "spack_deployment",
                "bootstrap.sh"))

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

        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "mirror.sh"))

    def envs(self, args):
        """Build Environments"""
        self.shenv["KESSEL_BUILD_ROOTS"] = "true" if self.build_roots else "false"
        self.shenv["KESSEL_ENV_VIEWS"] = "true" if self.env_views else "false"
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "envs.sh"))

    def finalize(self, args):
        """Finalize"""
        for pkg in self.build_exclude:
            self.shenv.eval(f"spack uninstall -y --all --dependents {shlex.quote(pkg)} || true")

        self.shenv.source(
            self.kessel_root.joinpath(
                "libexec",
                "kessel",
                "workflows",
                "spack_deployment",
                "finalize.sh"))
