import os
import json
import argparse
import subprocess
import shutil

from ruamel.yaml import YAML
from pathlib import Path

import glob
import sys
from pathlib import Path

def merge(envA, envB):
    a = envA['spack']
    for k, b in envB['spack'].items():
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

    base_names = new_env['spack'].get('extends', ())

    if isinstance(base_names, str):
        base_names = [base_names]

    new_env['spack'].pop('extends', None)

    env = {'spack': {}}
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


class SpackConfig(object):
    def __init__(self, directory, git_url, git_commit):
        self.directory = directory
        self.git_url = git_url
        self.git_commit = git_commit

    def init(self):
        if not Path(self.directory).exists():
            subprocess.call(["git", "clone", "-c", "feature.manyFiles=true", "-n", "--depth=1",  self.git_url, self.directory])

        spack_head = subprocess.check_output(["git", "-C", self.directory, "rev-parse", "HEAD"]).decode().strip()
        if spack_head != self.git_commit:
            subprocess.call(["git", "-C", self.directory, "fetch", "--depth=1", "origin", self.git_commit])
            subprocess.call(["git", "-C", self.directory, "checkout", "FETCH_HEAD"])
            subprocess.call(["git", "-C", self.directory, "branch", "-q", "-D", "@{-1}"])

    def to_dict(self):
        return {'git': self.git_url, 'commit': self.git_commit }



class KesselConfig(object):
    def __init__(self, config_file, deployment_dir=Path.cwd()):
        with open(config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)['kessel']

        config_dir = Path(config_file).resolve().parent

        if 'config_dir' in config:
            self.config_dir = Path(config['config_dir'])
            self.deployment_dir = config_dir
        else:
            self.config_dir = config_dir
            self.deployment_dir = Path(deployment_dir)

        self.config_file = self.config_dir / ".kessel.yaml"
        self.deployment_config_file = self.deployment_dir / ".kessel.yaml"

        spack_path = self.deployment_dir / "spack"
        self.spack = SpackConfig(spack_path, config["spack"]["git"], config["spack"]["commit"])

    def to_dict(self):
        return {
          'kessel' : {
            'version' : self.version,
            'spack'  : self.spack.to_dict(),
            'config_dir' : str(self.config_dir)
          }
        }

    @property
    def version(self):
        return "0.0.1"

    @property
    def env_dir(self):
        return self.config_dir / "environments"

    @property
    def kessel_root(self):
        return Path(os.environ["KESSEL_ROOT"])

    @property
    def kessel_config_dir(self):
        return self.kessel_root / "etc" / "kessel"

    def kessel_template_dir(self, system=None):
        if system:
            return self.kessel_config_dir / system / "templates"
        return self.kessel_config_dir / "templates"

    def deployment_template_dir(self, system=None):
        if system:
            return self.config_dir / "config" / system / "templates"
        return self.config_dir / "config" / "templates"

    def init(self):
        with open(self.deployment_config_file, 'w') as f:
            yaml = YAML(typ="safe")
            yaml.default_flow_style = False
            yaml.width = 256
            yaml.dump(self.to_dict(), f)

        self.spack.init()

        env_glob = (self.env_dir / "**" / "*.yaml").resolve()
        env_templates = glob.glob(str(env_glob), recursive=True)

        for tpl in env_templates:
            path = Path(tpl)
            relpath = Path(path.relative_to(self.env_dir.resolve()))
            system = relpath.parts[0]
            target = self.deployment_dir / "environments" /  relpath.parent / relpath.stem / "spack.yaml"
            source = path.parent / path.stem

            template_dirs = [
                self.deployment_template_dir(system),
                self.deployment_template_dir(),
                self.kessel_template_dir(system),
                self.kessel_template_dir()
            ]

            os.makedirs(target.parent, exist_ok=True)
            print("Creating",  target)
            env = load_env(path, template_dirs)
            with open(target, 'w') as f:
                yaml = YAML(typ="safe")
                yaml.default_flow_style = False
                yaml.width = 256
                yaml.dump(env, f)


class ShellEnvironment(object):
    def __init__(self):
        self.fd = open(3, 'w', closefd=False)

    def eval(self, cmd):
        print(cmd, file=self.fd, flush=True)

    def set_env_var(self, name, value):
        self.eval(f"export {name}={value}")

    def source(self, path):
        self.eval(f"source {path}")

def init(args, senv):
    config = KesselConfig(Path(args.config_dir) / ".kessel.yaml")
    config.init()

def activate(args, senv):
    deployment_dir = args.path

    if deployment_dir.exists():
        senv.set_env_var("SPACK_USER_CACHE_PATH", f"{deployment_dir}/.spack")
        senv.set_env_var("SPACK_DISABLE_LOCAL_CONFIG", "true")
        senv.set_env_var("SPACK_SKIP_MODULES", "true")
        senv.set_env_var("KESSEL_DEPLOYMENT", deployment_dir)
        senv.source("${KESSEL_DEPLOYMENT}/spack/share/spack/setup-env.sh")

def system_list(args, senv):
    deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)

    if deployment_dir:
        environments_dir = Path(deployment_dir) / "environments"

        for d in [c.name for c in environments_dir.iterdir() if c.is_dir()]:
            print(d)

def system_activate(args, senv):
    deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)

    if deployment_dir:
        sys_dir = Path(deployment_dir) / "environments" / args.system
        if sys_dir.exists():
            print(f"Activating {args.system}")
            senv.set_env_var("KESSEL_SYSTEM", args.system)

def env_list(args, senv):
    deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)
    system = os.environ.get('KESSEL_SYSTEM', default=None)

    if deployment_dir and system:
        env_dir = Path(deployment_dir) / "environments" / system
        env_glob = (env_dir /  "**" / "*.yaml").resolve()
        envs = sorted(glob.glob(str(env_glob), recursive=True))

        for e in envs:
            print(Path(e).relative_to(env_dir).parent)

def env_activate(args, senv):
    deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)
    system = os.environ.get('KESSEL_SYSTEM', default=None)

    if deployment_dir and system:
        env_dir = Path(deployment_dir) / "environments" / system / args.env
        if env_dir.exists():
            print(f"Activating {system} environment {args.env}")
            senv.eval(f"spack env activate -d {env_dir}")

def main():
    senv = ShellEnvironment()
    parser = argparse.ArgumentParser(prog='kessel')
    subparsers = parser.add_subparsers()
    init_cmd = subparsers.add_parser('init')
    init_cmd.add_argument('config_dir')
    init_cmd.set_defaults(func=init)
    activate_cmd = subparsers.add_parser('activate')
    activate_cmd.add_argument('path', nargs='?', default=Path.cwd())
    activate_cmd.set_defaults(func=activate)

    system_cmd = subparsers.add_parser('system')
    sys_subparsers = system_cmd.add_subparsers()
    sys_list_cmd = sys_subparsers.add_parser('list')
    sys_list_cmd.set_defaults(func=system_list)
    sys_activate_cmd = sys_subparsers.add_parser('activate')
    sys_activate_cmd.add_argument('system')
    sys_activate_cmd.set_defaults(func=system_activate)

    env_cmd = subparsers.add_parser('env')
    env_subparsers = env_cmd.add_subparsers()
    env_list_cmd = env_subparsers.add_parser('list')
    env_list_cmd.set_defaults(func=env_list)
    env_activate_cmd = env_subparsers.add_parser('activate')
    env_activate_cmd.add_argument('env')
    env_activate_cmd.set_defaults(func=env_activate)

    args = parser.parse_args()
    args.func(args, senv)
    return 0
