"""Capture one independent native instrument without modifying other receipts."""
import argparse,asyncio,json,sys,time
from pathlib import Path
from .client import Backend,Context
from .instrument_registry import RUNNERS
from .scenarios import run_page

async def main(args):
    output=Path(args.output)/args.page;output.mkdir(parents=True,exist_ok=True)
    if list((output/'recordings').glob('*.json')):
        raise ValueError('Capture already exists; preserve it and choose a fresh --output directory')
    async def emit(kind,data):
        if kind=='step' and data['status']=='completed':print(data['title'],round(data['wall_ms']),'ms',flush=True)
    async with Backend('live',base_url=args.base_url,capture=output/'recordings') as backend:
        ctx=Context(backend,emit);started=time.perf_counter();result=await run_page(ctx,args.page,{})
        data=dict(page=args.page,result=result,receipt=ctx.receipt(),wall_ms=(time.perf_counter()-started)*1000)
    (output/'capture.json').write_bytes(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False).encode())
    print(json.dumps(dict(page=args.page,requests=len(ctx.calls),wall_ms=data['wall_ms'])))

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('page',choices=RUNNERS)
    p.add_argument('--base-url',default='http://127.0.0.1:8080')
    p.add_argument('--output',default='evidence/captures');asyncio.run(main(p.parse_args()))
