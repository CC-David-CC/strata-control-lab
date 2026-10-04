# Control Lab quality rubric v1

This rubric is frozen before the first quality assessment. Passing functional tests
does not by itself earn a quality score. This is a reproducible engineering
self-review, not a user study or an independent design award.

The unit is one default recorded example, its automatic walkthrough, and its
downloaded Python bundle. Score each criterion 0, 1, or 2 using the anchors below.
Each of the three surfaces scores out of 10. A page's score is the mean of its
three surfaces. The site score is the mean of all page scores, including analytical
pages. Include failed examples; never remove them to improve the average.

## Recorded example

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| R1: Testable purpose | No concrete question | Concrete question only | Question plus a comparison, baseline, or falsifiable outcome |
| R2: Inspectable inputs | Inputs hidden | Partial input or constraint | Exact inputs and applicable GBNF/JSON; explicitly says when no model request exists |
| R3: Provenance | Invented or ambiguous results | Source category named | Native receipts or disclosed synthetic inputs, with raw numbers and their meaning |
| R4: Checkable result | Unsupported conclusion | Calculation described | Calculation or oracle independently exercised by tests; measured result visible |
| R5: Honest boundary | Overclaims | Generic caveat | Specific failure/limitation and a concrete next gate |

## Walkthrough and display

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| D1: Works without clicks | Cannot complete | Manual assistance needed | Loads, walks, advances and loops; pause and reduced motion work |
| D2: Plain explanation | Jargon alone | Purpose understandable | Question, rule and result understandable without opening technical details |
| D3: Meaningful movement | Decoration only | Highlights static output | At least one explained comparison, state change, or revealed measurement with accurate captions |
| D4: Readable presentation | Broken/obscured | Usable with avoidable friction | Desktop and phone checked; principal step target and caption readable, no horizontal overflow |
| D5: Inspectable mechanism | Missing request/code | Available but disconnected | Exact request/constraint and portable calculation accessible, with their relationship to the displayed example explained |

## Portable bundle

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| B1: Batteries included | Needs service/dependency | Offline setup needed | Standard-library script runs with networking blocked; Windows and Linux commands included |
| B2: Inspectable evidence | Opaque dump | Some evidence readable | Requests, constraints, responses and provenance inspectable; no embedded secret |
| B3: Reproduce the lesson | Prints only a saved conclusion | Replays evidence without central calculation | Recalculates the central illustrated quantity/transition from bundled inputs; agrees with the page |
| B4: Try a change | Cannot change anything meaningful | Editing possible but unexplained | A documented, bounded parameter/intervention changes an offline result; invalid inputs rejected |
| B5: Faithful scope | Mock/live confusion | Scope clear with reproduction gap | Printed lesson identifies the reproduced/default view, assumptions and limits; changing a fixture cannot masquerade as new model inference |

## Passing gate

All requested example families must have an executable, inspectable demonstration
or an explicitly identified engine prerequisite accompanied by a working bounded
analytical demonstration. A proposal card alone does not satisfy example coverage.

The mean must be at least **8.0/10**, every page at least **7.0/10**, and R2, R3, R5,
B1 and B5 must have no zero. Document each score with an evidence reference and
the reason for every deduction. Report baseline and final scores under this same
rubric; do not change anchors after seeing the results.

Browser evidence must cover every page, desktop and phone, its automatic phases,
console/network failures and downloadable bundle. Inspect rendered screenshots as
well as DOM checks. Computational checks must compare against independently
calculated expectations, not just repeat the implementation. Native, recorded,
synthetic, assumed and unimplemented paths must remain visibly distinct.

This gate does not claim that the model is calibrated, the toy tasks generalize,
the UI has been validated with children or researchers, or an engineering roofline
has been reached. Those require separate evidence.
