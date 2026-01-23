from kessel.workflows import Workflow, collapsed, environment, default_ci_message, git
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
    git_mirrors: list[str] = []

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
            project,
            system=system,
            workflow=self.workflow,
            pre_alloc_init=pre_alloc_init,
            post_alloc_init=post_alloc_init)

    def prepare_env(self, args):
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "prepare_env.sh"))
        for p in self.git_mirrors:
            wdir = self.source_dir / p
            repo_path = Path(git(["rev-parse", "--absolute-git-dir"], cwd=wdir))
            self.print(f"Creating Git Mirror for '{wdir.name}' pointing to file://{repo_path}...")
            self.exec(f"spack config add \"packages:{wdir.name}:package_attributes:git:'file://{repo_path}'\"")

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
    bootstrap_mirror = False
    git_mirrors: list[str] = []
    mirror_exclude: list[str] = []
    build_exclude: list[str] = []

    def setup_args(self, parser):
        parser.add_argument("-D", "--deployment", default=self.deployment)
        parser.add_argument("-C", "--deployment_config", default=self.deployment_config)
        parser.add_argument("system", default=self.system)

    def clone_and_sync(self, src_checkout, dest):
        """Clone and sync a git repository with efficient mirroring."""
        try:
            src = git(["rev-parse", "--absolute-git-dir"], cwd=src_checkout)
            src_rev = git(["rev-parse", "HEAD"], cwd=src_checkout)

            self.print(f"Syncing: {src_checkout} → {dest} (rev {src_rev[:8]})")
            git(["fetch", "--all", "--tags", "--prune", "--force"], cwd=src_checkout)

            dest = Path(dest)
            if dest.exists():
                shutil.rmtree(dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)

            self.print("  Creating mirror clone...")
            git(["clone", "--mirror", src, f"{dest}/.git"])
            git(["config", "--local", "--bool", "core.bare", "false"], cwd=f"{dest}/.git")

            os.makedirs(dest, exist_ok=True)
            git(["config", "--local", "core.worktree", ".."], cwd=f"{dest}/.git")
            git(["checkout", "--force", "HEAD"], cwd=dest)

            self.print("  Setting up tracking for remote branches...")
            remote_branches = git(["branch", "-r"], cwd=dest)
            count = 0

            for line in remote_branches.splitlines():
                branch = line.strip()
                if "->" in branch or not branch:
                    continue

                if branch.startswith("origin/"):
                    local_branch = branch.replace("origin/", "", 1)
                    if local_branch == "HEAD":
                        continue

                    # Create local branch tracking remote branch
                    git(["branch", "--track", local_branch, branch], cwd=dest, check=False)
                    count += 1

            self.print(f"  Set up {count} tracking branches")
            git(["checkout", src_rev], cwd=dest)
            self.print(f"  Successfully created mirror at {dest} at revision {src_rev[:8]}")
            return True
        except Exception as e:
            self.print(f"Error: {str(e)}")
            return False

    def setup(self, args):
        """Setup"""
        os.umask(0o007)
        self.deployment.mkdir(parents=True, exist_ok=True)
        config_dir = self.deployment / "config"
        envs_dir = self.deployment / "environments"

        # wipe any existing configuration and environments
        shutil.rmtree(config_dir, ignore_errors=True)
        shutil.rmtree(envs_dir, ignore_errors=True)
        config_dir.mkdir(exist_ok=True)
        envs_dir.mkdir(exist_ok=True)

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
            src = self.deployment_config / path
            if src.exists():
                self.clone_and_sync(src, self.deployment / path)

        if self.git_mirrors:
            with open(config_dir / "git_mirrors.yaml", "w") as dst:
                print("packages:", file=dst)
                for p in self.git_mirrors:
                    wdir = self.deployment / p
                    repo_path = Path(git(["rev-parse", "--absolute-git-dir"], cwd=wdir))
                    self.print(f"Creating Git Mirror for '{wdir.name}' pointing to file://{repo_path}...")
                    print(f"  {wdir.name}:\n    package_attributes:\n      git: 'file://{repo_path}'", file=dst)

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
        if self.bootstrap_mirror:
            self.exec('spack bootstrap mirror --binary-packages "${KESSEL_DEPLOYMENT}/spack-bootstrap" || true')
        self.shenv.unset_env_var("KESSEL_REQUIRE_SYSTEM_MIRROR")

    def mirror(self, args):
        """Create Source Mirror"""
        mirror_exclude_file = self.deployment / "config" / "mirror.exclude"
        self.exec(f'mirror_exclude_file="{mirror_exclude_file}"')

        if self.mirror_exclude:
            with open(mirror_exclude_file, "w") as f:
                for pkg in self.mirror_exclude:
                    print(pkg, file=f)
        elif mirror_exclude_file.is_file():
            mirror_exclude_file.unlink()

        self.shenv["KESSEL_REQUIRE_GIT_MIRRORS"] = "true" if self.require_git_mirrors else "false"
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "mirror.sh"))

    def envs(self, args):
        """Build Environments"""
        self.shenv["KESSEL_BUILD_ROOTS"] = "true" if self.build_roots else "false"
        self.shenv["KESSEL_ENV_VIEWS"] = "true" if self.env_views else "false"
        self.shenv["KESSEL_REQUIRE_GIT_MIRRORS"] = "true" if self.require_git_mirrors else "false"
        self.shenv.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "envs.sh"))

    def finalize(self, args):
        """Finalize"""
        for pkg in self.build_exclude:
            self.exec(f"spack uninstall -y --all --dependents {shlex.quote(pkg)} || true")

        self.shenv.source(
            self.kessel_root.joinpath(
                "libexec",
                "kessel",
                "workflows",
                "spack_deployment",
                "finalize.sh"))
