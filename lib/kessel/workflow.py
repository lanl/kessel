import importlib.util
import sys
from pathlib import Path


def load_workflow_from_directory(path: Path):
    cls_name = path.name.capitalize()
    mod_name = f"kessel.workflows.project.{path.name}"
    spec = importlib.util.spec_from_file_location(mod_name, path / "workflow.py")

    if spec is None:
        raise Exception("Could not load workflow")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod

    if spec.loader is None:
        raise Exception("Could create loader for workflow")

    spec.loader.exec_module(mod)
    wf = getattr(mod, cls_name)
    instance = wf()
    instance.workflow_dir = path
    return instance
