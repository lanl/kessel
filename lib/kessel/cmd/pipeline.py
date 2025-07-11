from kessel.cmd.workflow import status
import subprocess
import sys


def step(args, ctx, senv):
    workflow = ctx.workflow_config
    step = next(s for s in workflow.steps if s.name == args.step)

    senv.section_start(
        step.name, step.title, collapsed=step.collapsed, passthrough=True
    )
    print(status(ctx, step.name))

    process = subprocess.Popen(f"{step.script}", pass_fds=[3], stdout=sys.stdout, stderr=sys.stderr)
    ctx.pipeline_state = step.name

    try:
        sys.exit(process.wait())
    except KeyboardInterrupt:
        pass


def setup_command(subparser, ctx):
    subparsers = subparser.add_subparsers()

    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config

        for s in workflow.steps:
            name = s.name
            pipeline_step_cmd = subparsers.add_parser(name)
            pipeline_step_cmd.set_defaults(func=step, step=name)
