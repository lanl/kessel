from pathlib import Path
import shutil


def init(args, extra, ctx, senv):
    kessel_dir = args.directory / ".kessel"

    if not kessel_dir.exists():
        kessel_dir.mkdir(parents=True)
        print("Creating deployment configuration based on default template")
        template_dir = ctx.kessel_root / "share" / "kessel" / "templates" / "deployment-config"
        shutil.copytree(template_dir, args.directory, dirs_exist_ok=True)


def setup_command(subparser):
    subparsers = subparser.add_subparsers()
    init_cmd = subparsers.add_parser("init")
    init_cmd.add_argument("directory", nargs="?", default=Path.cwd(), type=Path)
    init_cmd.set_defaults(func=init)
