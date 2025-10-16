from pathlib import Path
import shutil


def init(args, extra, ctx, senv):
    kessel_dir = args.directory / ".kessel"
    workflow_dir = kessel_dir / "workflows" / "default"

    ctx.workflow = None

    if not kessel_dir.exists():
        workflow_dir.mkdir(parents=True)
        print("Creating kessel configuration based on default template")
        template_dir = ctx.kessel_root / "share" / "kessel" / "templates" / "spack-config"
        shutil.copytree(template_dir, args.directory, dirs_exist_ok=True)


def setup_command(subparser):
    subparser.add_argument("directory", nargs="?", default=Path.cwd(), type=Path)
    subparser.set_defaults(func=init)
