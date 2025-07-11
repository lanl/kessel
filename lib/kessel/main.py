import argparse
import kessel.cmd.init as init_cmd
import kessel.cmd.deploy as deploy_cmd
import kessel.cmd.system as system_cmd
import kessel.cmd.env as env_cmd
import kessel.cmd.workflow as workflow_cmd
import kessel.cmd.pipeline as pipeline_cmd
import kessel.cmd.run as run_cmd
import kessel.cmd.build_env as build_env_cmd

from kessel.context import Context
from kessel.util import ShellEnvironment


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
    subparsers = parser.add_subparsers()

    init_cmd.setup_command(subparsers.add_parser("init"))
    deploy_cmd.setup_command(subparsers.add_parser("deploy"))
    system_cmd.setup_command(subparsers.add_parser("system"))
    env_cmd.setup_command(subparsers.add_parser("env"))
    build_env_cmd.setup_command(subparsers.add_parser("build-env"))
    workflow_cmd.setup_command(subparsers.add_parser("workflow"))
    pipeline_cmd.setup_command(subparsers.add_parser("pipeline"), ctx)
    run_cmd.setup_command(subparsers.add_parser("run"), ctx)

    args, extra = parser.parse_known_args()
    senv.debug = args.shell_debug
    args.func(args, extra, ctx, senv)
    return 0
