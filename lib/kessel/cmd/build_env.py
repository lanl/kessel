from pathlib import Path
import os

def build_env(args, ctx, senv):
    if ctx.build_env.exists():
        os.execl(os.environ["SHELL"], os.environ["SHELL"], "--rcfile", ctx.build_env, "-i")

def setup_command(subparser):
    subparser.set_defaults(func=build_env)
