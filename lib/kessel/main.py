import os
import re
import grp
import json
import argparse
import stat
import subprocess
import shutil
import tempfile

from ruamel.yaml import YAML
from pathlib import Path

import glob
import sys
from pathlib import Path

KESSEL_VERSION="0.0.1"

PROGRESS_STEP_COMPLETE = "●"
PROGRESS_STEP_PENDING = "○"
PROGRESS_BAR_PENDING = "▭"
PROGRESS_BAR_COMPLETE = "▬"

COLOR_BLUE='\033[1;34m'
COLOR_MAGENTA='\033[1;35m'
COLOR_CYAN='\033[1;36m'
COLOR_PLAIN='\033[0m'

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


class GitConfig(object):
    def __init__(self, git_url, git_commit):
        self.git_url = git_url
        self.git_commit = git_commit

    def checkout(self, directory):
        if not Path(directory).exists():
            subprocess.call(["git", "clone", "-c", "feature.manyFiles=true", "--depth=1",  self.git_url, directory])
        else:
            subprocess.call(["git", "-C", directory, "remote", "set-url", "origin", self.git_url])

        spack_head = subprocess.check_output(["git", "-C", directory, "rev-parse", "HEAD"]).decode().strip()
        if spack_head != self.git_commit:
            subprocess.call(["git", "-C", directory, "fetch", "--depth=1", "origin", self.git_commit])
            subprocess.call(["git", "-C", directory, "checkout", "FETCH_HEAD"])
            subprocess.call(["git", "-C", directory, "branch", "-q", "-D", "@{-1}"])


    def to_dict(self):
        return {'git': self.git_url, 'commit': self.git_commit }

class BuildConfig(object):
    def __init__(self, options={}):
        self.exclude = options.get("exclude", [])

    def to_dict(self):
        return {'exclude': self.exclude }


class MirrorConfig(object):
    def __init__(self, options={}):
        self.exclude = options.get("exclude", [])

    def write_exclude_file(self, path):
        with open(path, "w") as f:
            for e in self.exclude:
                print(e, file=f)

    def to_dict(self):
        return {'exclude': self.exclude }

def symbolic_to_octal(perm_str, directory=False):
    perm_bits = {'r': 4, 'w': 2, 'x': 1}
    perms = {'u': 0, 'g': 0, 'o': 0}

    for clause in perm_str.split(','):
        who, rights = clause.split('=')
        bit = 0
        for char in rights:
            if char in perm_bits:
                bit |= perm_bits[char]
            elif char == 'X' and directory:
                bit |= perm_bits['x']
        perms[who] = bit

    return int(f"{perms['u']}{perms['g']}{perms['o']}", 8)

class Context(object):
    def __init__(self, senv):
        self.senv = senv

    @property
    def build_dir(self):
        return Path(os.environ.get("BUILD_DIR", Path.cwd() / "build"))

    @property
    def install_dir(self):
        return Path(os.environ.get("INSTALL_DIR", self.build_dir / "install"))

    @property
    def build_env(self):
        return self.build_dir / "build_env.sh"

    @property
    def source_dir(self):
        return Path(os.environ.get("SOURCE_DIR", Path.cwd()))

    @property
    def project_spec(self):
        return os.environ["KESSEL_ENV_PROJECT_SPEC"]

    @project_spec.setter
    def project_spec(self, value):
        # TODO validate
        self.senv.set_env_var("KESSEL_ENV_PROJECT_SPEC", value.strip())

    @property
    def project(self):
        # cases to cover
        # foo@1.2.0 +bar
        # foo@=1.2.0 ~bar
        # foo@git.sha=1.2.0 ~bar
        # foo+bar@1.2.0
        # foo+bar@1.2.0 ^dep@1.2.3
        # foo +bar @1.2.0
        # foo +bar @1.2.0 ^dep@1.2.3
        spec = self.project_spec
        root_match = re.search(r'\b[a-zA-Z0-9_-]+\b', spec)
        return root_match.group()

    @property
    def project_version(self):
        spec = self.project_spec
        cutoff_match = re.search(r'[\^%]', spec)
        if cutoff_match:
            spec = spec[:cutoff_match.start()]
        version_match = re.search(r'@[^+\s~^%]+', spec)
        return version_match.group() if version_match else ""

    @property
    def project(self):
        spec = self.project_spec.split(" ")
        root_spec = spec[0].split("@")
        return root_spec[0]

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

    @property
    def deployment_dir(self):
        deployment_dir = os.environ.get('KESSEL_DEPLOYMENT', default=None)
        return Path(deployment_dir) if deployment_dir else None

    @deployment_dir.setter
    def deployment_dir(self, value):
        d = Path(value).resolve()
        config = KesselConfig(d / ".kessel.yaml")
        self.senv.echo(f"Activating deployment at {d}")
        self.senv.set_env_var("SPACK_USER_CACHE_PATH", f"{d}/.spack")
        self.senv.unset_env_var("SPACK_DISABLE_LOCAL_CONFIG")
        self.senv.set_env_var("SPACK_USER_CONFIG_PATH", "${KESSEL_CONFIG_DIR}")
        self.senv.set_env_var("SPACK_SKIP_MODULES", "true")
        self.senv.set_env_var("KESSEL_DEPLOYMENT", d)
        self.senv.set_env_var("KESSEL_PARENT_DEPLOYMENT", config.parent if config.parent else d)
        self.senv.source("${KESSEL_DEPLOYMENT}/spack/share/spack/setup-env.sh")

    @property
    def system(self):
        return os.environ.get('KESSEL_SYSTEM', default="local")

    @system.setter
    def system(self, value):
        if self.deployment_dir:
            sys_dir = self.deployment_dir / "environments" / value
            if not sys_dir.exists():
                raise Exception(f"Unknown system '{value}'!")
        elif value != "local":
            raise Exception("No active deployment!")
        self.senv.echo(f"Activating {value} system")
        self.senv.set_env_var("KESSEL_SYSTEM", value)
        self.senv.set_env_var("SPACK_SYSTEM_CONFIG_PATH", "${KESSEL_CONFIG_DIR}/${KESSEL_SYSTEM}")

    @property
    def environment(self):
        spack_env = os.environ.get('SPACK_ENV', default=None)
        if spack_env:
            env_dir = Path(spack_env).resolve().parent
            sys_dir = self.deployment_dir / "environments" / self.system
            return env_dir.relative_to(sys_dir)
        return None

    @environment.setter
    def environment(self, value):
        if self.deployment_dir:
            if self.system:
                env_dir = self.deployment_dir / "environments" / self.system / value
                if env_dir.exists():
                    self.senv.echo(f"Activating {self.system} environment {value}")
                    self.senv.eval(f"spack env activate -d {env_dir}")
                else:
                    raise Exception(f"Unknown environment '{value}' for system '{self.system}'!")
            else:
                raise Exception("No active system!")
        elif self.system and self.system == "local":
            self.senv.echo(f"Activating {self.system} environment {value}")
            self.senv.eval(f"spack env activate {value}")
        else:
            raise Exception("No active deployment!")


    @property
    def config(self):
        return KesselConfig(self.deployment_dir / ".kessel.yaml")

    @property
    def file_permissions(self):
        return symbolic_to_octal(os.environ.get('KESSEL_PERMISSIONS', default="u=rwX,g=rX,o="), directory=False)

    @property
    def directory_permissions(self):
        return symbolic_to_octal(os.environ.get('KESSEL_PERMISSIONS', default="u=rwX,g=rX,o="), directory=True)

    @property
    def group(self):
        grp_name = os.environ.get('KESSEL_GROUP', default=f"{os.environ['USER']}")
        return grp.getgrnam(grp_name).gr_gid

    @property
    def replicate_sqfs(self):
        return self.deployment_dir / ".replicate.sqfs"

    def replicate(self, dest):
        print("Creating deployment copy...")
        print(f"  src: {self.deployment_dir}")
        print(f"  dst: {dest}")
        cmd = [
          "rsync", "-a", "--no-p", "--no-g", "--chmod=ugo=rwX",
          "--exclude='.env'", "--exclude='spack-mirror'", "--exclude='spack-bootstrap'",
          "--exclude='/spack'", "--exclude='*spack.lock'", "--exclude='*.spack-env*'",
          f"{self.deployment_dir}/", dest]
        print(" ".join(cmd))
        subprocess.run(" ".join(cmd), shell=True)
        cmd2 = [
          "rsync", "-a", "--no-p", "--no-g", "--chmod=ugo=rwX",
          "--include={\"*__pycache__*\",\"*.pyc\"}",
          "--include=\"etc/spack/**\"",
          "--include=\"lib/spack/**\"",
          f"--exclude-from={self.deployment_dir}/spack/.gitignore",
          f"{self.deployment_dir}/spack/", f"{dest}/spack"]
        print(" ".join(cmd2))
        subprocess.run(" ".join(cmd2), shell=True)

        replica_config = {
          'kessel' : {
            'version' : KESSEL_VERSION,
            'build' : self.config.build.to_dict(),
            'mirror' : self.config.mirror.to_dict(),
            'parent' : str(self.deployment_dir),
          }
        }

        replica_config_file = Path(dest) / ".kessel.yaml"

        with open(replica_config_file, 'w') as f:
            yaml = YAML(typ="safe")
            yaml.default_flow_style = False
            yaml.width = 256
            yaml.dump(replica_config, f)

    def create_squashfs(self, dest):
        with tempfile.TemporaryDirectory() as d:
            if Path(dest).exists():
                os.remove(dest)
            self.replicate(d)
            print(f"Creating squashfs file {dest}...")
            subprocess.run(["mksquashfs", d, dest, "-comp", "gzip"])

        try:
          os.chown(dest, -1, self.group)
          os.chmod(dest, self.file_permissions)
        except:
          pass

    def create_ci_deployment(self):
        ci_deployment_dir = f"{os.environ['TMPDIR']}/{os.environ['USER']}-ci-env"
        subprocess.run(["unsquashfs", "-d", ci_deployment_dir, self.replicate_sqfs])
        return ci_deployment_dir

class KesselConfig(object):
    def __init__(self, config_file):
        self.config_file = config_file

        with open(self.config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)['kessel']

        self.mirror = MirrorConfig(config.get("mirror", {}))
        self.build = BuildConfig(config.get("build", {}))
        self.parent = config.get("parent", None)

class KesselSourceConfig(object):
    def __init__(self, config_root):
        self.config_root = Path(config_root).resolve()
        self.config_file = self.config_root / ".kessel.yaml"

        with open(self.config_file, "r") as f:
            yaml = YAML(typ="safe")
            config = yaml.load(f)['kessel']

        self.mirror = MirrorConfig(config.get("mirror", {}))
        self.build = BuildConfig(config.get("build", {}))

        self.spack = GitConfig(config["spack"]["git"], config["spack"]["commit"])
        self.spack_packages = GitConfig(config["spack-packages"]["git"], config["spack-packages"]["commit"])

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


class KesselDeployment(object):
    def __init__(self, deployment_dir=Path.cwd()):
        self.deployment_dir = Path(deployment_dir)

    @property
    def config_file(self):
        return self.deployment_dir / ".kessel.yaml"

    @property
    def config_dir(self):
        return self.deployment_dir / "config"

    @property
    def env_dir(self):
        return self.deployment_dir / "environments"

    @property
    def mirror_exclude_file(self):
        return self.config_dir / "mirror.exclude"

    @property
    def spack_path(self):
        return self.deployment_dir / "spack"

    @property
    def spack_packages_path(self):
        return self.deployment_dir / "spack-packages"

    def init(self, ctx, source_config):
        deployment_config = {
          'kessel' : {
            'version' : KESSEL_VERSION,
            'build' : source_config.build.to_dict(),
            'mirror' : source_config.mirror.to_dict(),
          }
        }

        with open(self.config_file, 'w') as f:
            yaml = YAML(typ="safe")
            yaml.default_flow_style = False
            yaml.width = 256
            yaml.dump(deployment_config, f)

        # copy config folder from source_config
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
        shutil.copytree(source_config.config_dir, self.config_dir)

        # create spack and spack-packages checkouts
        source_config.spack.checkout(self.spack_path)
        source_config.spack_packages.checkout(self.spack_packages_path)

        source_config.mirror.write_exclude_file(self.mirror_exclude_file)

        env_glob = (source_config.env_dir / "**" / "*.yaml").resolve()
        env_templates = glob.glob(str(env_glob), recursive=True)

        for tpl in env_templates:
            path = Path(tpl)
            relpath = Path(path.relative_to(source_config.env_dir.resolve()))
            system = relpath.parts[0]
            target = self.env_dir /  relpath.parent / relpath.stem / "spack.yaml"
            source = path.parent / path.stem

            template_dirs = [
                source_config.template_dir(system),
                source_config.template_dir(),
                ctx.kessel_template_dir(system),
                ctx.kessel_template_dir()
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
        self.cmd_count = 0

    def eval(self, cmd):
        if self.cmd_count > 0:
            print(" && " + cmd, file=self.fd, flush=True, end="")
        else:
            print(cmd, file=self.fd, flush=True, end="")
        self.cmd_count += 1

    def set_env_var(self, name, value):
        self.eval(f"export {name}={value}")
        os.environ[name] = str(value)

    def unset_env_var(self, name):
        self.eval(f"unset {name}")
        if name in os.environ:
            del os.environ[name]

    def source(self, path):
        self.eval(f"source {path}")

    def echo(self, str=""):
        for line in str.splitlines():
            self.eval(f"echo '{line}'")

    def _section(self, marker, section, passthrough=False, msg=""):
        if "CI" in os.environ:
            if passthrough:
                print(f"\033[0Ksection_{marker}:$(date +%s):{section}\r\033[0K{COLOR_CYAN}{msg}{COLOR_PLAIN}", flush=True)
            else:
                self.eval(f"echo -e \"\033[0Ksection_{marker}:$(date +%s):{section}\r\033[0K{COLOR_CYAN}{msg}{COLOR_PLAIN}\"")
        else:
            if passthrough:
                print(f"{COLOR_CYAN}{msg}{COLOR_PLAIN}", flush=True)
            else:
                self.eval(f"echo -e \"{COLOR_CYAN}{msg}{COLOR_PLAIN}\"")

    def section_start(self, section, msg, collapsed=False, passthrough=False):
        self.set_env_var("KESSEL_RUN_STATE", section)

        if "CI" in os.environ:
            if collapsed:
                section += "[collapsed=true]"

        self._section("start", section, passthrough, msg)

    def section_end(self, section, passthrough=False):
        self._section("end", section, passthrough)

def init(args, senv):
    ctx = Context(senv)
    source_config = KesselSourceConfig(args.config_dir)
    deployment = KesselDeployment()
    deployment.init(ctx, source_config)

def activate(args, senv):
    ctx = Context(senv)
    deployment_dir = Path(args.path).resolve()
    if deployment_dir.exists():
        ctx.deployment_dir = deployment_dir
    else:
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")

def system_list(args, senv):
    ctx = Context(senv)

    print("local")

    if ctx.deployment_dir:
        environments_dir = ctx.deployment_dir / "environments"

        for d in [c.name for c in environments_dir.iterdir() if c.is_dir()]:
            print(d)

def system_activate(args, senv):
    ctx = Context(senv)
    ctx.system = args.system

def env_list(args, senv):
    ctx = Context(senv)

    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system
        env_glob = (env_dir /  "**" / "*.yaml").resolve()
        envs = sorted(glob.glob(str(env_glob), recursive=True))

        for e in envs:
            print(Path(e).relative_to(env_dir).parent)

def env_activate(args, senv):
    ctx = Context(senv)
    ctx.environment = args.env

def create_bootstrap_mirror(ctx, senv):
    # create bootstrap mirror
    senv.eval(f"spack bootstrap status || true")
    senv.eval(f"spack bootstrap now")
    senv.eval(f"spack bootstrap status")
    senv.eval(f"spack bootstrap mirror --binary-packages {ctx.deployment_dir}/spack-bootstrap || true")

def concretize_env_for_mirror(name, env_path, senv):
    senv.eval(f"echo \"Concretizing {name}...\"")
    senv.eval(f"rm -rf {env_path}/.spack-env")
    senv.eval(f"mkdir -p {env_path}/.spack-env")
    senv.eval(f"cp {env_path}/spack.yaml {env_path}/spack.yaml.original")
    senv.eval(f"spack env activate -d {env_path}")
    senv.eval(f"spack config add view:false")
    senv.eval(f"spack concretize -f --fresh 2>&1 > {env_path}/.spack-env/concretization.txt || touch {env_path}/.spack-env/failure &")
    senv.eval(f"spack env deactivate")

def create_env_mirror(mirror_dir, mirror_exclude_file, name, env_path, senv):
    failure_file = env_path / ".spack-env" / "failure"
    if failure_file.exists():
        print(f"ERROR: Concretization of {name} failed!")
    else:
        senv.eval(f"echo \"Creating mirror for {name}...\"")
        senv.eval(f"spack env activate -d {env_path}")
        senv.eval(f"spack spec")
        senv.eval(f"spack mirror create -d {mirror_dir} --all --skip-unstable-version --exclude-file {mirror_exclude_file}")
        senv.eval(f"rm -f {env_path}/spack.lock")
        senv.eval(f"cp {env_path}/spack.yaml.original {env_path}/spack.yaml")

def create_system_source_mirror(ctx, envs, senv):
    mirror_dir = ctx.deployment_dir / "spack-mirror"
    env_dir = ctx.deployment_dir / "environments" / ctx.system
    mirror_exclude_file = ctx.deployment_dir / "config" / "mirror.exclude"

    for e in envs:
        env_path = Path(e).parent
        concretize_env_for_mirror(env_path.relative_to(env_dir), env_path, senv)

    senv.eval("wait")

    for e in envs:
        env_path = Path(e).parent
        create_env_mirror(mirror_dir, mirror_exclude_file, env_path.relative_to(env_dir), env_path, senv)

def bootstrap_create(args, senv):
    ctx = Context(senv)

    if ctx.deployment_dir and ctx.system:
        create_bootstrap_mirror(ctx, senv)

def mirror_create(args, senv):
    ctx = Context(senv)

    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system
        if args.all:
            env_glob = (env_dir /  "**" / "*.yaml").resolve()
            envs = sorted(glob.glob(str(env_glob), recursive=True))
        else:
            envs = [env_dir / args.env / "spack.yaml"]

        create_system_source_mirror(ctx, envs, senv)

def remove_packages(pkgs, senv):
    for pkg in pkgs:
        senv.eval(f"spack uninstall -y --all --dependents {pkg} || true")

def clean(args, senv):
    ctx = Context(senv)
    if ctx.deployment_dir:
        config = ctx.config
        remove_packages(config.build.exclude, senv)
        senv.eval("spack clean -a")

def finalize(args, senv):
    ctx = Context(senv)

    if ctx.deployment_dir:
        group = ctx.group
        dperms = ctx.directory_permissions # also applies to executables
        fperms = ctx.file_permissions

        print("Setting permissions and group...")
        for dirpath, dirnames, filenames in os.walk(ctx.deployment_dir):
            for d in [os.path.join(dirpath, x) for x in dirnames]:
                os.chown(d, -1, group)
                os.chmod(d, dperms)

            for f in [os.path.join(dirpath, x) for x in filenames]:
                os.chown(f, -1, group, follow_symlinks=False)
                if os.access(f, os.X_OK):
                    os.chmod(f, dperms)
                else:
                    os.chmod(f, fperms)

        spack_db_dir = ctx.deployment_dir / "spack" / "opt" / "spack" / ".spack-db"
        if spack_db_dir.exists():
            mode = os.stat(spack_db_dir).st_mode
            mode |= stat.S_ISGID
            os.chmod(spack_db_dir, mode)

        ctx.create_squashfs(ctx.deployment_dir / ".replicate.sqfs")

def status(step=None):
    steps = [
        "setup",
        "env",
        "configure",
        "build",
        "test",
        "install",
        "submit",
    ]
    step_size = [0, 9, 11, 9, 7, 6, 7]

    s = " \n"
    s += " "*6
    completed = steps.index(step) if step in steps else -1
    for i, _ in enumerate(steps):
        if i <= completed:
            s += PROGRESS_BAR_COMPLETE * step_size[i]
            s += PROGRESS_STEP_COMPLETE
        else:
            s += PROGRESS_BAR_PENDING * step_size[i]
            s += PROGRESS_STEP_PENDING
    s += "\n\n"

    s += "    Setup    Prepare    Configure   Build   Test  Install  Submit\n"
    s += "           Environment\n \n"
    return s

def pipeline_setup(args, senv):
    ctx = Context(senv)
    senv.section_start("setup", "Setup", collapsed=True, passthrough=True)
    print(status("setup"), flush=True)
    os.umask(0o007)
    senv.eval("umask 0007")

    if args.system == "local":
        if "SPACK_ROOT" in os.environ:
            print(f"Using Spack install at {os.environ['SPACK_ROOT']}")
        else:
            raise Exception("No Spack installation active!")
    else:
        ctx.deployment_dir = ctx.create_ci_deployment()

    ctx.system = args.system
    senv.section_end("setup", passthrough=True)

def pipeline_env(args, senv):
    ctx = Context(senv)
    senv.section_start("env", "Create environment", collapsed=True)
    senv.echo(status("env"))

    # TODO local system, which will create a new Spack env and activate it
    # TODO custom-spec, which uses custom/spack.yaml
    ctx.environment = args.env
    ctx.project_spec = args.spec

    if os.path.exists(f"spack_repo/{ctx.project}"):
        senv.eval(f"(spack repo remove {ctx.project} 2> /dev/null > /dev/null || true)")
        senv.eval(f"spack repo add {ctx.source_dir}/spack_repo/{ctx.project}")

    if ctx.project_version:
        senv.set_env_var("PROJECT_PREFERRED_VERSION", ctx.project_version)
    else:
        # the preferred version is dependent on the active spack package in this spack environment and needs to be determined at runtime
        # we could avoid this if spack develop would chose the preferred version if nothing is specified
        senv.eval(f"export PROJECT_PREFERRED_VERSION=$(spack-python -c \"spec = spack.spec.Spec('{ctx.project}');pkg_cls = spack.repo.PATH.get_pkg_class(spec.fullname);print(spack.package_base.preferred_version(pkg_cls(spec)))\")")
    senv.eval(f"spack develop -b {ctx.build_dir} -p {ctx.source_dir} --no-clone {ctx.project}@${{PROJECT_PREFERRED_VERSION}}")
    senv.unset_env_var("PROJECT_PREFERRED_VERSION")

    # TODO custom-spec support

    # ignore first concretization output due to Spack bug https://github.com/spack/spack/issues/49326
    senv.eval("(spack concretize -f 2> /dev/null > /dev/null || true)")
    senv.eval("spack concretize -f")
    senv.eval("spack install --include-build-deps --only dependencies")
    senv.section_end("env")
    senv.eval("test -d \"$SPACK_ENV\"")

def pipeline_configure(args, senv):
    ctx = Context(senv)
    senv.section_start("configure", "Initial Spack CMake Configure", collapsed=True)
    senv.echo(status("configure"))
    senv.eval(f"spack install --test root --include-build-deps -u cmake -v {ctx.project}")

    senv.eval(f"spack build-env --dump {ctx.build_env} {ctx.project}")
    senv.eval(f"mv {ctx.build_env} {ctx.build_env}.tmp")
    senv.eval(f"grep -v '^SLURM' {ctx.build_env}.tmp > {ctx.build_env}")
    senv.eval(f"rm {ctx.build_env}.tmp")

    # silently change Spack defaults
    senv.eval(f"(source {ctx.build_env}; cmake -DCMAKE_VERBOSE_MAKEFILE=off -DCMAKE_INSTALL_PREFIX={ctx.install_dir} {ctx.build_dir} 2> /dev/null > /dev/null )")

    senv.section_end("configure")

def pipeline_build(args, senv):
    ctx = Context(senv)
    senv.section_start("build", "CMake build")
    senv.echo(status("build"))
    senv.eval(f"(source {ctx.build_env}; cmake {ctx.build_dir}; cmake --build {ctx.build_dir} --parallel)")
    senv.section_end("build")

def pipeline_test(args, senv):
    ctx = Context(senv)
    senv.section_start("test", "Tests")
    senv.echo(status("test"))
    senv.eval(f"(source {ctx.build_env}; export CTEST_OUTPUT_ON_FAILURE=1; ctest --test-dir {ctx.build_dir} --output-junit tests.xml )")
    senv.section_end("test")

def pipeline_install(args, senv):
    ctx = Context(senv)
    senv.section_start("install", "Install")
    senv.echo(status("install"))
    senv.eval(f"(source {ctx.build_env}; cmake --build {ctx.build_dir} --target install )")
    senv.section_end("install")

def pipeline_submit(args, senv):
    ctx = Context(senv)
    senv.section_start("submit", "Submit results to CDash")
    senv.echo(status("submit"))
    senv.section_end("submit")

def run(args, senv):
    ctx = Context(senv)
    senv.unset_env_var("KESSEL_RUN_STATE")

    if "CI" in os.environ:
        print(f"{COLOR_BLUE} ")
        print("######################################################################")
        print(" ")
        print("To recreate this CI run, follow these steps:")
        print(" ")
        print(f"ssh {args.system}")
        print(f"cd /your/{ctx.project}/checkout")
        if "LLNL_FLUX_SCHEDULER_PARAMETERS" in os.environ:
            print("flux alloc", os.environ["LLNL_FLUX_SCHEDULER_PARAMETERS"])
        elif "SCHEDULER_PARAMETERS" in os.environ:
            print("salloc", os.environ["SCHEDULER_PARAMETERS"])
        print(f"kessel run -s {args.system} -e {args.env} {args.project_spec}")
        print(" ")
        print("######################################################################")
        print(f"{COLOR_PLAIN} ", flush=True)

    senv.eval(f"kessel pipeline setup -s {args.system}")
    senv.eval(f"kessel pipeline env -e {args.env} {args.spec}")
    senv.eval(f"kessel pipeline configure")
    senv.eval(f"kessel pipeline build")
    senv.eval(f"kessel pipeline test")
    senv.eval(f"kessel pipeline install")
    senv.eval(f"kessel pipeline submit")

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
    mcgroup = mirror_create_cmd.add_mutually_exclusive_group()
    mcgroup.add_argument("-a", "--all", action="store_true")
    mcgroup.add_argument("env", nargs='?', default=None)
    mirror_create_cmd.set_defaults(func=mirror_create)

    clean_cmd = subparsers.add_parser('clean')
    clean_cmd.set_defaults(func=clean)

    finalize_cmd = subparsers.add_parser('finalize')
    finalize_cmd.set_defaults(func=finalize)

    pipeline_cmd = subparsers.add_parser('pipeline')
    pipeline_subparsers = pipeline_cmd.add_subparsers()

    pipeline_setup_cmd = pipeline_subparsers.add_parser('setup')
    pipeline_setup_cmd.add_argument('-s', '--system', default="local")
    pipeline_setup_cmd.set_defaults(func=pipeline_setup)

    pipeline_env_cmd = pipeline_subparsers.add_parser('env')
    pipeline_env_cmd.add_argument('-e', '--env', required=True)
    pipeline_env_cmd.add_argument('spec', help="project spec to build")
    pipeline_env_cmd.set_defaults(func=pipeline_env)

    pipeline_configure_cmd = pipeline_subparsers.add_parser('configure')
    pipeline_configure_cmd.set_defaults(func=pipeline_configure)

    pipeline_build_cmd = pipeline_subparsers.add_parser('build')
    pipeline_build_cmd.set_defaults(func=pipeline_build)

    pipeline_test_cmd = pipeline_subparsers.add_parser('test')
    pipeline_test_cmd.set_defaults(func=pipeline_test)

    pipeline_install_cmd = pipeline_subparsers.add_parser('install')
    pipeline_install_cmd.set_defaults(func=pipeline_install)

    pipeline_submit_cmd = pipeline_subparsers.add_parser('submit')
    pipeline_submit_cmd.set_defaults(func=pipeline_submit)

    run_cmd = subparsers.add_parser('run')
    run_cmd.add_argument('-s', '--system', default="local")
    run_cmd.add_argument('-e', '--env', required=True)
    run_cmd.add_argument('spec', help="project spec to build")
    run_cmd.set_defaults(func=run)

    args = parser.parse_args()
    args.func(args, senv)
    return 0
