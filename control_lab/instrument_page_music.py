from .applied import page,run_applied

PAGE=page('music')


async def run(ctx,opt):
    return await run_applied(ctx,'music')
