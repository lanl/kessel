from pathlib import Path
import subprocess

from kessel.config import SourceConfig
from kessel.deployment import Deployment


def init(args, extra, ctx, senv):
    source_config = SourceConfig(args.config_dir)
    deployment = Deployment()
    deployment.init(ctx, source_config)


def activate(args, extra, ctx, senv):
    deployment_dir = Path(args.path).resolve()
    if deployment_dir.exists():
        ctx.deployment_dir = deployment_dir
    else:
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")


def replicate(args, extra, ctx, senv):
    if ctx.replicate_script.exists():
        subprocess.call([ctx.replicate_script, args.dest])
    else:
        raise Exception(f"Deployment doesn't provide replicate script!")


def setup_command(subparser):
    subparsers = subparser.add_subparsers()
    init_cmd = subparsers.add_parser("init")
    init_cmd.add_argument("config_dir")
    init_cmd.set_defaults(func=init)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("path", nargs="?", default=Path.cwd())
    activate_cmd.set_defaults(func=activate)

    replicate_cmd = subparsers.add_parser("replicate")
    replicate_cmd.add_argument("dest", default=Path.cwd(), help="destination folder")
    replicate_cmd.set_defaults(func=replicate)
