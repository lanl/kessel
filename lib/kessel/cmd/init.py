from pathlib import Path


def init(args, extra, ctx, senv):
    kessel_dir = args.directory / ".kessel"
    workflow_dir = kessel_dir / "workflows" / "default"

    ctx.workflow = None

    if not kessel_dir.exists():
        workflow_dir.mkdir(parents=True)
        # TODO copy template folder


def setup_command(subparser):
    subparser.add_argument("directory", nargs="?", default=Path.cwd(), type=Path)
    subparser.set_defaults(func=init)
