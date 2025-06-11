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

class Context(object):
    def __init__(self):
        pass

    @property
    def deployment_dir(self):
        deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)
        return Path(deployment_dir) if deployment_dir else None

    @property
    def system(self):
        return os.environ.get('KESSEL_SYSTEM', default=None)

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
    deployment_dir = Path(args.path).resolve()

    if deployment_dir.exists():
        senv.set_env_var("SPACK_USER_CACHE_PATH", f"{deployment_dir}/.spack")
        senv.set_env_var("SPACK_DISABLE_LOCAL_CONFIG", "true")
        senv.set_env_var("SPACK_SKIP_MODULES", "true")
        senv.set_env_var("KESSEL_DEPLOYMENT", deployment_dir)
        senv.source("${KESSEL_DEPLOYMENT}/spack/share/spack/setup-env.sh")

def system_list(args, senv):
    ctx = Context()

    if ctx.deployment_dir:
        environments_dir = ctx.deployment_dir / "environments"

        for d in [c.name for c in environments_dir.iterdir() if c.is_dir()]:
            print(d)

def system_activate(args, senv):
    ctx = Context()

    if ctx.deployment_dir:
        sys_dir = ctx.deployment_dir / "environments" / args.system
        if sys_dir.exists():
            print(f"Activating {args.system}")
            senv.set_env_var("KESSEL_SYSTEM", args.system)

def env_list(args, senv):
    ctx = Context()

    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system
        env_glob = (env_dir /  "**" / "*.yaml").resolve()
        envs = sorted(glob.glob(str(env_glob), recursive=True))

        for e in envs:
            print(Path(e).relative_to(env_dir).parent)

def env_activate(args, senv):
    ctx = Context()

    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system / args.env
        if env_dir.exists():
            print(f"Activating {ctx.system} environment {args.env}")
            senv.eval(f"spack env activate -d {env_dir}")

def create_bootstrap_mirror(ctx, senv):
    # create bootstrap mirror
    senv.eval("rm -f ${SPACK_ROOT}/etc/spack/linux/compilers.yaml")
    senv.eval(f"spack bootstrap mirror --binary-packages {ctx.deployment_dir}/spack_bootstrap || true")

def concretize_env_for_mirror(name, env_path, senv):
    senv.eval(f"echo \"Concretizing {name}...\"")
    senv.eval(f"rm -rf {env_path}/.spack-env")
    senv.eval(f"mkdir -p {env_path}/.spack-env")
    senv.eval("rm -f ${SPACK_ROOT}/etc/spack/linux/compilers.yaml")
    senv.eval(f"cp {env_path}/spack.yaml {env_path}/spack.yaml.original")
    senv.eval(f"spack env activate -d {env_path}")
    senv.eval(f"spack config add view:false")
    senv.eval(f"spack concretize -f --fresh 2>&1 > {env_path}/.spack-env/concretization.txt || touch {env_path}/.spack-env/failure &")
    senv.eval(f"spack env deactivate")

def create_env_mirror(mirror_dir, name, env_path, senv):
    failure_file = env_path / ".spack-env" / "failure"
    if failure_file.exists():
        print(f"ERROR: Concretization of {name} failed!")
    else:
        senv.eval(f"echo \"Creating mirror for {name}...\"")
        senv.eval(f"spack env activate -d {env_path}")
        senv.eval(f"cat {env_path}/.spack-env/concretization.txt")
        senv.eval(f"spack mirror create -d {mirror_dir} --all --skip-unstable-version")
        senv.eval(f"rm -f {env_path}/spack.lock")
        senv.eval(f"cp {env_path}/spack.yaml.original {env_path}/spack.yaml")

def create_system_source_mirror(ctx, senv):
    mirror_dir = ctx.deployment_dir / "spack_mirror"
    env_dir = ctx.deployment_dir / "environments" / ctx.system
    env_glob = (env_dir /  "**" / "*.yaml").resolve()
    envs = sorted(glob.glob(str(env_glob), recursive=True))

    for e in envs:
        env_path = Path(e).parent
        concretize_env_for_mirror(env_path.relative_to(env_dir), env_path, senv)

    senv.eval("wait")

    for e in envs:
        env_path = Path(e).parent
        create_env_mirror(mirror_dir, env_path.relative_to(env_dir), env_path, senv)

    senv.eval("rm -f ${SPACK_ROOT}/etc/spack/linux/compilers.yaml")


def bootstrap_create(args, senv):
    ctx = Context()

    if ctx.deployment_dir:
        create_bootstrap_mirror(ctx, senv)

def mirror_create(args, senv):
    ctx = Context()

    if ctx.deployment_dir and ctx.system:
        create_system_source_mirror(ctx, senv)

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

    bootstrap_cmd = subparsers.add_parser('bootstrap')
    bootstrap_subparsers = bootstrap_cmd.add_subparsers()
    bootstrap_create_cmd = bootstrap_subparsers.add_parser('create')
    bootstrap_create_cmd.set_defaults(func=bootstrap_create)

    mirror_cmd = subparsers.add_parser('mirror')
    mirror_subparsers = mirror_cmd.add_subparsers()
    mirror_create_cmd = mirror_subparsers.add_parser('create')
    mirror_create_cmd.set_defaults(func=mirror_create)

    args = parser.parse_args()
    args.func(args, senv)
    return 0
