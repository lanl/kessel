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

import sys
from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment


def workflow_list(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel workflow list' is deprecated. Use 'kessel list' instead.", file=sys.stderr)
    senv.eval("kessel list")


def workflow_activate(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel workflow activate' is deprecated. Use 'kessel activate' instead.", file=sys.stderr)
    senv.eval(f"kessel activate {args.name}")


def workflow_status(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel workflow status' is deprecated. Use 'kessel status' instead.", file=sys.stderr)
    senv.eval("kessel status")


def workflow_edit(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    print("Warning: 'kessel workflow edit' is deprecated. Use 'kessel edit' instead.", file=sys.stderr)
    senv.eval("kessel edit")


def setup_command(subparser: ArgumentParser) -> None:
    subparsers = subparser.add_subparsers()

    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=workflow_list)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("name")
    activate_cmd.set_defaults(func=workflow_activate)

    status_cmd = subparsers.add_parser("status")
    status_cmd.set_defaults(func=workflow_status)

    edit_cmd = subparsers.add_parser("edit")
    edit_cmd.set_defaults(func=workflow_edit)
