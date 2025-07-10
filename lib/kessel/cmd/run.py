import os
import sys

from kessel.cmd.workflow import COLOR_BLUE, COLOR_PLAIN


def run(args, ctx, senv):
    ctx.pipeline_state = None

    for prop in ctx.visible_variables:
        if hasattr(args, prop):
            setattr(ctx, prop, getattr(args, prop))

    workflow = ctx.workflow_config

    variables = {}
    for k, v in workflow["variables"].items():
        variables[k] = ctx.evaluate(v, [args, variables])

    for prop in ctx.visible_variables:
        if prop in variables:
            setattr(ctx, prop, variables[prop])

    if "CI" in os.environ:
        print(f"{COLOR_BLUE} ")
        print("######################################################################")
        print(" ")
        print("To recreate this CI run, follow these steps:")
        print(" ")
        if ctx.system != "local":
            print(f"ssh {ctx.system}")
        print(f"cd /your/{ctx.project}/checkout")
        if "LLNL_FLUX_SCHEDULER_PARAMETERS" in os.environ:
            print("flux alloc", os.environ["LLNL_FLUX_SCHEDULER_PARAMETERS"])
        elif "SCHEDULER_PARAMETERS" in os.environ:
            print("salloc", os.environ["SCHEDULER_PARAMETERS"])
        if "KESSEL_INIT" in os.environ:
            print(os.environ["KESSEL_INIT"])
        if ctx.workflow != "default":
            print("kessel workflow activate", ctx.workflow)
        print("kessel", *sys.argv[1:])
        print(" ")
        print("######################################################################")
        print(f"{COLOR_PLAIN} ", flush=True)

    for step in workflow["steps"]:
        senv.eval(f"[ $? -eq 0 ] && kessel pipeline {step['name']}")
        if args.until == step["name"]:
            break


def setup_command(subparser, ctx):
    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config
        names = [s["name"] for s in workflow["steps"]]

        def _add_arguments(cmd, cmd_args, local_vars=[]):
            for a in cmd_args:
                atype = list(a.keys())[0]
                if atype == "argument":
                    arg = a["argument"]
                    pos_args = []
                    kw_args = {}
                    for p in arg:
                        if isinstance(p, str):
                            pos_args.append(p)
                        elif isinstance(p, dict):
                            kw_args.update(
                                {k: ctx.evaluate(v, [local_vars]) for k, v in p.items()}
                            )
                    try:
                        cmd.add_argument(*pos_args, **kw_args)
                    except Exception as e:
                        print("add_argument params:", pos_args, kw_args)
                        raise e
        args = []

        for s in workflow["steps"]:
            args += s.get("arguments", [])

        _add_arguments(
            subparser, args, workflow.get("variables", {})
        )
        subparser.add_argument("-u", "--until", choices=names, default=names[-1])
        subparser.set_defaults(func=run)
