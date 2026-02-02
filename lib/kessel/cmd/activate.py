"""Activate a workflow."""

from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment


def activate_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Activate the specified workflow."""
    ctx.reset()
    ctx.workflow = args.name


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the activate command."""
    subparser.add_argument("name", help="Name of the workflow to activate")
    subparser.set_defaults(func=activate_workflow)
