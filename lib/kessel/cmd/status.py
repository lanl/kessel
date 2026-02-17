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

"""Display workflow status."""

import textwrap
from argparse import ArgumentParser, Namespace

from kessel.context import Context
from kessel.util import ShellEnvironment

PROGRESS_STEP_COMPLETE = "●"
PROGRESS_STEP_PENDING = "○"
PROGRESS_BAR_PENDING = "▭"
PROGRESS_BAR_COMPLETE = "▬"


def step_lines(title: str) -> list[str]:
    min_width = len(max(title.split(), key=len)) + 2
    return [
        line.center(min_width)
        for line in textwrap.wrap(
            title, width=min_width, break_long_words=False, break_on_hyphens=False
        )
    ]


def format_status(ctx: Context, step: str | None = None) -> str:
    """Format the workflow status display."""
    if ctx.workflow_config is None:
        raise Exception(f"{ctx.workflow} workflow can not be found!")

    steps = ctx.workflow_config.steps
    captions = [step_lines(ctx.workflow_config.get_step_title(s)) for s in steps]
    lines = len(max(captions, key=len))
    widths = [len(c[0]) for c in captions] + [0]
    step_size = [0] + [
        (widths[i] + widths[i + 1]) // 2 - widths[i] % 2 for i in range(len(widths) - 1)
    ]

    s = " \n"
    s += "  "
    s += " " * (widths[0] // 2)
    completed = steps.index(step) if step in steps else -1
    for i, _ in enumerate(steps):
        if i <= completed:
            s += PROGRESS_BAR_COMPLETE * step_size[i]
            s += PROGRESS_STEP_COMPLETE
        else:
            s += PROGRESS_BAR_PENDING * step_size[i]
            s += PROGRESS_STEP_PENDING
    s += "\n \n"

    for i in range(lines):
        s += "  "
        for c in captions:
            if i < len(c):
                s += c[i]
            else:
                s += " " * len(c[0])
        s += "\n"
    s += " \n"
    return s


def show_status(args: Namespace, ctx: Context, senv: ShellEnvironment) -> None:
    """Display the current workflow status."""
    senv.echo(format_status(ctx, ctx.run_state))


def setup_command(subparser: ArgumentParser, ctx: Context) -> None:
    """Setup the status command."""
    subparser.set_defaults(func=show_status)
