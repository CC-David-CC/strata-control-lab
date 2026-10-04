from .applied import page,run_applied

PAGE=page('divider')


async def run(ctx,opt):
    return await run_applied(ctx,'divider')
