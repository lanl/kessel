from pathlib import Path
import os

def clean_build_env(args, ctx, senv):
    if args.env_file.exists():
        tmp_file = f"{args.env_file}.tmp"
        with open(args.env_file, "r") as r, open(tmp_file, "w") as w:
            for line in r:
                if not ( line.startswith("FLUX_") or line.startswith("SLURM_") ):
                    print(line, file=w)
            print(f"PS1='(build) {os.environ['KESSEL_PARENT_PROMPT']}'", file=w)
        os.rename(tmp_file, args.env_file)

def setup_command(subparser):
    subparser.add_argument("env_file", type=Path)
    subparser.set_defaults(func=clean_build_env)
