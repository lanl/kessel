from pathlib import Path
import subprocess
from ruamel.yaml import YAML


class KesselConfig(object):
    def __init__(self, deployment_dir):
        self.deployment_dir = Path(deployment_dir)

    @property
    def parent(self):
        parent_file = self.deployment_dir / ".kessel" / "parent"
        if parent_file.exists():
            with open(parent_file, "r") as f:
                return f.read().strip()
        return None

class SourceConfig(object):
    def __init__(self, config_root):
        self.config_root = Path(config_root).resolve()
        self.config_file = self.config_root / ".kessel.yaml"

        with open(self.config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)["kessel"]

    @property
    def config_dir(self):
        return self.config_root / "config"

    def template_dir(self, system=None):
        if system:
            return self.config_dir / system / "templates"
        return self.config_dir / "templates"

    @property
    def env_dir(self):
        return self.config_root / "environments"
