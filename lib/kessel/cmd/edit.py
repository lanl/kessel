"""Edit the active workflow."""


def edit_workflow(args, ctx, senv):
    """Edit the current workflow."""
    workflow = ctx.workflow_config
    senv.eval(f"${{EDITOR:-vim}} {workflow.workflow_dir / 'workflow.py'}")


def setup_command(subparser, ctx):
    """Setup the edit command."""
    subparser.set_defaults(func=edit_workflow)
