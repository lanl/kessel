
def state(name, default=None):
    env_var = f"KESSEL_{name.upper()}"
    var_type = type(default)

    def getter(self):
        if env_var not in self.shenv:
            self.shenv[env_var] = default
        return var_type(self.shenv[env_var])

    def setter(self, value):
        self.shenv[env_var] = str(value)

    frame = __import__("inspect").currentframe().f_back
    cls_dict = frame.f_locals
    cls_dict[name] = property(getter, setter)


def collapsed(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
    wrapper.collapsed = True
    return wrapper


class Workflow(object):
    def __init__(self):
        self.shenv = None
        self.workflow_dir = None

    def is_step_collapsed(self, step):
        s = getattr(self, step)
        return hasattr(s, "collapsed") and s.collapsed

    def get_step_title(self, step):
        return getattr(self, step).__doc__
