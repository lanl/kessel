# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.

import argparse
import importlib.abc
import importlib.util
import inspect
import itertools
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from kessel.colors import COLOR_BLUE, COLOR_PLAIN
from kessel.util import ShellEnvironment


class ProjectWorkflowFinder(importlib.abc.MetaPathFinder):
    """Import hook to enable project workflows to import from each other."""

    def __init__(self):
        self.workflows_dir = None
        for d in itertools.chain([Path.cwd()], Path.cwd().parents):
            kessel_dir = d / ".kessel"
            if kessel_dir.exists() and kessel_dir.is_dir():
                self.workflows_dir = kessel_dir / "workflows"
                break

    def find_spec(self, fullname, path, target=None):
        """Find import spec for kessel.workflows.<name> if it's a project workflow."""
        if not self.workflows_dir or not self.workflows_dir.exists() or not fullname.startswith("kessel.workflows."):
            return None

        parts = fullname.split(".")
        if len(parts) != 3:  # Must be exactly kessel.workflows.<name>
            return None

        name = parts[2]

        if name == "base":
            return None

        search_paths = [
            self.workflows_dir / f"{name}.py",
            self.workflows_dir / name / "__init__.py",
            self.workflows_dir / name / "workflow.py",
        ]

        if name in {'spack', 'cmake', 'pip'}:
            # fall back for legacy workflows
            search_paths.append(Path(os.environ["KESSEL_ROOT"]) / "lib" / "kessel" / "workflows" / "base" / f"{name}.py")

        return next((importlib.util.spec_from_file_location(fullname, path)
                    for path in search_paths if path.exists()), None)


_workflow_finder = ProjectWorkflowFinder()
sys.meta_path.insert(0, _workflow_finder)


class EnvState:
    def __init__(self, default: Path | str | None = None, variable: Path | str | None = None) -> None:
        self.default = default
        self.variable = variable
        self.type: type[Path] | type[str] = type(default) if default else str


class Meta(type):
    def __new__(mcls, cname: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        states = {
            name: value
            for name, value in namespace.items()
            if isinstance(value, EnvState)
        }

        def make_accessors(name: str, state: EnvState) -> tuple[Callable, Callable]:
            if state.variable:
                variable = state.variable
            else:
                variable = f"KESSEL_{name.upper()}"

            def getter(self) -> Path | str | None:
                if variable not in self.environ:
                    self.environ[variable] = state.default
                    if state.default is None:
                        return None
                return state.type(self.environ[variable])

            def setter(self, value: str | list[str]) -> None:
                if isinstance(value, list):
                    self.environ[variable] = " ".join(value)
                else:
                    self.environ[variable] = str(value)

            return getter, setter

        for name, state in states.items():
            getter, setter = make_accessors(name, state)
            namespace[name] = property(getter, setter)
            namespace.setdefault("states", set()).add(name)
        return super().__new__(mcls, cname, bases, namespace)


def environment(default: Path | str | None = None, variable: str | None = None) -> EnvState:
    return EnvState(default=default, variable=variable)


def collapsed(func) -> Callable:
    func.collapsed = True
    return func


def default_ci_message(project: str,
                       system: str = "local",
                       workflow: str = "default",
                       args: list[str] = sys.argv[1:],
                       pre_alloc_init: str = "",
                       post_alloc_init: str = "") -> str:
    system_change = ""
    alloc = ""
    workflow_change = ""
    kessel_cmd = "kessel " + " ".join(args)

    if system != "local":
        system_change = f"ssh {system}\n"

    if pre_alloc_init:
        pre_alloc_init += "\n"

    if post_alloc_init:
        post_alloc_init += "\n"

    if "LLNL_FLUX_SCHEDULER_PARAMETERS" in os.environ:
        alloc = f"flux alloc {os.environ['LLNL_FLUX_SCHEDULER_PARAMETERS']}\n"
    elif "SCHEDULER_PARAMETERS" in os.environ:
        alloc = f"salloc {os.environ['SCHEDULER_PARAMETERS']}\n"

    if workflow != "default":
        workflow_change = f"kessel activate {workflow}\n"

    return (
        f"{COLOR_BLUE} \n"
        "######################################################################\n"
        " \n"
        "To recreate this CI run, follow these steps:\n"
        " \n"
        f"{system_change}"
        f"cd /your/{project}/checkout\n"
        f"{pre_alloc_init}"
        f"{alloc}"
        f"{post_alloc_init}"
        f"{workflow_change}"
        f"{kessel_cmd}\n"
        " \n"
        "######################################################################\n"
        f"{COLOR_PLAIN} \n"
    )


class Workflow(metaclass=Meta):
    def __init__(self) -> None:
        self.shenv: ShellEnvironment | None = None
        self._workflow: str | None = None
        self.steps: list[str]

    @property
    def merged_states(self) -> set:
        merged = set()
        for base in self.__class__.__mro__:
            if hasattr(base, "states"):
                merged |= base.states
        return merged

    def init(self) -> None:
        # initialize states to default values if not already set
        for s in self.merged_states:
            getattr(self, s)

    def init_step(self, args: argparse.Namespace) -> None:
        for name, value in vars(args).items():
            if hasattr(self, name) and value:
                setattr(self, name, value)

    @property
    def workflow(self) -> str:
        return self._workflow if self._workflow else self.resolved_workflow

    @workflow.setter
    def workflow(self, name):
        self._workflow = name

    @property
    def resolved_workflow(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def kessel_root(self) -> Path:
        return Path(os.environ["KESSEL_ROOT"])

    @property
    def workflow_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).parent

    def is_step_collapsed(self, step: str) -> bool:
        s = getattr(self, step)
        return hasattr(s, "collapsed") and s.collapsed

    def get_step_title(self, step: str) -> str:
        doc = inspect.getdoc(getattr(self, step))
        assert doc is not None
        return doc.splitlines()[0]

    def exec(self, *args: str) -> None:
        assert self.shenv is not None
        self.shenv.eval(*args)

    def print(self, *args: str) -> None:
        assert self.shenv is not None
        self.shenv.echo(*args)

    def source(self, path: str | Path, *args: str) -> None:
        assert self.shenv is not None
        self.shenv.source(path, *args)

    @property
    def environ(self) -> ShellEnvironment:
        assert self.shenv is not None
        return self.shenv


def load_workflow(name: str) -> Workflow:
    """Load workflow by name from workflows directory."""
    import importlib
    try:
        mod = importlib.import_module(f"kessel.workflows.{name}")
    except ModuleNotFoundError as e:
        # Convert to FileNotFoundError to maintain same exception interface
        raise FileNotFoundError(f"Could not find workflow '{name}'") from e

    cls_name = name.capitalize()
    wf = getattr(mod, cls_name)
    instance = wf()
    instance.workflow = name
    return instance


def git(cmd, cwd=None, check=True) -> None | str:
    """Run git command and return output, suppressing normal output."""
    env = os.environ.copy()
    env["GIT_ADVICE_DETACHED_HEAD"] = "false"
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"Git command failed: {e.stderr}")
        return None
