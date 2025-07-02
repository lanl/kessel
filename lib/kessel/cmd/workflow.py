import textwrap
import sys
from ruamel.yaml import YAML

PROGRESS_STEP_COMPLETE = "●"
PROGRESS_STEP_PENDING = "○"
PROGRESS_BAR_PENDING = "▭"
PROGRESS_BAR_COMPLETE = "▬"

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
    steps = ctx.workflow_config["steps"]
    names = [s["name"] for s in steps]
    captions = [step_lines(s["title"]) for s in steps]
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


def workflow_list(args, ctx, senv):
    for wf in ctx.workflows:
        print(wf)


def workflow_activate(args, ctx, senv):
    ctx.workflow = args.name


def workflow_status(args, ctx, senv):
    senv.echo(status(ctx, ctx.pipeline_state))


def workflow_get(args, ctx, senv):
    yaml = YAML(typ="safe")
    yaml.default_flow_style = False
    yaml.width = 256
    yaml.dump(ctx.workflow_config, sys.stdout)


def setup_command(subparser):
    subparsers = subparser.add_subparsers()

    list_cmd = subparsers.add_parser("list")
    list_cmd.set_defaults(func=workflow_list)

    activate_cmd = subparsers.add_parser("activate")
    activate_cmd.add_argument("name")
    activate_cmd.set_defaults(func=workflow_activate)

    status_cmd = subparsers.add_parser("status")
    status_cmd.set_defaults(func=workflow_status)

    get_cmd = subparsers.add_parser("get")
    get_cmd.set_defaults(func=workflow_get)
