from pathlib import Path
import os
import stat
import glob
import subprocess

from kessel.config import SourceConfig
from kessel.deployment import Deployment
from kessel.util import create_squashfs


def init(args, ctx, senv):
    source_config = SourceConfig(args.config_dir)
    deployment = Deployment()
    deployment.init(ctx, source_config)


def activate(args, ctx, senv):
    deployment_dir = Path(args.path).resolve()
    if deployment_dir.exists():
        ctx.deployment_dir = deployment_dir
    else:
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")


def finalize(args, ctx, senv):
    if ctx.deployment_dir:
        group = ctx.group
        dperms = ctx.directory_permissions  # also applies to executables
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

        ctx.create_replicate_squashfs(ctx.deployment_dir / ".replicate.sqfs")


def remove_packages(pkgs, senv):
    for pkg in pkgs:
        senv.eval(f"spack uninstall -y --all --dependents {pkg} || true")


def clean(args, ctx, senv):
    if ctx.deployment_dir:
        config = ctx.config
        remove_packages(config.build.exclude, senv)
        senv.eval("spack clean -a")


def create_bootstrap_mirror(ctx, senv):
    # create bootstrap mirror
    senv.eval("spack bootstrap status || true")
    senv.eval("spack bootstrap now")
    senv.eval("spack bootstrap status")
    senv.eval(
        f"spack bootstrap mirror --binary-packages {ctx.deployment_dir}/spack-bootstrap || true"
    )


def concretize_env_for_mirror(name, env_path, senv):
    senv.eval(f'echo "Concretizing {name}..."')
    senv.eval(f"rm -rf {env_path}/.spack-env")
    senv.eval(f"mkdir -p {env_path}/.spack-env")
    senv.eval(f"cp {env_path}/spack.yaml {env_path}/spack.yaml.original")
    senv.eval(f"spack env activate -d {env_path}")
    senv.eval("spack config add view:false")
    senv.eval(
        f"spack concretize -f --fresh 2>&1 > {env_path}/.spack-env/concretization.txt || touch {env_path}/.spack-env/failure &"
    )
    senv.eval("spack env deactivate")


def create_env_mirror(mirror_dir, mirror_exclude_file, name, env_path, senv):
    failure_file = env_path / ".spack-env" / "failure"
    if failure_file.exists():
        print(f"ERROR: Concretization of {name} failed!")
    else:
        senv.eval(f'echo "Creating mirror for {name}..."')
        senv.eval(f"spack env activate -d {env_path}")
        senv.eval("spack spec")
        senv.eval(
            f"spack mirror create -d {mirror_dir} --all --skip-unstable-version --exclude-file {mirror_exclude_file}"
        )
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
        create_env_mirror(
            mirror_dir,
            mirror_exclude_file,
            env_path.relative_to(env_dir),
            env_path,
            senv,
        )


def bootstrap_create(args, ctx, senv):
    if ctx.deployment_dir and ctx.system:
        create_bootstrap_mirror(ctx, senv)


def mirror_create(args, ctx, senv):
    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system
        if args.all:
            env_glob = (env_dir / "**" / "*.yaml").resolve()
            envs = sorted(glob.glob(str(env_glob), recursive=True))
        else:
            envs = [env_dir / args.env / "spack.yaml"]

        create_system_source_mirror(ctx, envs, senv)


def snapshot_create(args, ctx, senv):
    if ctx.deployment_dir:
        print("Creating snapshot of current deployment...")
        print(f"  src: {ctx.deployment_dir}")
        print(f"  dst: {args.snapshot_file}")
        create_squashfs(ctx.deployment_dir, args.snapshot_file)
    else:
        raise Exception("No active deployment")


def snapshot_restore(args, ctx, senv):
    subprocess.run(["unsquashfs", "-d", args.dest, args.snapshot_file])


def setup_command(subparser):
    subparsers = subparser.add_subparsers()
    init_cmd = subparsers.add_parser("init")
    init_cmd.add_argument("config_dir")
    init_cmd.set_defaults(func=init)

    bootstrap_cmd = subparsers.add_parser("bootstrap")
    bootstrap_subparsers = bootstrap_cmd.add_subparsers()
    bootstrap_create_cmd = bootstrap_subparsers.add_parser("create")
    bootstrap_create_cmd.set_defaults(func=bootstrap_create)

    mirror_cmd = subparsers.add_parser("mirror")
    mirror_subparsers = mirror_cmd.add_subparsers()
    mirror_create_cmd = mirror_subparsers.add_parser("create")
    mcgroup = mirror_create_cmd.add_mutually_exclusive_group()
    mcgroup.add_argument("-a", "--all", action="store_true")
    mcgroup.add_argument("env", nargs="?", default=None)
    mirror_create_cmd.set_defaults(func=mirror_create)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("path", nargs="?", default=Path.cwd())
    activate_cmd.set_defaults(func=activate)

    finalize_cmd = subparsers.add_parser("finalize")
    finalize_cmd.set_defaults(func=finalize)

    clean_cmd = subparsers.add_parser("clean")
    clean_cmd.set_defaults(func=clean)

    snapshot_cmd = subparsers.add_parser("snapshot")
    snapshot_subparsers = snapshot_cmd.add_subparsers()

    snapshot_create_cmd = snapshot_subparsers.add_parser("create")
    snapshot_create_cmd.add_argument("snapshot_file", help="destination", type=Path)
    snapshot_create_cmd.set_defaults(func=snapshot_create)
    snapshot_restore_cmd = snapshot_subparsers.add_parser("restore")
    snapshot_restore_cmd.add_argument(
        "-d", "--dest", help="destination", default=Path.cwd(), type=Path
    )
    snapshot_restore_cmd.add_argument("snapshot_file", help="snapshot file", type=Path)
    snapshot_restore_cmd.set_defaults(func=snapshot_restore)
