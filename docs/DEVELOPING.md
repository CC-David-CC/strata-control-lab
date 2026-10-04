# Developing and testing

From the repository root, in a Python 3.11+ virtual environment:

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
python -m playwright install chromium
python -m control_lab --port 8878
```

In another terminal using the same environment:

```sh
python -m control_lab.check_quality --base-url http://127.0.0.1:8878 --downloads evidence/downloads
python -m control_lab.check_windowshop --base-url http://127.0.0.1:8878 --downloads evidence/walkthrough-downloads
python -m control_lab.check_portable_archive control_lab/static/strata-control-lab-39-offline-examples.zip --output evidence/archive-check.json
python -m control_lab.check_exports --base-url http://127.0.0.1:8878 --downloads evidence/downloads --evidence evidence/quality/browser/results.json
```

The quality check walks all phases at desktop and phone sizes and runs both
portable lesson settings with sockets blocked. The walkthrough check exercises
navigation and all saved mocks. Export checks reproduce the generated scripts
against that run's hashes and compare the downloaded ZIP with the frozen shipped
archive. Trace durations can differ on a fresh replay; native fixture bytes and
the bundled ZIP stay fixed. Browser downloads need
internet only when initially installing Chromium. Fresh check output lives in
ignored `evidence/`; selected release receipts belong in `docs/validation/`.

To test installation independently of a source checkout:

```sh
python -m build
python -m venv .venv-wheel
```

Install the generated `.whl` from `dist/` into `.venv-wheel`, change to a folder
outside the checkout, and run that environment's `python -m control_lab`. Confirm
all 39 pages and 342 recordings are present. The release qualification below
uses this installed-wheel server, not an editable install.

`python -I tools/check_installed.py --output evidence/installed.json` also verifies
that imports resolve to `site-packages` and replays every default workload with
outbound socket operations blocked. Run it with the wheel environment's Python,
using the full script path if you changed folders.

## Responsibilities

| Location | Responsibility |
| --- | --- |
| `control_lab/app.py` | Loopback UI API and run lifecycle |
| `control_lab/client.py` | Exact recording replay and optional authenticated HTTP calls |
| `control_lab/scenarios.py`, research/instrument modules | Explicit experimental workloads |
| `control_lab/static/` | Local UI, fonts, portable calculations and downloadable archive |
| `control_lab/data/` | Immutable native recordings, captures, requests and diagnostic evidence |
| `tests/` | Contracts, exact math checks, failure cases and offline replay |
| `docs/provenance/` | Origin hashes, inherited native identity and historical self-review |
| `docs/validation/` | Standalone extraction/installation test receipts |

New native measurements require an explicit live command and a fresh output
directory. For example:

```sh
python -m control_lab.capture --page choice --base-url http://127.0.0.1:8080 --output evidence/new-choice
python -m control_lab.capture_instrument pressure --base-url http://127.0.0.1:8080 --output evidence/new-instruments
```

Use `STRATA_API_KEY` when required. Review requests for private content before
committing fixtures. Capture commands refuse an existing recording destination.
Never relabel mocks as fresh native results or overwrite an old measurement to
make a test pass. A changed prompt requires a new matching recording.

New engine capabilities belong in Strata. This repository may demonstrate them
after their contract and independent evidence are established.
