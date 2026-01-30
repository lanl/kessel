import os
from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment


def build_env(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    os.execl(os.environ["SHELL"], os.environ["SHELL"],
             "--rcfile", os.environ["KESSEL_BUILD_ENV"], "-i")


def setup_command(subparser: ArgumentParser):
    subparser.set_defaults(func=build_env)
