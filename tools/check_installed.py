"""Smoke-test a wheel with isolated Python, even outside the source checkout.

Run: /path/to/venv/python -I /path/to/tools/check_installed.py --output receipt.json
"""
import argparse
import asyncio
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import control_lab
from control_lab.catalog import PAGES
from control_lab.client import Backend, Context, recording_roots
from control_lab.paths import DATA, STATIC
from control_lab.scenarios import run_page


async def check():
    # A wheel must supply these resources without the repository on sys.path.
    location = Path(control_lab.__file__).resolve()
    assert 'site-packages' in location.parts, location
    assert len(PAGES) == 39
    assert sum(len(list(root.glob('*.json'))) for root in recording_roots()) == 342
    assert (STATIC/'strata-control-lab-39-offline-examples.zip').is_file()
    assert (STATIC/'OFL.txt').is_file()
    assert len(list((DATA/'requests').glob('*.json'))) == 10

    def block_network(event, args):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo'):
            raise AssertionError('Recorded mode attempted outbound networking')
    sys.addaudithook(block_network)
    rows=[]
    async def emit(kind, data):
        pass
    for page in PAGES:
        async with Backend('recorded', base_url='http://127.0.0.1:1') as backend:
            ctx=Context(backend, emit)
            result=await run_page(ctx, page['id'], {})
            assert result is not None
            rows.append(dict(page=page['id'], calls=len(ctx.calls)))
    return dict(
        package=importlib.metadata.version('strata-control-lab'),
        installed_in_site_packages=True,
        platform=platform.platform(), python=sys.version,
        network_blocked=True, native_recordings=342, request_examples=10,
        pages=rows,
        dependencies={name:importlib.metadata.version(name)
                      for name in ['fastapi','uvicorn','httpx','chess','pydantic','starlette']},
    )


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    receipt=asyncio.run(check())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(receipt, indent=2)+'\n').encode())
    print(f"Installed wheel: {len(receipt['pages'])} pages, 342 recordings, network blocked")
