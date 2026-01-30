from pathlib import Path
import os
import subprocess

from argparse import Namespace, ArgumentParser
from kessel.util import ShellEnvironment
from kessel.context import Context


def activate(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    deployment_dir = Path(args.path).resolve()
    deployment_activate_script = deployment_dir / "activate.sh"
    if deployment_activate_script.exists():
        senv.source(deployment_activate_script)
    else:
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")


def replicate(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    if args.src is None:
        raise Exception("No active deployment!")

    deployment_dir = Path(args.src).resolve()
    if not deployment_dir.exists():
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")

    if ctx.replicate_script.exists():
        renv = os.environ.copy()
        renv["KESSEL_DEPLOYMENT"] = str(deployment_dir)
        subprocess.call([ctx.replicate_script, args.dest], env=renv)
    else:
        raise Exception("Deployment doesn't provide replicate script!")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    subparsers = subparser.add_subparsers()

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("path", nargs="?", default=Path.cwd())
    activate_cmd.set_defaults(func=activate)

    replicate_cmd = subparsers.add_parser("replicate")
    replicate_cmd.add_argument("src", nargs="?", default=ctx.deployment_dir, help="source deployment folder")
    replicate_cmd.add_argument("dest", default=Path.cwd(), help="destination folder")
    replicate_cmd.set_defaults(func=replicate)
