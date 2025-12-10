import sys
from kessel.cmd.workflow import status


def step(args, ctx, senv):
    workflow = ctx.workflow_config
    step_func = getattr(workflow, args.step)
    title = workflow.get_step_title(args.step)
    collapsed = workflow.is_step_collapsed(args.step)

    senv.section_start(
        args.step, title, collapsed=collapsed
    )
    senv.echo(status(ctx, args.step))

    step_func(args)

    senv.section_end(args.step)
    ctx.run_state = args.step


def setup_command(subparser, ctx):
    subparsers = subparser.add_subparsers()

    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config

        for name in workflow.steps:
            step_cmd = subparsers.add_parser(name)
            args_func = f"{name}_args"
            if hasattr(workflow, args_func):
                getattr(workflow, args_func)(step_cmd)
            step_cmd.set_defaults(func=step, step=name)
