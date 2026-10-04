from .applied import page,run_applied

PAGE=page('camouflage')


async def run(ctx,opt):
    return await run_applied(ctx,'camouflage')
