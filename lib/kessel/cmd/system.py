def system_list(args, ctx, senv):
    print("local")

    if ctx.deployment_dir:
        environments_dir = ctx.deployment_dir / "environments"

        for d in [c.name for c in environments_dir.iterdir() if c.is_dir()]:
            print(d)


def system_activate(args, ctx, senv):
    ctx.system = args.system


def setup_command(subparser):
    subparsers = subparser.add_subparsers()
    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=system_list)
    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("system")
    activate_cmd.set_defaults(func=system_activate)
