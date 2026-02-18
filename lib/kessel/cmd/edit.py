"""Edit the active workflow."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context
from kessel.util import ShellEnvironment


def edit_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Edit the current workflow."""
    if args.workflow:
        if args.workflow in set(ctx.workflows):
            assert ctx.kessel_dir is not None
            workflow_path = ctx.kessel_dir / "workflows" / args.workflow / "workflow.py"
        else:
            raise Exception(f"Unknown workflow '{args.workflow}'")
    else:
        workflow = ctx.workflow_config

        assert workflow is not None
        assert isinstance(workflow.workflow_dir, Path)
        workflow_path = workflow.workflow_dir / "workflow.py"
    senv.eval(f"${{EDITOR:-vim}} {workflow_path}")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the edit command."""
    subparser.add_argument("workflow", nargs="?")
    subparser.set_defaults(func=edit_workflow)
