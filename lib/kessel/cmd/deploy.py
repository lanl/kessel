import os
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context
from kessel.util import ShellEnvironment


def activate(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel deploy activate' is deprecated. "
          "Source deployment activate.sh directly instead.",
          file=sys.stderr)
    deployment_dir = Path(args.path).resolve()
    deployment_activate_script = deployment_dir / "activate.sh"
    if deployment_activate_script.exists():
        senv.source(deployment_activate_script)
    else:
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")


def replicate(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel deploy replicate' is deprecated. "
          "Run clone-deployment command from active deployment directly instead.",
          file=sys.stderr)
    if args.src is None:
        raise Exception("No active deployment!")

    deployment_dir = Path(args.src).resolve()
    if not deployment_dir.exists():
        raise Exception(f"Deployment at '{deployment_dir} does not exist!")

    clone_deployment_command = deployment_dir / "bin" / "clone-deployment"

    if clone_deployment_command.exists():
        renv = os.environ.copy()
        renv["KESSEL_DEPLOYMENT"] = str(deployment_dir)
        subprocess.call([str(clone_deployment_command), args.dest], env=renv)
    else:
        raise Exception("Deployment doesn't provide clone-deployment script!")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    subparsers = subparser.add_subparsers()

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("path", nargs="?", default=Path.cwd())
    activate_cmd.set_defaults(func=activate)

    deployment_dir = os.environ.get("KESSEL_DEPLOYMENT", default=None)
    deployment_path = Path(deployment_dir) if deployment_dir else None

    replicate_cmd = subparsers.add_parser("replicate")
    replicate_cmd.add_argument("src", nargs="?", default=deployment_path, help="source deployment folder")
    replicate_cmd.add_argument("dest", default=Path.cwd(), help="destination folder")
    replicate_cmd.set_defaults(func=replicate)
