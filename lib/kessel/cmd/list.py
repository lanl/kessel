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

"""List available workflows."""

from argparse import ArgumentParser, Namespace

from kessel.colors import COLOR_GREEN, COLOR_PLAIN
from kessel.context import Context
from kessel.util import ShellEnvironment


def list_workflows(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """List all available workflows, highlighting the active one."""
    for wf in ctx.workflows:
        if wf == ctx.workflow:
            print(f"{COLOR_GREEN}{wf}{COLOR_PLAIN}")
        else:
            print(wf)


def setup_command(subparser: ArgumentParser, ctx: Context):
    """Setup the list command."""
    subparser.set_defaults(func=list_workflows)
