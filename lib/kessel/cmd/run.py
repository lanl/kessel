import os

from kessel.cmd.workflow import COLOR_BLUE, COLOR_PLAIN


def run(args, ctx, senv):
    ctx.pipeline_state = None

    for prop in ctx.visible_variables:
        if hasattr(args, prop):
            setattr(ctx, prop, getattr(args, prop))

    if "CI" in os.environ:
        print(f"{COLOR_BLUE} ")
        print("######################################################################")
        print(" ")
        print("To recreate this CI run, follow these steps:")
        print(" ")
        print(f"ssh {args.system}")
        print(f"cd /your/{ctx.project}/checkout")
        if "LLNL_FLUX_SCHEDULER_PARAMETERS" in os.environ:
            print("flux alloc", os.environ["LLNL_FLUX_SCHEDULER_PARAMETERS"])
        elif "SCHEDULER_PARAMETERS" in os.environ:
            print("salloc", os.environ["SCHEDULER_PARAMETERS"])
        print(f"kessel run -s {ctx.system} -e {ctx.environment} {ctx.project_spec}")
        print(" ")
        print("######################################################################")
        print(f"{COLOR_PLAIN} ", flush=True)

    workflow = ctx.workflow_config
    for step in workflow["steps"]:
        senv.eval(f"[ $? ] && kessel pipeline {step['name']}")
        if args.until == step["name"]:
            break


def setup_command(subparser, ctx):
    if ctx.kessel_dir:
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

        _add_arguments(
            subparser, workflow.get("arguments", []), workflow.get("variables", {})
        )
        subparser.add_argument("-u", "--until", choices=names, default=names[-1])
        subparser.set_defaults(func=run)
