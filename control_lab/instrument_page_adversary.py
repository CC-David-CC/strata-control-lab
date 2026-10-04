from .applied import page,run_applied

PAGE=page('adversary')


async def run(ctx,opt):
    return await run_applied(ctx,'adversary')
