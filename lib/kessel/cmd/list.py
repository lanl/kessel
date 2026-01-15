"""List available workflows."""

from kessel.colors import COLOR_GREEN, COLOR_PLAIN


def list_workflows(args, ctx, senv):
    """List all available workflows, highlighting the active one."""
    for wf in ctx.workflows:
        if wf == ctx.workflow:
            print(f"{COLOR_GREEN}{wf}{COLOR_PLAIN}")
        else:
            print(wf)


def setup_command(subparser, ctx):
    """Setup the list command."""
    subparser.set_defaults(func=list_workflows)
