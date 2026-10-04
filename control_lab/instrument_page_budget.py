from .applied import page,run_applied

PAGE=page('budget')


async def run(ctx,opt):
    return await run_applied(ctx,'budget')
