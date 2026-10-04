# Getting started

Follow the Windows or Linux commands in the [README](../README.md). Installing
this project installs only the Python web app and its dependencies. It does not
install an inference engine or download model weights.

## Watch, pause, inspect

1. Open [the local index](http://127.0.0.1:8876). It starts the recorded tour after
   12 seconds. **Stay on the index** keeps the gallery open.
2. Each experiment starts automatically, compares two compact
   question → rule → result settings, then opens its detailed view and advances.
3. **Pause / explore**, typing, scrolling or clicking a control pauses the tour.
   **Restart recorded tour** restores that page's defaults. **Next** advances now.
4. Open **The actual request, with its rules** for the exact request JSON, GBNF,
   JSON Schema or sampler settings. Choose a request when a run contains several.
5. **Download Python + mocks** saves a standalone example. **Download receipt**
   saves the measurements. Pages with no HTTP calls show their analytical or
   diagnostic inputs instead of inventing a request.

Hidden tabs stop advancing and reduced-motion preferences remove nonessential
animation. Each page follows a plain link to the next, passing no model context
or page state. Add `?manual=1` to a page URL to start paused.

Changing a compact-panel control recalculates saved evidence. It does not
produce a fresh model answer to a changed prompt. Recorded requests require
exactly matching saved inputs; unavailable recordings produce a clear error.

## Run a downloaded Python example

From the folder containing the extracted examples:

```powershell
# Windows: Python standard library only
py .\strata-choice-example.py
py .\strata-samplers-example.py --all
py .\strata-circuit-example.py --request 1 --show
py .\strata-pressure-example.py --lesson-only --value 1
```

```sh
# Ubuntu / Linux
python3 ./strata-choice-example.py
python3 ./strata-samplers-example.py --all
python3 ./strata-circuit-example.py --request 1 --show
python3 ./strata-pressure-example.py --lesson-only --value 1
```

`--all` replays every included mock. `--lesson-only` prints the calculation;
`--value` changes that lesson's named, bounded parameter. `--output result.json`
saves it. `--show` displays the exact request and constraints. The downloaded
file contains its help text and the actual arithmetic.

## Connect your own Strata server

First follow [engine compatibility](ENGINE_COMPATIBILITY.md). Recorded mode is
available independently of that setup. Start the lab with the server address
in the environment; **do not append `/v1`** to the address.

```powershell
$env:STRATA_BASE_URL = 'http://YOUR-SERVER:8080'
$env:STRATA_API_KEY = 'your-configured-strata-key'
.\.venv\Scripts\python.exe -m control_lab
```

```sh
export STRATA_BASE_URL=http://YOUR-SERVER:8080
export STRATA_API_KEY=your-configured-strata-key
.venv/bin/python -m control_lab
```

Use `http://127.0.0.1:8080` for a server on the same machine or a local tunnel.
Omit the key variable when your loopback server does not require one. A LAN
Strata server must use its existing `--api-key` protection. The lab UI itself
stays on loopback; its Python process keeps the server key out of browser data
and exports. Plain HTTP on a LAN is not encrypted; use your usual secure tunnel
when needed.

Open an experiment, select **Live model**, then **Run experiment**. This pauses
the automatic tour. **Stop** closes the HTTP connection; Strata owns native
cancellation and output draining. Live UI results are not written to disk
automatically. Analytical pages remain analytical and the speculation page
continues to inspect its separately captured native diagnostics.

A downloaded script can send **one selected request**:

```sh
python strata-pressure-example.py --request 1 --live-url http://127.0.0.1:8080
```

It does not adapt an old multi-step trace to new answers or execute tools.
Live mode cannot be combined with `--all`, `--lesson-only` or `--value`.

## Common problems

| What you see | What to do |
| --- | --- |
| The browser cannot connect | Keep the Python terminal open; check its printed port and errors. |
| Port already in use | Start with `--port 8877`, then open `http://127.0.0.1:8877`. |
| No matching native recording | Restart the recorded tour to restore default inputs, or run the edited request live. |
| Live connection failed | Check the base URL, server process, LAN/tunnel and API key. |
| Unsupported grammar, JSON or sampler | Use the compatible native branch/build described in the engine guide. |
| Unsupported answer labels/tokenizer | The measurement cannot establish complete single-token support; use a supported model or redesign and requalify the probe. |

There is no automatic cloud fallback and no fabricated successful result when
the backend lacks a required capability.
