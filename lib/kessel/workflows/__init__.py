import inspect
import os
import sys
import subprocess
from pathlib import Path
from kessel.colors import COLOR_BLUE, COLOR_PLAIN


class EnvState:
    def __init__(self, default=None, variable=None):
        self.default = default
        self.variable = variable
        self.type = type(default) if default else str


class Meta(type):
    def __new__(mcls, name, bases, namespace):
        states = {
            name: value
            for name, value in namespace.items()
            if isinstance(value, EnvState)
        }

        def make_accessors(name, state):
            if state.variable:
                variable = state.variable
            else:
                variable = f"KESSEL_{name.upper()}"

            def getter(self):
                if variable not in self.shenv:
                    self.shenv[variable] = state.default
                    if state.default is None:
                        return None
                return state.type(self.shenv[variable])

            def setter(self, value):
                self.shenv[variable] = str(value)

            return getter, setter

        for name, state in states.items():
            getter, setter = make_accessors(name, state)
            namespace[name] = property(getter, setter)
            namespace.setdefault("states", set()).add(name)
        return super().__new__(mcls, name, bases, namespace)


def environment(default=None, variable=None):
    return EnvState(default=default, variable=variable)


def collapsed(func):
    func.collapsed = True
    return func


def default_ci_message(project,
                       system="local",
                       workflow="default",
                       args=sys.argv[1:],
                       pre_alloc_init="",
                       post_alloc_init=""):
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
    def __init__(self):
        self.shenv = None
        self.workflow_dir = None

    @property
    def merged_states(self):
        merged = set()
        for base in self.__class__.__mro__:
            if hasattr(base, "states"):
                merged |= base.states
        return merged

    def init(self):
        # initialize states to default values if not already set
        for s in self.merged_states:
            getattr(self, s)

    def init_step(self, args):
        for name, value in vars(args).items():
            if hasattr(self, name) and value:
                setattr(self, name, value)

    @property
    def workflow(self):
        return self.__class__.__name__.lower()

    @property
    def kessel_root(self):
        return Path(os.environ["KESSEL_ROOT"])

    def is_step_collapsed(self, step):
        s = getattr(self, step)
        return hasattr(s, "collapsed") and s.collapsed

    def get_step_title(self, step):
        return inspect.getdoc(getattr(self, step)).splitlines()[0]

    def exec(self, *args):
        return self.shenv.eval(*args)


def git(cmd, cwd=None, check=True):
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
