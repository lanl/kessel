import inspect
import os
from pathlib import Path


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
            namespace.setdefault("states", []).append(name)
        return super().__new__(mcls, name, bases, namespace)


def environment(default=None, variable=None):
    return EnvState(default=default, variable=variable)


def collapsed(func):
    func.collapsed = True
    return func


class Workflow(metaclass=Meta):
    def __init__(self):
        self.shenv = None
        self.workflow_dir = None

    def init(self):
        # initialize states to default values if not already set
        for s in self.states:
            getattr(self, s)

    def init_step(self, args):
        for name, value in vars(args).items():
            if hasattr(self, name) and value:
                setattr(self, name, value)

    @property
    def kessel_root(self):
        return Path(os.environ["KESSEL_ROOT"])

    def is_step_collapsed(self, step):
        s = getattr(self, step)
        return hasattr(s, "collapsed") and s.collapsed

    def get_step_title(self, step):
        return inspect.getdoc(getattr(self, step)).splitlines()[0]
