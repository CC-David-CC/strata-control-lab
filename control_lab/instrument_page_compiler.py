from .applied import page,run_applied

PAGE=page('compiler')


async def run(ctx,opt):
    return await run_applied(ctx,'compiler')
