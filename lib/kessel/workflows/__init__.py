import inspect


def state(name, default=None, var=None):
    if var:
        env_var = var
    else:
        env_var = f"KESSEL_{name.upper()}"

    if default:
        var_type = type(default)
    else:
        var_type = str

    def getter(self):
        if env_var not in self.shenv:
            self.shenv[env_var] = default
            if default is None:
                return None
        return var_type(self.shenv[env_var])

    def setter(self, value):
        self.shenv[env_var] = str(value)

    frame = __import__("inspect").currentframe().f_back
    cls_dict = frame.f_locals
    cls_dict[name] = property(getter, setter)
    if "states" not in cls_dict:
        cls_dict["states"] = [name]
    else:
        cls_dict["states"].append(name)


def collapsed(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
    wrapper.collapsed = True
    return wrapper


class Workflow(object):
    def __init__(self):
        self.shenv = None
        self.workflow_dir = None

    def init(self):
        # initialize states to default values if not already set
        for s in self.states:
            getattr(self, s)

    def is_step_collapsed(self, step):
        s = getattr(self, step)
        return hasattr(s, "collapsed") and s.collapsed

    def get_step_title(self, step):
        return inspect.getdoc(getattr(self, step)).splitlines()[0]
