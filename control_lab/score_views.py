"""Page-specific score provenance; these descriptions never change a calculation."""
RAW = ('Each generated token carries target logprob before grammar, penalties and sampling. '
       'Raw probability is exp(logprob), with the denominator over the full target vocabulary. '
       'Every score belongs to its selected request and exact preceding token path.')
MASK = (RAW + ' These instruments also inspect a pure temperature-1 grammar mask. '
        'Complete answer rows recover raw label p from native legal-set weight q times surviving mass Z; '
        'the selected token logprob below is the direct target score, not that recovered row.')
SCOPE = ('The raw receipt stays attached to the captured request. Page dials recalculate derived views; '
         'they do not rerun the model or replace token scores. Neither model probability nor a derived '
         'weight is calibrated truth. Missing top-N alternatives stay unknown.')

DERIVED = {
    'choice': 'Answer weights normalize the measured label scores over the declared answer set. The raw vocabulary probabilities need not sum to one over those labels.',
    'boolean': 'Yes/No weight conditions on the declared meanings. It is not the raw probability of the Yes token or a measured probability that the proposition is true.',
    'score': 'Rubric weights condition on declared levels. Expected score, variance, entropy, margin and peakedness are arithmetic summaries of those weights.',
    'candidates': 'A path adds conditional token logprobs along its own prefix. Group scores sum disjoint measured paths; final weights condition on the listed candidate paths, not all grammar strings.',
    'controller': 'The application restricts allowed actions, conditions their measured weights on that set and applies a hold threshold. State transitions and legality are code rules, separate from model preference.',
    'rerank': 'Each source answer is a measured token path. Source-ranking weights normalize those candidate scores; they are not calibrated relevance or recall.',
    'graph': 'Normalized Yes/No edge measurements feed a global code-owned admissibility solver. Edge weight, chosen graph structure and probability that the document is correct are different quantities.',
    'scene': 'Native JSON supplies text. Normalized semantic probes, their mean and code geometry checks choose a scene; the mean is not a joint probability or a visual-image judgment.',
    'wire': 'The token view converts logprob to raw probability without changing the denominator. Grammar may force a low-probability token; hidden reasoning and tool syntax are not scored answer content.',
    'speculation': 'Draft probability and raw target verification use different heads, vocabularies and prefixes. Retained target output is distinct from rejected proposal scores; suffix lookup has no draft distribution.',
    'performance': 'The main bars are request latency in milliseconds, not token confidence. Some benchmark arms intentionally omit scores; cache, queue, prefill, decode and transport affect elapsed time.',
    'samplers': 'strata_sampling.probability is the final selection weight after ordered operators and constraints. It is separate from raw token p. Support and entropy cover all survivors, not just displayed top-N.',
    'sampler-sandbox': 'The sandbox recomputes synthetic masking, filtering and temperature weights. These are teaching calculations, not native model scores or extra implemented native samplers.',
    'tictactoe': 'Answer weights guide a legal move. Minimax outcomes, opponent policy and regret are exact code-owned game calculations; a model action weight is not a win probability.',
    'chess': 'Measured move-path weights cover the disclosed shortlist. Code checks every legal move for mate or stalemate; model preference is not proof of mate or complete move coverage.',
    'poker': 'Action weights and modeled opponent call probabilities feed an assumed payoff calculation. Expected chips and utility regret are not raw token probabilities or measured real-player behavior.',
    'thermal': 'Action weights choose among code-permitted fan settings. The temperature dynamics, safety shield and control baseline are simulations; their temperatures and regret are not model probabilities.',
    'scheduler': 'Normalized action weights choose a ready job. The simulated queue, dependency rules, deadlines and lateness are code-owned state and costs, not confidence scores.',
    'context': 'Each prompt variant generates its own token path. Path scores and measured latency belong to those contexts; editing the prompt is not an arbitrary KV-tensor edit.',
    'observer': 'Normalized semantic probe weights form a feature vector used by the observer. Distance, reconstruction and fault decisions are derived calculations, not direct vocabulary probabilities.',
    'calibration': 'The semantic Yes weight is compared with labeled cases to calculate calibration, error and retained coverage. Those empirical summaries do not calibrate every raw token score.',
    'information': 'Native action weights choose an observation. Information gain and posterior beliefs use the disclosed analytic observation model; they are not direct logprobs from the language model.',
    'search': 'Normalized semantic measurements feed a bounded candidate utility search and hard checks. Averaged scores, accepted proposals and search utility are not joint truth probabilities.',
    'frontier': 'The chart combines recorded native selector timings with explicit bandwidth, power and forward-time assumptions. It calculates latency/cost bounds, not native token probabilities or a measured roofline.',
    'research-map': 'The graph organizes published experiments and research proposals. It makes no token-probability measurement and does not assign a numerical probability that a proposed optimization works.',
    'circuit': 'Complete legal-set weights define finite semantic conditionals. Circuit products and marginals follow those declared variable dependencies; they are not raw vocabulary probabilities or independent truth evidence.',
    'control': 'Legal-set semantic weights and log-odds feed a controller with explicit state, thresholds and code-selected actions. A forced commit token is not evidence the model independently preferred that action.',
    'counterexamples': 'Semantic weights score disclosed candidates. Counterexample tests, consistency gaps and selection rules are derived comparisons on those measurements, not an independent correctness guarantee.',
    'future': 'Finite semantic conditionals feed the disclosed policy and horizon calculations. Future success is policy-dependent arithmetic over measured meanings, not the raw probability of a success token.',
    'pressure': 'Under the pure temperature-1 mask, log Z = selected raw logprob - log(selected q). Pressure is -log Z. The synthetic 60/40 dial is separately labeled and is not a native measurement.',
    'sensitivity': 'Changes in semantic log-odds form finite differences and measurement directions. Signed sensitivity and projected scores are derived quantities, not probabilities or direct internal model vectors.',
    'adversary': 'Native legal-set answer weights express the declared security judgments. The toy attacker, checker, admitted candidates and regret are application rules; the weights are not validated detector accuracy.',
    'budget': 'Native legal-set weights rank observation or action choices. Expected information benefit, observation price, utility and regret use the disclosed toy model, not raw token confidence or real allocation guarantees.',
    'camouflage': 'Semantic answer weights compare descriptions of the same unfinished job. Observer decisions, verification rules and the framing baseline are derived comparisons, not calibrated correctness probabilities.',
    'compiler': 'Native answer weights rank candidate rewrites. The exact toy compiler/behavior checks and utility establish local validity independently of the language model scores.',
    'divider': 'Answer weights rank simulated resistor circuits. Nominal voltage, tolerance ranges and the disclosed utility are code calculations, separate from semantic model preferences or physical measurements.',
    'music': 'Answer weights rank candidate notes in the finite toy alphabet. The supplied surprise model and numerical rules are separate calculations; they do not establish human musical quality or calibrated preference probability.',
    'proof': 'Native answer weights choose among proposed proof actions. The toy proof referee establishes its own validity and utility; model preference is not a proof.',
    'transaction': 'Answer weights rank proposed transaction actions. Exact toy state invariants, commit checks and regret are code-owned outcomes, not model confidence or real financial guidance.',
}
PURE_MASK = {'circuit', 'control', 'counterexamples', 'future', 'pressure', 'sensitivity',
             'adversary', 'budget', 'camouflage', 'compiler', 'divider', 'music', 'proof', 'transaction'}
SCORE_VIEWS = {name: dict(raw=MASK if name in PURE_MASK else RAW,
                         derived=text, scope=SCOPE, raw_kind='native')
               for name, text in DERIVED.items()}
SCORE_VIEWS['speculation'].update(
    raw_kind='diagnostic', raw='Existing native diagnostic receipts expose raw target logprobs on retained emitted token IDs. Proposal and draft scores are separate; this page makes no new Chat request.')
SCORE_VIEWS['sampler-sandbox'].update(
    raw_kind='synthetic', raw='The before distribution is softmax over disclosed synthetic logits. It is a complete teaching distribution, not a truncated native row or a new model measurement.')
SCORE_VIEWS['frontier'].update(
    raw_kind='no_token_row', raw='This page reads recorded native selector timing receipts. It has no Chat token-probability row; durations and assumed bandwidth are not probabilities.')
SCORE_VIEWS['research-map'].update(
    raw_kind='no_token_row', raw='This page is an explicit research map. It has no generated tokens, raw probabilities or new model calls.')
