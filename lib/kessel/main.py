import sys
import argparse
import kessel.cmd.init as init_cmd
import kessel.cmd.deploy as deploy_cmd
import kessel.cmd.workflow as workflow_cmd
import kessel.cmd.step as step_cmd
import kessel.cmd.run as run_cmd
import kessel.cmd.reset as reset_cmd
import kessel.cmd.build_env as build_env_cmd
import kessel.cmd.activate as activate_cmd
import kessel.cmd.list as list_cmd
import kessel.cmd.status as status_cmd
import kessel.cmd.edit as edit_cmd
from kessel.context import Context
from kessel.util import ShellEnvironment
from kessel import __version__


def main():
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
    subparsers = parser.add_subparsers()
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
    edit_cmd.setup_command(subparsers.add_parser("edit"), ctx)
    args = parser.parse_args()
    senv.debug = args.shell_debug
    senv.eval("set --")  # makes sure sourced scripts don't see our args
    try:
        if hasattr(args, "func"):
            args.func(args, ctx, senv)
        else:
            parser.print_help(sys.stderr)
            return 1
    except Exception as e:
        print("ERROR:", e)
        return 1
    return 0
