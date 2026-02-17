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


def edit_workflow(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Edit the current workflow."""
    if args.workflow:
        if args.workflow in set(ctx.workflows):
            assert ctx.kessel_dir is not None
            workflows_dir = ctx.kessel_dir / "workflows"

            # Check for .py file first
            py_file = workflows_dir / f"{args.workflow}.py"
            if py_file.exists():
                workflow_path = py_file
            # Then check for __init__.py
            elif (workflows_dir / args.workflow / "__init__.py").exists():
                workflow_path = workflows_dir / args.workflow / "__init__.py"
            # Fall back to legacy workflow.py
            else:
                workflow_path = workflows_dir / args.workflow / "workflow.py"
        else:
            raise Exception(f"Unknown workflow '{args.workflow}'")
    else:
        workflow = ctx.workflow_config

        assert workflow is not None
        assert isinstance(workflow.workflow_dir, Path)

        # Determine the actual file to edit
        if (workflow.workflow_dir.parent / f"{workflow.workflow}.py").exists():
            workflow_path = workflow.workflow_dir.parent / f"{workflow.workflow}.py"
        elif (workflow.workflow_dir / "__init__.py").exists():
            workflow_path = workflow.workflow_dir / "__init__.py"
        else:
            workflow_path = workflow.workflow_dir / "workflow.py"

    senv.eval(f"${{EDITOR:-vim}} {workflow_path}")


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the edit command."""
    subparser.add_argument("workflow", nargs="?")
    subparser.set_defaults(func=edit_workflow)
