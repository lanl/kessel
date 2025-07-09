from kessel.cmd.workflow import status


def step(args, ctx, senv):
    for prop in ctx.visible_variables:
        if hasattr(args, prop):
            setattr(ctx, prop, getattr(args, prop))

    workflow = ctx.workflow_config
    step = next(s for s in workflow["steps"] if s["name"] == args.step)

    senv.section_start(
        step["name"], step["title"], collapsed=step.get("collapsed", False)
    )
    senv.echo(status(ctx, step["name"]))

    variables = {}
    for k, v in workflow["variables"].items():
        variables[k] = ctx.evaluate(v, [args, variables])

    script = step["script"]
    for line in script:
        if isinstance(line, str):
            senv.eval("[ $? ] && " + ctx.evaluate(line, [args, variables]))
        elif isinstance(line, dict):
            if "buildenv" in line and line["buildenv"]:
                senv.begin_subshell(env_script=ctx.build_env)

            if isinstance(line["run"], str):
                senv.eval(
                    "[ $? ] && "
                    + ctx.evaluate(line["run"], [args, variables])
                )
            elif isinstance(line["run"], list):
                for sline in line["run"]:
                    for subcmd in sline.splitlines():
                        senv.eval(
                            "[ $? ] && "
                            + ctx.evaluate(subcmd, [args, variables])
                        )

            if "buildenv" in line and line["buildenv"]:
                senv.end_subshell()
    senv.eval("ret=$?")

    senv.section_end(step["name"])
    senv.eval("test $ret -eq 0 && ", end="")
    ctx.pipeline_state = step["name"]


def setup_command(subparser, ctx):
    subparsers = subparser.add_subparsers()

    if ctx.kessel_dir and ctx.workflow_config:
        workflow = ctx.workflow_config

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

        variables = {}
        for k, v in workflow["variables"].items():
            variables[k] = ctx.evaluate(v, [variables])

        for s in workflow["steps"]:
            pipeline_step_cmd = subparsers.add_parser(s["name"])
            _add_arguments(
                pipeline_step_cmd, s.get("arguments", []), variables
            )
            pipeline_step_cmd.set_defaults(func=step, step=s["name"])
