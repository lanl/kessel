# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.
"""Create a workflow."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context
from kessel.util import ShellEnvironment


def create_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Create a new workflow."""
    assert ctx.kessel_dir is not None
    workflows_dir = ctx.kessel_dir / "workflows"
    workflow_file = workflows_dir / f"{args.name}.py"

    if not workflow_file.exists():
        workflows_dir.mkdir(parents=True, exist_ok=True)
        print(f"Creating kessel workflow with name: '{args.name}'")
        with open(workflow_file, "w") as f:
            print(f"""from kessel.workflows import *

class {args.name.capitalize()}(Workflow):
    steps = []""", file=f)
        senv.eval(f"kessel edit {args.name}")
    else:
        raise Exception(f"Existing workflow '{args.name}' found.")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the create command."""
    subparser.add_argument("name")
    subparser.set_defaults(func=create_workflow)
