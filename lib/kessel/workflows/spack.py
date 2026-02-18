import argparse
import getpass
import grp
import os
import shlex
import shutil
import subprocess
from pathlib import Path

from kessel.workflows import EnvState, Workflow, collapsed, default_ci_message, environment, git


def get_project_name_from_spec(spec: EnvState | str) -> str:
    return subprocess.check_output(
        ["spack-python", "-c", f"spec = spack.spec.Spec('{spec}');print(spec.name)"]).decode('utf-8').strip()


def join_ssh_url(pathA, pathB):
    parts = pathA.split('/')
    partsB = pathB.split('/')
    for p in partsB:
        if p == '.': continue
        if p == '..':
          parts = parts[:-1]
          continue
        parts.append(p)
    return '/'.join(parts)


def resolve_relative_ssh_url(url):
    """handles a special case where the site configs repo is a relative URL to the deployment config repo"""
    if url.startswith("../"):
        base_url = git(["remote", "get-url", "origin"])
        return join_ssh_url(base_url, url)
    return url


class BuildEnvironment(Workflow):
    steps = ["env", "configure"]

    spack_env = environment("default")
    source_dir = environment(Path.cwd())
    build_dir = environment(Path.cwd() / "build")
    install_dir = environment(Path.cwd() / "build" / "install")
    project_spec = environment()
    git_mirrors: list[str] = []
    allow_lockfile_changes = False

    def init(self) -> None:
        super().init()
        if ("KESSEL_DEPLOYMENT" not in os.environ or not Path(
                os.environ["KESSEL_DEPLOYMENT"]).exists()) and "SPACK_ROOT" not in os.environ:
            raise Exception("No active Spack installation!")

    def ci_message(self, parsed_args, pre_alloc_init: str = "", post_alloc_init: str = "") -> str:
        if parsed_args.project_spec:
            project = get_project_name_from_spec(" ".join(parsed_args.project_spec))
        else:
            project = get_project_name_from_spec(self.project_spec)
        system = os.environ.get("KESSEL_SYSTEM", default="local")
        return default_ci_message(
            project,
            system=system,
            workflow=self.workflow,
            pre_alloc_init=pre_alloc_init,
            post_alloc_init=post_alloc_init)

    def prepare_env(self, args: argparse.Namespace) -> None:
        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "prepare_env.sh"))
        for p in self.git_mirrors:
            assert isinstance(self.source_dir, Path)
            wdir = self.source_dir / p

            git_out = git(["rev-parse", "--absolute-git-dir"], cwd=wdir)
            assert git_out is not None
            repo_path = Path(git_out)
            self.print(f"Creating Git Mirror for '{wdir.name}' pointing to file://{repo_path}...")
            self.exec(f"spack config add \"packages:{wdir.name}:package_attributes:git:'file://{repo_path}'\"")

    def install_env(self, args: argparse.Namespace) -> None:
        if self.allow_lockfile_changes or args.force:
            self.exec("spack concretize -f")
        else:
            self.exec("spack spec")

        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "install_env.sh"))

    def env_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-e", "--env", metavar="ENVIRONMENT", default=self.spack_env, dest="spack_env")
        parser.add_argument("-S", "--source-dir", default=self.source_dir)
        parser.add_argument("-B", "--build-dir", default=self.build_dir)
        parser.add_argument("-f", "--force", action="store_true", help="allow changes to Spack lockfile")
        parser.add_argument("project_spec", nargs=argparse.REMAINDER, default=self.project_spec)

    @collapsed
    def env(self, args: argparse.Namespace) -> None:
        """Prepare Environment"""
        self.prepare_env(args)
        self.install_env(args)

    def configure_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-I", "--install-dir", default=self.install_dir)

    @collapsed
    def configure(self, args: argparse.Namespace) -> None:
        """Configure"""
        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack", "configure.sh"))


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
    site_configs_url = ""
    site_configs_ref = "main"
    build_roots = False
    env_views = False
    require_system_mirrors = False
    require_git_mirrors = False
    bootstrap_mirror = False
    allow_replicate = True
    git_mirrors: list[str] = []
    mirror_exclude: list[str] = []
    build_exclude: list[str] = []

    def setup_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-D", "--deployment", default=self.deployment)
        parser.add_argument("-C", "--deployment_config", default=self.deployment_config)
        parser.add_argument("system", default=self.system)

    def clone_and_sync(self, src_checkout: str | Path, dest: str | Path) -> bool:
        """Clone and sync a git repository with efficient mirroring."""
        try:
            src = git(["rev-parse", "--absolute-git-dir"], cwd=src_checkout)
            src_rev = git(["rev-parse", "HEAD"], cwd=src_checkout)

            assert src_rev is not None
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

            assert remote_branches is not None
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
            assert src_rev is not None
            self.print(f"  Successfully created mirror at {dest} at revision {src_rev[:8]}")
            return True
        except Exception as e:
            self.print(f"Error: {str(e)}")
            return False

    def setup(self, args: argparse.Namespace) -> None:
        """Setup"""
        os.umask(0o007)

        assert isinstance(self.deployment, Path)
        self.deployment.mkdir(parents=True, exist_ok=True)
        config_dir = self.deployment / "config"
        envs_dir = self.deployment / "environments"

        # wipe any existing configuration and environments
        shutil.rmtree(config_dir, ignore_errors=True)
        shutil.rmtree(envs_dir, ignore_errors=True)
        config_dir.mkdir(exist_ok=True)
        envs_dir.mkdir(exist_ok=True)

        self.environ["SPACK_CHECKOUT_URL"] = resolve_relative_ssh_url(self.spack_url)
        self.environ["SPACK_CHECKOUT_REF"] = self.spack_ref
        self.environ["KESSEL_ALLOW_REPLICATE"] = "true" if self.allow_replicate else "false"

        if self.site_configs_url:
            self.environ["SITE_CONFIGS_CHECKOUT_URL"] = resolve_relative_ssh_url(self.site_configs_url)
            self.environ["SITE_CONFIGS_CHECKOUT_REF"] = self.site_configs_ref

        # generate activate.sh for deployment
        activate_template = self.kessel_root / "libexec" / "kessel" / \
            "workflows" / "spack_deployment" / "activate.sh.in"

        with open(activate_template, "r") as src, open(self.deployment / "activate.sh", "w") as dst:
            for line in src:
                line = line.replace("@KESSEL_PARENT_DEPLOYMENT@", "$KESSEL_DEPLOYMENT")
                line = line.replace("@KESSEL_SYSTEM@", str(self.system))
                print(line.rstrip(), file=dst)

        # clone git mirrors
        for path in self.git_mirrors:
            assert isinstance(self.deployment_config, Path)
            src_path = self.deployment_config / path
            if src_path.exists():
                self.clone_and_sync(src_path, self.deployment / path)

        if self.git_mirrors:
            with open(config_dir / "git_mirrors.yaml", "w") as dst:
                print("packages:", file=dst)
                for p in self.git_mirrors:
                    wdir = self.deployment / p

                    git_out = git(["rev-parse", "--absolute-git-dir"], cwd=wdir)
                    assert git_out is not None
                    repo_path = Path(git_out)
                    self.print(f"Setting Git attribute for '{wdir.name}' to file://{repo_path}...")
                    print(f"  {wdir.name}:\n    package_attributes:\n      git: 'file://{repo_path}'", file=dst)

        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "setup.sh"))

    def bootstrap(self, args: argparse.Namespace) -> None:
        """Bootstrap"""
        self.environ["KESSEL_REQUIRE_SYSTEM_MIRRORS"] = "true" if self.require_system_mirrors else "false"
        self.source(
            self.kessel_root.joinpath(
                "libexec",
                "kessel",
                "workflows",
                "spack_deployment",
                "bootstrap.sh"))
        if self.bootstrap_mirror:
            self.exec('spack bootstrap mirror --binary-packages "${KESSEL_DEPLOYMENT}/spack-bootstrap" || true')
        self.environ["KESSEL_REQUIRE_SYSTEM_MIRROR"] = None

    def mirror(self, args: argparse.Namespace) -> None:
        """Create Source Mirror"""
        assert isinstance(self.deployment, Path)
        self.environ["KESSEL_REQUIRE_SYSTEM_MIRRORS"] = "true" if self.require_system_mirrors else "false"
        mirror_exclude_file = self.deployment / "config" / "mirror.exclude"
        self.exec(f'mirror_exclude_file="{mirror_exclude_file}"')

        if self.mirror_exclude:
            with open(mirror_exclude_file, "w") as f:
                for pkg in self.mirror_exclude:
                    print(pkg, file=f)
        elif mirror_exclude_file.is_file():
            mirror_exclude_file.unlink()

        self.environ["KESSEL_REQUIRE_GIT_MIRRORS"] = "true" if self.require_git_mirrors else "false"
        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "mirror.sh"))
        self.environ["KESSEL_REQUIRE_SYSTEM_MIRROR"] = None

    def envs(self, args: argparse.Namespace) -> None:
        """Build Environments"""

        self.environ["KESSEL_BUILD_ROOTS"] = "true" if self.build_roots else "false"
        self.environ["KESSEL_ENV_VIEWS"] = "true" if self.env_views else "false"
        self.environ["KESSEL_REQUIRE_GIT_MIRRORS"] = "true" if self.require_git_mirrors else "false"
        self.source(self.kessel_root.joinpath("libexec", "kessel", "workflows", "spack_deployment", "envs.sh"))

    def finalize(self, args):
        """Finalize"""
        for pkg in self.build_exclude:
            self.exec(f"spack uninstall -y --all --dependents {shlex.quote(pkg)} || true")

        self.environ["KESSEL_ALLOW_REPLICATE"] = "true" if self.allow_replicate else "false"

        self.source(
            self.kessel_root.joinpath(
                "libexec",
                "kessel",
                "workflows",
                "spack_deployment",
                "finalize.sh"))
