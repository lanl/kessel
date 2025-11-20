import glob
import os
import shutil
import sys
from pathlib import Path

from ruamel.yaml import YAML


def merge(envA, envB):
    a = envA["spack"]
    for k, b in envB["spack"].items():
        a1 = a.get(k)
        if isinstance(a1, list):
            a1 += b
        elif isinstance(a1, dict):
            a1 |= b
        else:
            a[k] = b
    return envA


def load_env(path, template_dirs=[]):
    with open(path) as f:
        yaml = YAML(typ="safe")
        new_env = yaml.load(f)

    base_names = new_env["spack"].get("extends", ())

    if isinstance(base_names, str):
        base_names = [base_names]

    new_env["spack"].pop("extends", None)

    env = {"spack": {}}
    for base_name in base_names:
        found = False
        for template_dir in template_dirs:
            template = template_dir / f"{base_name}.yaml"
            if template.exists():
                env = merge(env, load_env(template, template_dirs))
                found = True

        if not found:
            sys.exit(f"ERROR: unknown template '{base_name}'")
    return merge(env, new_env)


class Deployment(object):
    def __init__(self, deployment_dir=Path.cwd()):
        self.deployment_dir = Path(deployment_dir)

    @property
    def config_dir(self):
        return self.deployment_dir / "config"

    @property
    def env_dir(self):
        return self.deployment_dir / "environments"

    def init(self, ctx, source_config, preserve=False):
        # copy config folder from source_config
        if not preserve and self.config_dir.exists():
            shutil.rmtree(self.config_dir)
            shutil.rmtree(self.env_dir)
        if source_config.config_dir.exists():
            shutil.copytree(source_config.config_dir, self.config_dir, dirs_exist_ok=True)

        env_glob = (source_config.env_dir / "**" / "*.yaml").resolve()
        env_templates = glob.glob(str(env_glob), recursive=True)

        sys_links = {}

        for tpl in env_templates:
            path = Path(tpl)
            relpath = Path(path.relative_to(source_config.env_dir.resolve()))
            system = relpath.parts[0]
            source_system_dir = source_config.env_dir / system

            if source_system_dir.is_symlink():
                if system not in sys_links:
                    sys_links[system] = source_system_dir.readlink()
                continue

            target = self.env_dir / relpath.parent / relpath.stem / "spack.yaml"

            template_dirs = [
                source_config.template_dir(system),
                source_config.template_dir(),
                ctx.kessel_template_dir(system),
                ctx.kessel_template_dir(),
            ]

            os.makedirs(target.parent, exist_ok=True)
            print("Creating", target)
            env = load_env(path, template_dirs)
            with open(target, "w") as f:
                yaml = YAML(typ="safe")
                yaml.default_flow_style = False
                yaml.width = 256
                yaml.dump(env, f)

        for s, target in sys_links.items():
            target_system_dir = self.env_dir / s
            print(f"Creating {target_system_dir} -> {target}")
            if not target_system_dir.exists():
                target_system_dir.symlink_to(target, target_is_directory=True)
