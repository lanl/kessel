import grp
import itertools
import os
import re
import subprocess
import tempfile
from pathlib import Path

from kessel import KESSEL_VERSION
from kessel.config import KesselConfig
from kessel.util import create_squashfs, symbolic_to_octal
from kessel.workflow import load_workflow_from_directory

from ruamel.yaml import YAML


class Context(object):
    def __init__(self, senv):
        self.senv = senv

    @property
    def kessel_dir(self):
        canditates = itertools.chain([Path.cwd()], Path.cwd().parents)
        for d in canditates:
            path = d / ".kessel"
            if path.exists() and path.is_dir():
                return path
        return None

    @property
    def workflows(self):
        d = self.kessel_dir
        if d:
            wd = d / "workflows"
            if wd.exists() and wd.is_dir():
                for f in wd.iterdir():
                    if f.is_dir():
                        yield f.name

    def load_workflow(self, name):
        return load_workflow_from_directory(self.kessel_dir / "workflows" / name)

    @property
    def workflow(self):
        return os.environ.get("KESSEL_WORKFLOW", "default")

    @workflow.setter
    def workflow(self, value):
        if value is None:
            self.senv.unset_env_var("KESSEL_WORKFLOW")
            return

        if self.workflow != value:
            self.senv.echo(f"Activating {value} workflow")
            self.senv.set_env_var("KESSEL_WORKFLOW", value)

    @property
    def workflow_config(self):
        try:
            return self.load_workflow(self.workflow)
        except FileNotFoundError:
            return None

    @property
    def build_env(self):
        return Path(os.environ.get("KESSEL_BUILD_ENV", self.build_dir / "build_env.sh"))

    @build_env.setter
    def build_env(self, value):
        self.senv.set_env_var("KESSEL_BUILD_ENV", Path(value).resolve())

    @property
    def pipeline_state(self):
        return os.environ.get("KESSEL_PIPELINE_STATE", None)

    @pipeline_state.setter
    def pipeline_state(self, value):
        self.senv.set_env_var("KESSEL_PIPELINE_STATE", value)

    @property
    def kessel_root(self):
        return Path(os.environ["KESSEL_ROOT"])

    @property
    def kessel_config_dir(self):
        return self.kessel_root / "etc" / "kessel"

    def kessel_template_dir(self, system=None):
        if system:
            return self.kessel_config_dir / system / "templates"
        return self.kessel_config_dir / "templates"

    @property
    def deployment_dir(self):
        deployment_dir = os.environ.get("KESSEL_DEPLOYMENT", default=None)
        return Path(deployment_dir) if deployment_dir else None

    @deployment_dir.setter
    def deployment_dir(self, value):
        d = Path(value).resolve()
        config = KesselConfig(d / ".kessel.yaml")
        if self.deployment_dir != d:
            self.senv.echo(f"Activating deployment at {d}")
        self.senv.set_env_var("SPACK_USER_CACHE_PATH", f"{d}/.spack")
        self.senv.unset_env_var("SPACK_DISABLE_LOCAL_CONFIG")
        self.senv.set_env_var("SPACK_USER_CONFIG_PATH", "$KESSEL_CONFIG_DIR")
        self.senv.set_env_var("SPACK_SKIP_MODULES", "true")
        self.senv.set_env_var("KESSEL_DEPLOYMENT", d)
        self.senv.set_env_var(
            "KESSEL_PARENT_DEPLOYMENT", config.parent if config.parent else d
        )
        self.senv.source("$KESSEL_DEPLOYMENT/spack/share/spack/setup-env.sh")

    @property
    def system(self):
        return os.environ.get("KESSEL_SYSTEM", default="local")

    @system.setter
    def system(self, value):
        if self.deployment_dir:
            sys_dir = self.deployment_dir / "environments" / value
            if not sys_dir.exists():
                raise Exception(f"Unknown system '{value}'!")
        elif value != "local":
            raise Exception("No active deployment!")
        if self.system != value:
            self.senv.echo(f"Activating {value} system")
        self.senv.set_env_var("KESSEL_SYSTEM", value)
        self.senv.set_env_var(
            "SPACK_SYSTEM_CONFIG_PATH", "$KESSEL_CONFIG_DIR/$KESSEL_SYSTEM"
        )

    @property
    def environment(self):
        return os.environ.get("KESSEL_ENVIRONMENT", default="default")

    @environment.setter
    def environment(self, value):
        self.senv.set_env_var("KESSEL_ENVIRONMENT", value)

    @property
    def config(self):
        return KesselConfig(self.deployment_dir / ".kessel.yaml")

    @property
    def file_permissions(self):
        return symbolic_to_octal(
            os.environ.get("KESSEL_PERMISSIONS", default="u=rwX,g=rX,o="),
            directory=False,
        )

    @property
    def directory_permissions(self):
        return symbolic_to_octal(
            os.environ.get("KESSEL_PERMISSIONS", default="u=rwX,g=rX,o="),
            directory=True,
        )

    @property
    def group(self):
        grp_name = os.environ.get("KESSEL_GROUP", default=f"{os.environ['USER']}")
        return grp.getgrnam(grp_name).gr_gid

    @property
    def replicate_sqfs(self):
        return self.deployment_dir / ".replicate.sqfs" if self.deployment_dir else None

    def replicate(self, dest):
        print("Creating deployment copy...")
        print(f"  src: {self.deployment_dir}")
        print(f"  dst: {dest}")
        cmd = [
            "rsync",
            "-a",
            "--no-p",
            "--no-g",
            "--chmod=ugo=rwX",
            "--exclude='.env'",
            "--exclude='spack-mirror'",
            "--exclude='spack-bootstrap'",
            "--exclude='/spack'",
            "--exclude='*spack.lock'",
            "--exclude='*.spack-env*'",
            f"{self.deployment_dir}/",
            dest,
        ]
        print(" ".join(cmd))
        subprocess.run(" ".join(cmd), shell=True)
        cmd2 = [
            "rsync",
            "-a",
            "--no-p",
            "--no-g",
            "--chmod=ugo=rwX",
            '--include={"*__pycache__*","*.pyc"}',
            '--include="etc/spack/**"',
            '--include="lib/spack/**"',
            f"--exclude-from={self.deployment_dir}/spack/.gitignore",
            f"{self.deployment_dir}/spack/",
            f"{dest}/spack",
        ]
        print(" ".join(cmd2))
        subprocess.run(" ".join(cmd2), shell=True)

        replica_config = {
            "kessel": {
                "version": KESSEL_VERSION,
                "build": self.config.build.to_dict(),
                "mirror": self.config.mirror.to_dict(),
                "parent": str(self.deployment_dir),
            }
        }

        replica_config_file = Path(dest) / ".kessel.yaml"

        with open(replica_config_file, "w") as f:
            yaml = YAML(typ="safe")
            yaml.default_flow_style = False
            yaml.width = 256
            yaml.dump(replica_config, f)

    def create_replicate_squashfs(self, dest):
        with tempfile.TemporaryDirectory() as d:
            if Path(dest).exists():
                os.remove(dest)
            self.replicate(d)
            create_squashfs(d, dest)

        try:
            os.chown(dest, -1, self.group)
            os.chmod(dest, self.file_permissions)
        except BaseException:
            pass
