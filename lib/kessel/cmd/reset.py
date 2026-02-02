from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment


def reset(args: Namespace, ctx: Context, senv: ShellEnvironment):
    ctx.reset()


def setup_command(subparser: ArgumentParser, ctx: Context):
    subparser.set_defaults(func=reset)
