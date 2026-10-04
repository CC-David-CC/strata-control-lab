from .applied import page,run_applied

PAGE=page('proof')


async def run(ctx,opt):
    return await run_applied(ctx,'proof')
