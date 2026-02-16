"""Create a workflow."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context
from kessel.util import ShellEnvironment


def create_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Create a new workflow."""
    assert ctx.kessel_dir is not None
    workflow_dir = ctx.kessel_dir / "workflows" / args.name

    if not workflow_dir.exists():
        workflow_dir.mkdir(parents=True)
        print(f"Creating kessel workflow with name: '{args.name}'")
        with open(workflow_dir / "workflow.py", "w") as f:
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
