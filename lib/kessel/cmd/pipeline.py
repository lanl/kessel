from kessel.cmd.workflow import status
import argparse
import subprocess
import sys


def step(args, extra_args, ctx, senv):
    workflow = ctx.workflow_config
    step = next(s for s in workflow.steps if s.name == args.step)

    senv.section_start(
        step.name, step.title, collapsed=step.collapsed
    )
    senv.echo(status(ctx, step.name))
    ignored_args = len(sys.argv) - len(extra_args) - 1
    senv.eval(f"shift {ignored_args}")
    senv.eval(f"source {step.script} " + " ".join([f"\"{a}\"" for a in extra_args]))
    senv.eval("ret=$?")

    senv.section_end(step.name)
    senv.eval("test $ret -eq 0 && ", end="")
    ctx.pipeline_state = step.name

def setup_command(subparser, ctx):
    subparsers = subparser.add_subparsers()

    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config

        for s in workflow.steps:
            name = s.name
            pipeline_step_cmd = subparsers.add_parser(name)
            pipeline_step_cmd.set_defaults(func=step, step=name)
