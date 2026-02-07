import argparse
import importlib.util
import inspect
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from kessel.colors import COLOR_BLUE, COLOR_PLAIN
from kessel.util import ShellEnvironment


def import_workflow_module(path: Path) -> ModuleType:
    mod_name = f"kessel.workflows.project.{path.name}"
    spec = importlib.util.spec_from_file_location(mod_name, path / "workflow.py")

    if spec is None:
        raise Exception("Could not load workflow")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod

    if spec.loader is None:
        raise Exception("Could create loader for workflow")

    spec.loader.exec_module(mod)
    return mod


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
        self.workflow_dir: Path | str | None = None
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
        return self.__class__.__name__.lower()

    @property
    def kessel_root(self) -> Path:
        return Path(os.environ["KESSEL_ROOT"])

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


def load_workflow_from_directory(path: Path) -> Workflow:
    cls_name = path.name.capitalize()
    mod = import_workflow_module(path)
    wf = getattr(mod, cls_name)
    instance = wf()
    instance.workflow_dir = path
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
