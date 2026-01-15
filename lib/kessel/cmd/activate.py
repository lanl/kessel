"""Activate a workflow."""


def activate_workflow(args, ctx, senv):
    """Activate the specified workflow."""
    ctx.reset()
    ctx.workflow = args.name


def setup_command(subparser, ctx):
    """Setup the activate command."""
    subparser.add_argument("name", help="Name of the workflow to activate")
    subparser.set_defaults(func=activate_workflow)
