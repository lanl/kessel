import sys


def run(args, extra_args, ctx, senv):
    ctx.run_state = None
    workflow = ctx.workflow_config

    if workflow is None:
        raise Exception(f"{ctx.workflow} workflow can not be found!")

    if workflow.init_script:
        ignored_args = len(sys.argv) - len(extra_args) - 1
        senv.eval(f"shift {ignored_args}")
        senv.eval(f"source {workflow.init_script} " + " ".join([f"\"{a}\"" for a in extra_args]))

    for step in workflow.steps:
        senv.eval(f"kessel step {step.name}")
        if args.until == step.name:
            break


def setup_command(subparser, ctx):
    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config
        names = [s.name for s in workflow.steps]
        subparser.add_argument("-u", "--until", choices=names, default=names[-1])

    subparser.set_defaults(func=run)
