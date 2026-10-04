from .applied import page,run_applied

PAGE=page('transaction')


async def run(ctx,opt):
    return await run_applied(ctx,'transaction')
