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

"""Edit the active workflow."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from kessel.context import Context
from kessel.util import ShellEnvironment


def locate_workflow_file(base_dir: Path, name: str) -> Path | None:
    search_paths = [
        base_dir / f"{name}.py",
        base_dir / name / "__init__.py",
        base_dir / name / "workflow.py",
    ]
    for p in search_paths:
        if p.exists():
            return p
    return None


def edit_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Edit the current workflow."""
    if args.workflow:
        if args.workflow in set(ctx.workflows):
            assert ctx.kessel_dir is not None
            workflows_dir = ctx.kessel_dir / "workflows"
            workflow_path = locate_workflow_file(workflows_dir, args.workflow)
        else:
            raise Exception(f"Unknown workflow '{args.workflow}'")
    else:
        workflow = ctx.workflow_config
        assert workflow is not None
        assert isinstance(workflow.workflow_dir, Path)
        workflow_path = locate_workflow_file(workflow.workflow_dir, workflow.workflow)

    senv.eval(f"${{EDITOR:-vim}} {workflow_path}")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the edit command."""
    subparser.add_argument("workflow", nargs="?")
    subparser.set_defaults(func=edit_workflow)
