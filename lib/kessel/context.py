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

    def reset(self):
        setup_script = os.environ.get("KESSEL_SETUP_SCRIPT")
        for v in [e for e in os.environ if e.startswith("KESSEL_")]:
            self.senv.unset_env_var(v)
        self.senv.source(setup_script)

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
    def run_state(self):
        return os.environ.get("KESSEL_RUN_STATE", None)

    @run_state.setter
    def run_state(self, value):
        self.senv.set_env_var("KESSEL_RUN_STATE", value)

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
        config = KesselConfig(d)
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
        self.senv.source("$KESSEL_DEPLOYMENT/kessel/share/kessel/setup-env.sh")

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
    def config(self):
        return KesselConfig(self.deployment_dir)

    @property
    def replicate_script(self):
        return self.deployment_dir / ".kessel" / "replicate"
