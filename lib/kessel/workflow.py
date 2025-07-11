import os
import re
from pathlib import Path


class Workflow(object):
    def __init__(self, steps, init_script=None):
        self.steps = steps
        self.init_script = init_script


class WorkflowStep(object):
    def __init__(self, script):
        self.script = Path(script)
        self._name = None
        self._title = None
        self._collapsed = None

    def _load_config(self):
        self._name = self.script.stem[self.script.stem.index('_') + 1:]
        self._title = self._name
        self._collapsed = False
        with open(self.script, "r") as f:
            for line in f:
                if line.startswith("#KESSEL name:"):
                    self._name = line[line.index(':') + 1:].strip()
                    # TODO validate no spaces
                elif line.startswith("#KESSEL title:"):
                    self._title = line[line.index(':') + 1:].strip()
                elif line.startswith("#KESSEL collapsed:"):
                    self._collapsed = line[line.index(':') + 1:].strip().upper() not in ["FALSE", "NO", "OFF"]

    @property
    def name(self):
        if self._name is None:
            self._load_config()
        return self._name

    @property
    def title(self):
        if self._title is None:
            self._load_config()
        return self._title

    @property
    def collapsed(self):
        if self._collapsed is None:
            self._load_config()
        return self._collapsed


def load_workflow_from_directory(path: Path):
    init_pattern = re.compile(r'^[0]+_init$')
    step_pattern = re.compile(r'^[0-9]+_[a-z0-9_-]+$')

    steps = []
    init_script = None

    for f in sorted(path.iterdir()):
        if f.is_file() and os.access(f, os.X_OK) and step_pattern.fullmatch(f.name):
            if init_pattern.fullmatch(f.name):
                init_script = f
            else:
                steps.append(WorkflowStep(f))
    return Workflow(steps, init_script=init_script)
