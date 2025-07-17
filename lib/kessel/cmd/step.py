import sys
from kessel.cmd.workflow import status


def step(args, extra_args, ctx, senv):
    workflow = ctx.workflow_config
    st = next(s for s in workflow.steps if s.name == args.step)

    senv.section_start(
        st.name, st.title, collapsed=st.collapsed
    )
    senv.echo(status(ctx, st.name))
    ignored_args = len(sys.argv) - len(extra_args) - 1
    senv.eval(f"shift {ignored_args}")
    senv.eval(f"source {st.script} " + " ".join([f"\"{a}\"" for a in extra_args]))
    senv.eval("ret=$?")

    senv.section_end(st.name)
    senv.eval("test $ret -eq 0 && ", end="")
    ctx.run_state = st.name


def setup_command(subparser, ctx):
    subparsers = subparser.add_subparsers()

    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config

        for s in workflow.steps:
            name = s.name
            step_cmd = subparsers.add_parser(name)
            step_cmd.set_defaults(func=step, step=name)
