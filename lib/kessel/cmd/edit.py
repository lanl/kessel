"""Edit the active workflow."""

from argparse import ArgumentParser, Namespace
from kessel.util import ShellEnvironment
from kessel.context import Context
from pathlib import Path


def edit_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Edit the current workflow."""
    workflow = ctx.workflow_config

    assert workflow is not None
    assert isinstance(workflow.workflow_dir, Path)
    senv.eval(f"${{EDITOR:-vim}} {workflow.workflow_dir / 'workflow.py'}")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the edit command."""
    subparser.set_defaults(func=edit_workflow)
