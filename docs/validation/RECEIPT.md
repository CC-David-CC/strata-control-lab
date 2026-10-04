# Standalone extraction qualification

2026-10-04. Fresh repository, branch `main`. This receipt belongs to the initial
extraction commit; resolve that commit with `git log --reverse --format=%H`.
The source lab checkpoint is `8c99143e05234c02f2ccf41cc3361746b09773cd`.
It was local and unpublished; source hashes are preserved in the
[extraction manifest](../provenance/extraction.json).

## What changed

The Python package is now `control_lab`, installed with `pip install .` and run
with `python -m control_lab`. Runtime assets and all 342 native recordings are
package data. The UI calls Strata only over HTTP. Source-checkout paths, engine
code, installers, hardware experiments, old PR drafts, duplicate example ZIPs
and unrelated Strata history are excluded. The original checkout remained clean
at the original commit. No new native inference was performed for this extraction.

Capture commands write outside installed data and reject an existing recording
destination. Documentation now starts with standalone Windows/Linux commands.
The inherited MIT and font licenses are retained. Fresh `main` is configured
for `CC-David-CC/strata-control-lab`; publication steps are in
[PUBLISH.md](../PUBLISH.md).

## Commands and results

Executed on Windows 11 with Python 3.13.15 in a new virtual environment:

| Command / check | Result | Evidence |
| --- | --- | --- |
| `python -m pip wheel . --wheel-dir dist`; install the resulting wheel into the new environment | Installed successfully; `pip check` passed | [Installed package](installed-wheel.json) |
| `python -I tools/check_installed.py --output ...` from outside the source tree | All 39 workloads; 342 packaged recordings; outbound sockets blocked | [Wheel replay](installed-wheel.json) |
| `python -m pytest -q --junitxml=docs/validation/pytest.xml` | 172 passed, one upstream Starlette/httpx deprecation warning | [Test results](pytest.xml) |
| `python -m control_lab.check_quality --base-url http://127.0.0.1:8878 --output evidence/quality/browser --downloads evidence/downloads` | 39 pages; 391 phases on desktop and phone; 78 portable calculations; loop closed | [Phase results](browser-phases.json) |
| `python -m control_lab.check_windowshop --base-url http://127.0.0.1:8878 --output evidence/walkthrough --downloads evidence/walkthrough-downloads` | Automatic page navigation, pause/resume, live-mode opt-in, gallery start/opt-out, reduced motion and every default mock passed | [Navigation](navigation.json) |
| `python -m control_lab.check_portable_archive ... --output docs/validation/portable-archive.json` | 39 scripts; 78 calculations; 312 mocked calls; sockets blocked | [Archive replay](portable-archive.json) |
| `python -m control_lab.check_exports --base-url http://127.0.0.1:8878 --downloads evidence/archive-files --output docs/validation/exports.json` | Frozen 39 scripts assemble identically; HTTP ZIP hash and literal escaping passed | [Export checks](exports.json) |
| `python -m control_lab.check_exports --base-url http://127.0.0.1:8878 --downloads evidence/downloads --evidence evidence/quality/browser/results.json --output docs/validation/fresh-exports.json` | Newly downloaded scripts reproduce this run's qualified hashes | [Fresh exports](fresh-exports.json) |
| Source byte/hash comparison | All packaged data and the portable ZIP match the extraction source | [Extraction check](extraction-check.json) |
| Markdown target check; pinned engine refs checked with `git ls-remote` and their docs with `git cat-file -e` | No missing local document targets; linked engine commits exist on the fork | [Links](links.json) |

The browser server ran the installed wheel using isolated Python, with its
working directory outside this repository and `STRATA_BASE_URL` set to an
unreachable loopback port. Browser requests outside the local app were blocked;
there were no unexpected network requests or browser exceptions. New index and
phone previews were copied from this run. The full transient screenshot
collection stays in ignored `evidence/`.

The qualified wheel SHA-256 is
`fd4db52081af8e10dbf450c4e19993c3991f3997dcc79728e95770a49fc58dce`.
The unchanged portable archive SHA-256 is
`e4129cd4cbc2f75273de30fcc01f7f1420a0f1d2360094a7dd75c185a2315c1d`.
Trace timings in fresh downloads can differ; recording contents and calculations
retain their disclosed meaning.

## Remaining boundaries

This is an application/package qualification, not a new Strata engine test or
fresh model evaluation. Linux and Python 3.11 are configured in the included
GitHub Actions matrix; those new CI jobs have not run before initial publication.
The portable ZIP was also tested on Linux before extraction; this receipt claims
the new Windows run only. Browser correctness does not establish usability or
the inherited self-review score independently.

The next gate is creating the empty GitHub repository, pushing this fresh
history, then inspecting its public landing page and CI. Live model features
continue to require the independently published
[engine dependency](../ENGINE_COMPATIBILITY.md).
