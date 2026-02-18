import itertools
import os
from pathlib import Path
from typing import Iterator

from kessel.util import ShellEnvironment
from kessel.workflows import Workflow, load_workflow_from_directory


class Context(object):
    def __init__(self, senv: ShellEnvironment) -> None:
        self.senv = senv
        self._workflow_config: Workflow | None = None

    def reset(self) -> None:
        self.workflow = None
        setup_script = os.environ.get("KESSEL_SETUP_SCRIPT")
        for v in [
            e for e in os.environ if e.startswith("KESSEL_") and e not in (
                "KESSEL_DEPLOYMENT",
                "KESSEL_PARENT_DEPLOYMENT",
                "KESSEL_SYSTEM",
                "KESSEL_CURRENT_SYSTEM")]:
            self.senv.unset_env_var(v)

        assert setup_script is not None
        self.senv.source(setup_script)

    @property
    def kessel_dir(self) -> Path | None:
        canditates = itertools.chain([Path.cwd()], Path.cwd().parents)
        for d in canditates:
            path = d / ".kessel"
            if path.exists() and path.is_dir():
                return path
        return None

    @property
    def workflows(self) -> Iterator[str]:
        d = self.kessel_dir
        if d:
            wd = d / "workflows"
            if wd.exists() and wd.is_dir():
                for f in wd.iterdir():
                    if f.is_dir():
                        yield f.name

    def load_workflow(self, name: str) -> Workflow:
        assert self.kessel_dir is not None
        wf = load_workflow_from_directory(self.kessel_dir / "workflows" / name)
        wf.shenv = self.senv
        return wf

    @property
    def workflow(self) -> str:
        return os.environ.get("KESSEL_WORKFLOW", "default")

    @workflow.setter
    def workflow(self, value: str | None) -> None:
        if value is None:
            self.senv.unset_env_var("KESSEL_WORKFLOW")
            self._workflow_config = None
            return

        if self.workflow != value:
            self.senv.echo(f"Activating {value} workflow")
            self.senv.set_env_var("KESSEL_WORKFLOW", value)
            self._workflow_config = None

    @property
    def workflow_config(self) -> Workflow | None:
        try:
            if self._workflow_config is None:
                self._workflow_config = self.load_workflow(self.workflow)
            return self._workflow_config
        except FileNotFoundError:
            return None

    @property
    def run_state(self) -> str | None:
        return os.environ.get("KESSEL_RUN_STATE", None)

    @run_state.setter
    def run_state(self, value: str | None) -> None:
        self.senv.set_env_var("KESSEL_RUN_STATE", value)

    @property
    def kessel_root(self) -> Path:
        return Path(os.environ["KESSEL_ROOT"])

    @property
    def kessel_config_dir(self) -> Path:
        return self.kessel_root / "etc" / "kessel"
