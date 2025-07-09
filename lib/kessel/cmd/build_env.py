from pathlib import Path
import argparse
import os
import subprocess


def generate(args, ctx, senv):
    if args.env_type == "spack":
        subprocess.call(
            f"spack build-env --dump {ctx.build_env} {ctx.project}", shell=True)
        tmp_file = f"{ctx.build_env}.tmp"
        with open(ctx.build_env, "r") as r, open(tmp_file, "w") as w:
            for line in r:
                if not (line.startswith("FLUX_") or line.startswith("SLURM_")):
                    print(line, file=w)
            print(
                f"PS1='(build) {os.environ['KESSEL_PARENT_PROMPT']}'", file=w)
        os.rename(tmp_file, ctx.build_env)


def set_build_env(args, ctx, senv):
    ctx.build_env = args.env_file


def build_env(args, ctx, senv):
    os.execl(os.environ["SHELL"], os.environ["SHELL"],
             "--rcfile", ctx.build_env, "-i")


def setup_command(subparser):
    subparsers = subparser.add_subparsers()

    generate_cmd = subparsers.add_parser("generate")
    generate_cmd.add_argument("--type", dest="env_type", choices=("spack",),
                              help="type of build environment to generate", default="spack")
    generate_cmd.set_defaults(func=generate)

    set_cmd = subparsers.add_parser("set")
    set_cmd.add_argument(
        "env_file", help="sourcable build environment file", type=Path)
    set_cmd.set_defaults(func=set_build_env)

    subparser.set_defaults(func=build_env)
