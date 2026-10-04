"""Read-only assets installed with the lab; never resolve a Strata checkout."""
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
DATA = PACKAGE / 'data'
STATIC = PACKAGE / 'static'
