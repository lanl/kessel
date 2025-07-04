import os
import re
import sys

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

_VAR_PATTERN = re.compile(r"\$([A-Za-z_]\w*)")


def merge_yaml(A, B):
    a = A
    for k, b in B.items():
        a1 = a.get(k)
        if isinstance(a1, list):
            combined = b + a1
            a1.clear()
            a1.extend(combined)
        elif isinstance(a1, dict):
            for k2 in b:
                if k2 not in a1:
                    a1[k2] = b[k2]
        else:
            a[k] = b
    return A


def load_workflow_from_string(s, template_dirs=[]):
    yaml = YAML()
    return load_workflow(yaml.load(s), template_dirs=template_dirs)


def load_workflow_from_file(path, template_dirs=[]):
    with open(path) as f:
        yaml = YAML()
        return load_workflow(yaml.load(f), template_dirs=template_dirs)


def load_workflow(new_wf, template_dirs=[]):
    base_names = new_wf.get("extends", ())

    if isinstance(base_names, str):
        base_names = [base_names]

    new_wf.pop("extends", None)

    wf = CommentedMap()
    for base_name in base_names:
        found = False
        for template_dir in template_dirs:
            template = template_dir / f"{base_name}.yml"
            if template.exists():
                wf = merge_yaml(load_workflow_from_file(template, template_dirs), wf)
                found = True

        if not found:
            sys.exit(f"ERROR: unknown template '{base_name}'")
    return merge_yaml(new_wf, wf)


def replace_variables(text, scopes=[os.environ]):
    """
    Replace all occurrences of $var in `text` by looking up `var`
    in each of the given `scopes` (in order). Scopes can be dicts or
    objects; if an object has a `visible_variables` attribute (an iterable
    of names), only attributes in that iterable will be considered.
    """

    def _lookup(var):
        for scope in scopes:
            if hasattr(scope, "__getitem__"):
                if var in scope:
                    return scope[var]
                continue
            vis = getattr(scope, "visible_variables", None)
            if vis is not None:
                if var not in vis:
                    continue
            if hasattr(scope, var):
                return getattr(scope, var)
        return None

    def _sub(match):
        name = match.group(1)
        val = _lookup(name)
        if val is None:
            return match.group(0)
        return str(val)

    return _VAR_PATTERN.sub(_sub, text)
