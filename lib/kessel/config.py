from pathlib import Path
import subprocess
from ruamel.yaml import YAML


class KesselConfig(object):
    def __init__(self, config_file):
        self.config_file = config_file

        with open(self.config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)["kessel"]

        self.parent = config.get("parent", None)


class GitConfig(object):
    def __init__(self, git_url, git_commit):
        self.git_url = git_url
        self.git_commit = git_commit

    def checkout(self, directory):
        if not Path(directory).exists():
            subprocess.call(
                [
                    "git",
                    "clone",
                    "-c",
                    "feature.manyFiles=true",
                    "--depth=1",
                    self.git_url,
                    directory,
                ]
            )
        else:
            subprocess.call(
                ["git", "-C", directory, "remote", "set-url", "origin", self.git_url]
            )

        spack_head = (
            subprocess.check_output(["git", "-C", directory, "rev-parse", "HEAD"])
            .decode()
            .strip()
        )
        if spack_head != self.git_commit:
            subprocess.call(
                [
                    "git",
                    "-C",
                    directory,
                    "fetch",
                    "--depth=1",
                    "origin",
                    self.git_commit,
                ]
            )
            subprocess.call(["git", "-C", directory, "checkout", "FETCH_HEAD"])
            subprocess.call(["git", "-C", directory, "branch", "-q", "-D", "@{-1}"])

    def to_dict(self):
        return {"git": self.git_url, "commit": self.git_commit}


class SourceConfig(object):
    def __init__(self, config_root):
        self.config_root = Path(config_root).resolve()
        self.config_file = self.config_root / ".kessel.yaml"

        with open(self.config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)["kessel"]

        self.spack = GitConfig(config["spack"]["git"], config["spack"]["commit"])
        self.spack_packages = GitConfig(
            config["spack-packages"]["git"], config["spack-packages"]["commit"]
        )

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
