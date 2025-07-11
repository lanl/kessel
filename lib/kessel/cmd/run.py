import os
import sys
import subprocess

from kessel.cmd.workflow import COLOR_BLUE, COLOR_PLAIN


def run(args, ctx, senv):
    ctx.pipeline_state = None
    workflow = ctx.workflow_config

    if workflow.init_script:
        process = subprocess.Popen([f"{workflow.init_script}"] + sys.argv[1:], pass_fds=[3])
        try:
            ret = process.wait()
            if ret != 0:
                sys.exit(1)
        except KeyboardInterrupt:
            pass

    for step in workflow.steps:
        senv.eval(f"kessel pipeline {step.name}")
        if args.until == step.name:
            break


def setup_command(subparser, ctx):
    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config
        names = [s.name for s in workflow.steps]
        subparser.add_argument("-u", "--until", choices=names, default=names[-1])
        subparser.set_defaults(func=run)
