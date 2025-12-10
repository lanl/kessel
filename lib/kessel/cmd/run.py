import sys

from kessel.cmd.step import step


def run(args, ctx, senv):
    ctx.run_state = None
    workflow = ctx.workflow_config

    if workflow is None:
        raise Exception(f"{ctx.workflow} workflow can not be found!")

    for s in workflow.steps:
        args.step = s
        step(args, ctx, senv)
        if args.until == s:
            break


def setup_command(subparser, ctx):
    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config
        subparser.add_argument("-u", "--until", choices=workflow.steps, default=workflow.steps[-1])
        for s in workflow.steps:
            args_func = f"{s}_args"
            if hasattr(workflow, args_func):
                getattr(workflow, args_func)(subparser)

    subparser.set_defaults(func=run)
