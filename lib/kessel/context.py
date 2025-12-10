import itertools
import os
from pathlib import Path

from kessel.util import create_squashfs, symbolic_to_octal
from kessel.workflow import load_workflow_from_directory


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
        wf = load_workflow_from_directory(self.kessel_dir / "workflows" / name)
        wf.shenv = self.senv
        return wf

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

    @property
    def deployment_dir(self):
        deployment_dir = os.environ.get("KESSEL_DEPLOYMENT", default=None)
        return Path(deployment_dir) if deployment_dir else None

    @property
    def replicate_script(self):
        return self.deployment_dir / "bin" / "replicate"
