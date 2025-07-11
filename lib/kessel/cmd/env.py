import glob
from pathlib import Path


def env_list(args, extra, ctx, senv):
    if ctx.deployment_dir and ctx.system:
        env_dir = ctx.deployment_dir / "environments" / ctx.system
        env_glob = (env_dir / "**" / "*.yaml").resolve()
        envs = sorted(glob.glob(str(env_glob), recursive=True))

        for e in envs:
            print(Path(e).relative_to(env_dir).parent)


def env_activate(args, extra, ctx, senv):
    ctx.environment = args.env
    if ctx.deployment_dir:
        if ctx.system:
            env_dir = ctx.deployment_dir / "environments" / ctx.system / ctx.environment
            if env_dir.exists():
                senv.echo(f"Activating {ctx.system} environment {ctx.environment}")
                senv.eval(f"spack env activate -d {env_dir}")
            else:
                raise Exception(
                    f"Unknown environment '{ctx.environment}' for system '{ctx.system}'!"
                )
        else:
            raise Exception("No active system!")
    elif ctx.system and ctx.system == "local":
        senv.echo(f"Activating {ctx.system} environment {ctx.environment}")
        senv.eval(f"spack env activate {ctx.environment}")
    else:
        raise Exception("No active deployment!")


def setup_command(subparser):
    subparsers = subparser.add_subparsers()

    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=env_list)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("env")
    activate_cmd.set_defaults(func=env_activate)
