from pathlib import Path
import os
import stat
import glob
import subprocess


def init(args, ctx, senv):
    kessel_dir = args.directory / ".kessel"
    workflow_dir = kessel_dir / "workflows"

    ctx.workflow = None

    if not kessel_dir.exists():
        workflow_dir.mkdir(parents=True)

        with open(workflow_dir / "default.yml", "w") as f:
            print("""\
variables:
  spec: myproject
extends: cmake_build""", file=f)


def setup_command(subparser):
    subparser.add_argument("directory", nargs="?", default=Path.cwd(), type=Path)
    subparser.set_defaults(func=init)
