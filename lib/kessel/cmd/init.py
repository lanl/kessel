import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context


def init(args: Namespace, ctx: Context) -> None:
    kessel_dir = args.directory / ".kessel"

    ctx.workflow = None

    if not kessel_dir.exists():
        kessel_dir.mkdir(parents=True)
        print(f"Creating kessel configuration based on {args.template} template")
        template_dir = ctx.kessel_root / "share" / "kessel" / "templates" / args.template
        shutil.copytree(template_dir, args.directory, dirs_exist_ok=True)
    else:
        raise Exception("Existing .kessel folder found.")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    template_dir = ctx.kessel_root / "share" / "kessel" / "templates"
    templates = [f.name for f in template_dir.iterdir() if f.is_dir()]
    subparser.add_argument("-t", "--template", choices=templates, default="spack-project")
    subparser.add_argument("directory", nargs="?", default=Path.cwd(), type=Path)
    subparser.set_defaults(func=init)
