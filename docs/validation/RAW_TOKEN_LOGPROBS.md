# Inline raw-token score update

Validated October 6, 2026 on Windows with Python 3.13 and headless Playwright
Chromium. The native inference receipts are inherited Linux measurements; no
fresh model inference was run for this client display update.

- `python -m pytest -q`: 180 passed. Non-failing dependency/cache warnings were emitted.
- `python tools/check_raw_tokens.py --base-url http://127.0.0.1:8879`: 14 desktop/phone checks plus a delayed native SSE check. Every displayed full score matched its exported token. All 29 streamed token scores appeared before the terminal result. Missing scores remained missing, labels were escaped and no page errors occurred.
- `python -m control_lab.check_browser --base-url http://127.0.0.1:8879`: all 28 existing checks passed, including the ten original wire examples, controller, export and phone layouts.
- `python -m control_lab.check_portable_archive control_lab/static/strata-control-lab-39-offline-examples.zip`: all 39 pages, 78 calculations and 312 mock calls passed with networking blocked.
- Wheel built with the repository's declared setuptools/build tools. Installed into a separate target `site-packages`, then tested with isolated Python and the existing test environment's dependencies. All 39 pages, 342 recordings and ten request examples replayed with networking blocked. The source package was not imported. The new wheel assets matched the source.
- Compared the original Git archive's 383 data/archive files directly with the working tree: every file, including the original ZIP, was byte-identical.

See [the machine-readable receipt](raw-token-logprobs.json) for the base commit,
ZIP/wheel hashes and detailed browser results. Fresh captures stay under ignored
`evidence/raw-token-logprobs/`; the original qualification receipts remain intact.
