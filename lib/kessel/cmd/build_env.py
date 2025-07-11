import os


def build_env(args, extra, ctx, senv):
    os.execl(os.environ["SHELL"], os.environ["SHELL"],
             "--rcfile", os.environ["KESSEL_BUILD_ENV"], "-i")


def setup_command(subparser):
    subparser.set_defaults(func=build_env)
