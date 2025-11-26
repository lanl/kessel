import textwrap
import sys

PROGRESS_STEP_COMPLETE = "●"
PROGRESS_STEP_PENDING = "○"
PROGRESS_BAR_PENDING = "▭"
PROGRESS_BAR_COMPLETE = "▬"

COLOR_GREEN = "\033[1;32m"
COLOR_BLUE = "\033[1;34m"
COLOR_MAGENTA = "\033[1;35m"
COLOR_CYAN = "\033[1;36m"
COLOR_PLAIN = "\033[0m"


def step_lines(title):
    min_width = len(max(title.split(), key=len)) + 2
    return [
        line.center(min_width)
        for line in textwrap.wrap(
            title, width=min_width, break_long_words=False, break_on_hyphens=False
        )
    ]


def status(ctx, step=None):
    if ctx.workflow_config is None:
        raise Exception(f"{ctx.workflow} workflow can not be found!")

    steps = ctx.workflow_config.steps
    names = [s.name for s in steps]
    captions = [step_lines(s.title) for s in steps]
    lines = len(max(captions, key=len))
    widths = [len(c[0]) for c in captions] + [0]
    step_size = [0] + [
        (widths[i] + widths[i + 1]) // 2 - widths[i] % 2 for i in range(len(widths) - 1)
    ]

    s = " \n"
    s += "  "
    s += " " * (widths[0] // 2)
    completed = names.index(step) if step in names else -1
    for i, _ in enumerate(names):
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


def workflow_list(args, extra, ctx, senv):
    for wf in ctx.workflows:
        if wf == ctx.workflow:
            print(f"{COLOR_GREEN}{wf}{COLOR_PLAIN}")
        else:
            print(wf)


def workflow_activate(args, extra, ctx, senv):
    ctx.workflow = args.name


def workflow_status(args, extra, ctx, senv):
    senv.echo(status(ctx, ctx.run_state))


def workflow_edit(args, extra, ctx, senv):
    workflow = ctx.workflow_config

    if args.step == "init":
        senv.eval(f"${{EDITOR:-vim}} {workflow.init_script}")
    else:
        for s in workflow.steps:
            if args.step == s.name:
                senv.eval(f"${{EDITOR:-vim}} {s.script}")


def setup_command(subparser):
    subparsers = subparser.add_subparsers()

    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=workflow_list)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("name")
    activate_cmd.set_defaults(func=workflow_activate)

    status_cmd = subparsers.add_parser("status")
    status_cmd.set_defaults(func=workflow_status)

    edit_cmd = subparsers.add_parser("edit")
    edit_cmd.add_argument("step")
    edit_cmd.set_defaults(func=workflow_edit)
