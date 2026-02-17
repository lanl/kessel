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

import argparse
import sys
import threading
import time

import kessel.cmd.activate as activate_cmd
import kessel.cmd.build_env as build_env_cmd
import kessel.cmd.create as create_cmd
import kessel.cmd.deploy as deploy_cmd
import kessel.cmd.edit as edit_cmd
import kessel.cmd.init as init_cmd
import kessel.cmd.list as list_cmd
import kessel.cmd.reset as reset_cmd
import kessel.cmd.run as run_cmd
import kessel.cmd.status as status_cmd
import kessel.cmd.step as step_cmd
import kessel.cmd.workflow as workflow_cmd
from kessel import __version__
from kessel.context import Context
from kessel.util import ShellEnvironment


def spinner(stop_event: threading.Event, message: str = "Working") -> None:
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    i = 0
    while not stop_event.is_set():
        if i > 20:
            dots = "." * ((i // 4) % 4) + " " * (3 - (i // 4) % 4)
            sys.stdout.write(f"\r \u001b[94m{frames[i % len(frames)]}\u001b[0m {message}{dots}")
            sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    # Clear spinner line
    sys.stdout.write("\r" + " " * (len(message) + 8) + "\r")
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def main() -> int:
    senv = ShellEnvironment()
    ctx = Context(senv)
    parser = argparse.ArgumentParser(
        prog="kessel", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--shell-debug",
        action="store_true",
        help="output shell commands instead of executing them",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command")
    init_cmd.setup_command(subparsers.add_parser("init"), ctx)
    deploy_cmd.setup_command(subparsers.add_parser("deploy"), ctx)
    build_env_cmd.setup_command(subparsers.add_parser("build-env"))
    workflow_cmd.setup_command(subparsers.add_parser("workflow"))  # deprecated
    step_cmd.setup_command(subparsers.add_parser("step"), ctx)
    run_cmd.setup_command(subparsers.add_parser("run"), ctx)
    reset_cmd.setup_command(subparsers.add_parser("reset"), ctx)
    # New top-level commands (replacing workflow subcommands)
    list_cmd.setup_command(subparsers.add_parser("list"), ctx)
    activate_cmd.setup_command(subparsers.add_parser("activate"), ctx)
    status_cmd.setup_command(subparsers.add_parser("status"), ctx)
    create_cmd.setup_command(subparsers.add_parser("create"), ctx)
    edit_cmd.setup_command(subparsers.add_parser("edit"), ctx)
    args = parser.parse_args()
    senv.debug = args.shell_debug
    senv.eval("set --")  # makes sure sourced scripts don't see our args
    interactive = sys.stdout.isatty() and not args.shell_debug and args.command in ("run", "step")
    try:
        if hasattr(args, "func"):
            if interactive:
                stop_event = threading.Event()
                t = threading.Thread(target=spinner, args=(stop_event,))
                t.start()

            args.func(args, ctx, senv)
        else:
            parser.print_help(sys.stderr)
            return 1
    except Exception as e:
        print("ERROR:", e)
        return 1
    finally:
        if interactive:
            stop_event.set()
            t.join()
    return 0
