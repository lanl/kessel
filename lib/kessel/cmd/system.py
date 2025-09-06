COLOR_GREEN = "\033[1;32m"
COLOR_PLAIN = "\033[0m"

def system_list(args, extra, ctx, senv):
    systems = ["local"]

    if ctx.deployment_dir:
        environments_dir = ctx.deployment_dir / "environments"
        systems += [c.name for c in environments_dir.iterdir() if c.is_dir()]

    for s in systems:
        if ctx.system == s:
            print(f"{COLOR_GREEN}{s}{COLOR_PLAIN}")
        else:
            print(s)

def system_activate(args, extra, ctx, senv):
    ctx.system = args.system


def setup_command(subparser):
    subparsers = subparser.add_subparsers()
    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=system_list)
    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("system")
    activate_cmd.set_defaults(func=system_activate)
