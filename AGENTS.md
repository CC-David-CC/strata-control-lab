# Working on the Control Lab

This repository is a Python/FastAPI educational client. Strata is a separate
inference server reached over HTTP. Keep engine code, CUDA, model installation,
hardware management and native feature contributions out of this repository.

- Install with `python -m pip install -e ".[dev]"`; run `python -m control_lab`.
- Run `python -m pytest -q`. See `docs/DEVELOPING.md` for browser and wheel checks.
- Keep offline replay and the automatic tour working without a model or network.
- Automatic tours use recorded data only. Live inference is a manual action.
- Preserve exact raw recordings in `control_lab/data`. Label simulations,
  analytical examples and fresh native measurements separately.
- New captures go under ignored `evidence/`, never into installed package data.
- The UI binds to loopback and holds server credentials on the Python side.
- Keep docs plain and measured. Distinguish raw token probabilities, constrained
  sampling weights and semantic scores; none is an independent truth guarantee.
- Preserve original MIT attribution and the bundled font license.
