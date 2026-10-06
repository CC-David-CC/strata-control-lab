# Coverage of raw and derived views

All 39 pages were audited through the actual browser UI at desktop and phone sizes. Each has its own raw-source and derived-view explanation. Every request selector was exercised; all 439 scored answer tokens across 312 captured requests retained their exact logprob and showed `exp(logprob)` as raw p. The diagnostic page separately shows three retained target token IDs.

| Example | Raw source | Requests | Scored answer tokens |
|---|---|---:|---:|
| choice | native | 3 | 3 |
| boolean | native | 2 | 2 |
| score | native | 3 | 3 |
| candidates | native | 5 | 23 |
| controller | native | 6 | 6 |
| rerank | native | 9 | 9 |
| graph | native | 10 | 10 |
| scene | native | 13 | 59 |
| wire | native | 1 | 29 |
| speculation | diagnostic | 0 | 0 |
| performance | native | 19 | 31 |
| samplers | native | 9 | 23 |
| sampler-sandbox | synthetic | 0 | 0 |
| tictactoe | native | 14 | 14 |
| chess | native | 7 | 10 |
| poker | native | 9 | 9 |
| thermal | native | 24 | 24 |
| scheduler | native | 12 | 12 |
| context | native | 8 | 8 |
| observer | native | 18 | 18 |
| calibration | native | 14 | 14 |
| information | native | 4 | 4 |
| search | native | 10 | 10 |
| frontier | no_token_row | 0 | 0 |
| research-map | no_token_row | 0 | 0 |
| circuit | native | 7 | 7 |
| control | native | 6 | 6 |
| counterexamples | native | 25 | 29 |
| future | native | 7 | 7 |
| pressure | native | 4 | 6 |
| sensitivity | native | 21 | 21 |
| adversary | native | 6 | 6 |
| budget | native | 6 | 6 |
| camouflage | native | 6 | 6 |
| compiler | native | 4 | 4 |
| divider | native | 6 | 6 |
| music | native | 4 | 4 |
| proof | native | 6 | 6 |
| transaction | native | 4 | 4 |

`native` means direct selected-token scores from captured Chat requests. Semantic instruments separately explain their reconstructed label rows and legal-set weights. `diagnostic` uses retained target token IDs from an existing diagnostic receipt. `synthetic` labels teaching logits. `no_token_row` means timing/research inputs; no native token probability is invented.

The automatic tour passed all 469 phases with desktop/phone visibility checks. Every page now starts by visiting its raw and derived explanations. Both lesson calculations per page (78 total) reproduced offline. All ten original wire contract examples were checked separately, including empty scored-content responses.

The added raw-score ZIP contains 39 updated Python examples with the same original native request/response pairs. It prints page-specific explanations and supports `--tokens`. All 39 ran with networking blocked, including 312 replayed calls and 78 calculations. The original ZIP and all original recording files remain byte-identical.

Python regression: 184 passed. An isolated installation of the rebuilt wheel replayed 39 pages and 342 recordings with networking blocked. These are client/replay checks, not new model inference or broader native-platform qualification.

See [page definitions](../control_lab/score_views.py), [source and math](RAW_TOKEN_LOGPROBS.md), [all-page browser receipt](validation/every-score-view.json), and [companion archive manifest](validation/raw-score-archive.json).
