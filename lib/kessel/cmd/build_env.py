# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.

import os
from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment


def build_env(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    os.execl(os.environ["SHELL"], os.environ["SHELL"],
             "--rcfile", os.environ["KESSEL_BUILD_ENV"], "-i")


def setup_command(subparser: ArgumentParser):
    subparser.set_defaults(func=build_env)
