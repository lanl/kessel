def reset(args, ctx, senv):
    ctx.reset()


def setup_command(subparser, ctx):
    subparser.set_defaults(func=reset)
