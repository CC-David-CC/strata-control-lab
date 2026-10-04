"""Discover only checked-in, independently reviewable instrument page modules."""
from importlib import import_module
from pathlib import Path

MODULES = [import_module('.'+p.stem,__package__) for p in sorted(Path(__file__).parent.glob('instrument_page_*.py'))]
MODULES.sort(key=lambda m:(bool(m.PAGE.get('applied')),m.PAGE['id']))
PAGES = [m.PAGE for m in MODULES]
RUNNERS = {m.PAGE['id']:m.run for m in MODULES}
if len(RUNNERS)!=len(PAGES):
    raise ValueError('Duplicate instrument page ID')
