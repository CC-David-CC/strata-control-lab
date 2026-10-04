# Engine compatibility

The recorded lab is self-contained. Live mode uses a separate Strata server's
`POST /v1/chat/completions` endpoint. No Strata Python module, engine binary,
model file or GPU library is imported into this application.

| Lab workload | Live backend requirement |
| --- | --- |
| Generated text and wire inspection | Chat Completions JSON / SSE, including the requested reasoning/tool channels |
| Raw token and candidate scores | `logprobs`, `top_logprobs`, raw target scores before masking/sampling |
| Finite legal answers and state controllers | Native `grammar` / GBNF enforcement |
| Typed scenes and JSON examples | The branch's strict JSON Schema implementation, including its validator |
| Native sampler pages and semantic/applied instruments | `strata_sampler` with `inspect:true`, advertised as `ordered-host-v1` |
| Speculation diagnostics | Bundled native diagnostic receipts; no new diagnostic HTTP endpoint is claimed |

For the full set of live workloads, use the published
[work/samplers branch](https://github.com/CC-David-CC/Strata-a5500/tree/work/samplers),
pinned for these measurements at
[`450285f3c90748057a02648345e6c3973519a710`](https://github.com/CC-David-CC/Strata-a5500/commit/450285f3c90748057a02648345e6c3973519a710).
Its [sampler guide](https://github.com/CC-David-CC/Strata-a5500/blob/450285f3c90748057a02648345e6c3973519a710/docs/SAMPLERS.md)
and [native model/build guide](https://github.com/CC-David-CC/Strata-a5500/blob/450285f3c90748057a02648345e6c3973519a710/docs/LOGPROBS.md)
describe the engine setup. Build that native version; changing only the Python
lab cannot add capabilities to an older binary. `/props` must advertise
`strata_capabilities.samplers` as `ordered-host-v1` for sampler inspection.

The earlier
[logprobs contribution](https://github.com/CC-David-CC/Strata-a5500/tree/work/logprobs-675)
at `2243cb1c5b1a87270731d8b8a76e4af001f96f97` supplies the foundation API features,
but lacks the later sampler inspection needed by several pages. Responses and
the earlier [GBNF / Codex work](https://github.com/CC-David-CC/Strata-a5500/tree/work/gbnf)
are engine contributions with their own scope. The lab does not require a
Responses endpoint or run Codex.

The native ordered selector is a CPU reference implementation after the existing
GPU forward pass. Min-P, sigma, top-k, top-p, XTC and temperature have explicit
ordering. DRY-like and other feedback demonstrations in the sandbox are labeled
simulations; they are not advertised as extra native sampler implementations.

The instruments verify complete one-token answer-code support, normalized
inspection and the disclosed temperature/mask contract. A compatible HTTP
shape alone does not establish equivalent score semantics. Errors remain
visible instead of silently substituting another model or weakening a constraint.

See [connection commands](GETTING_STARTED.md#connect-your-own-strata-server) for
Windows and Linux. The lab neither launches nor reconfigures Strata, MTP, suffix
speculation, model caches or hardware. Context experiments send explicit prompt
variants; they do not edit arbitrary KV tensors or change grammar mid-stream.
