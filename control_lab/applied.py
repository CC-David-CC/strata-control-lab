"""Small native probes attached to eight independently checked toy domains."""
from .instrument_math import page as instrument_page,measure,commit_label
from .static.applied_math import cases_for,case_oracle

DESCRIPTIONS={
 'music':('Musical tension','A melody inside a fence.','A small note alphabet keeps the toy playable. Numerical preferences and a supplied surprise model can still change which note comes next.','A four-note teaching system with fixed harmonic rules. Native weights are preferences over named notes, not acoustics or listener quality. The finite controller is arithmetic outside the engine.','Compare rendered melodies with uniform/Markov baselines under blind listening. Add timing and history before claiming a musical sampler.'),
 'proof':('Proof tactic budget','Words propose. A checker proves.','Watch three tiny proof states. A grammar makes tactic names valid; a proof checker decides whether each tactic actually works.','A small natural-deduction checker covers implication introduction, conjunction elimination and exact assumptions. Independent native state probes do not constitute an adaptive theorem prover. Exhaustive search already solves this tiny example.','Connect a sandboxed real prover, preserve proof objects, and compare held-out theorems at equal checker-call budgets.'),
 'compiler':('Compiler rewrites','A prettier expression may cost more.','Compare four rewrites of the same integer expression. Code rejects the wrong meaning before counting the work.','Exact degree-at-most-two polynomial coefficients establish equivalence for all integers. Operation weights are declared assumptions, not CPU timings. The four-candidate enumerative baseline is complete.','Compile verified candidates, control benchmark warmup/noise and compare held-out workloads. A symbolic cost reduction is not a measured speedup.'),
 'divider':('Circuit sketches','Let physics veto a good-looking answer.','Pick a tiny simulated circuit, then vary its resistors. The best nominal answer may have a less comfortable error range.','Four ideal voltage dividers, independent resistor tolerance and exact corner enumeration. There is no physical actuation, electronics safety claim or hidden circuit simulator. Native preferences are compared with the explicit formula.','Add loading, thermal limits and a qualified circuit simulator; compare equal-budget search with domain heuristics before testing physical hardware.'),
 'transaction':('Transaction choreography','The grammar cannot freeze the world.','A snapshot permits a reservation. Another writer changes the version. Watch the commit check stop the stale command.','The simulated reserve operation checks version and stock before changing either. GBNF controls emitted command shape; it does not replace database concurrency control. The sequential toy is not a distributed transaction system.','Use a transactional database operation, inject actual interleavings, and verify exactly-once business effects separately from command validity.'),
 'camouflage':('Wording robustness','Same facts. Different costume.','Give the same unfinished job three descriptions. Measure whether the observer still sends it to verification.','Structured facts stay fixed. Native distributions measure phrasing sensitivity. A direct structured-state rule supplies a code-only baseline; this small selected set is not a robustness benchmark.','Use a held-out paraphrase generator, label permutations and fixed budgets. Measure controller regret as well as probability drift.'),
 'adversary':('Adversarial legal actions','Allowed does not mean wise.','All four answers fit the grammar. Some still make a bad decision. Search a small bank of descriptions for the largest mistake.','The failed-test fact is fixed. An explicit action utility defines regret; native weights remain answer preferences. This bounded three-description search can fail to find a harmful perturbation and must retain that result.','Expand the perturbation space with exact semantic invariants, evaluate held-out attacks, and compare regret at equal query budgets.'),
 'budget':('Inference budget','Spend another call only when it helps.','An extra observation has a price. Compare the expected benefit with acting on the information already available.','A binary hidden-state prior and symmetric sensor likelihood are supplied by code. Bayes and expected reward determine a break-even cost. Native action weights are never treated as sensor likelihoods, calibration or electricity cost.','Measure actual model/verification time and held-out decision outcomes. Learn observation models before using expected value to allocate a real inference budget.'),
}


def page(name):
    title,headline,simple,detail,gate=DESCRIPTIONS[name]
    result=instrument_page(name,title,headline,simple,detail,['bounded application','native preferences','GBNF','code oracle'],gate)
    result['applied']=True
    return result


async def run_applied(ctx,name):
    cases=cases_for(name)
    for case in cases:
        measurement=await measure(ctx,case['state'],'Which listed choice best serves the stated task?',case['choices'],case['name']+' / measure alternatives')
        case['measurement']=measurement;weights=[r['weight'] for r in measurement['rows']]
        selected=max(case['allowed'],key=lambda i:weights[i]);utilities=case_oracle(name,case)
        oracle=max(case['allowed'],key=lambda i:utilities[i]);label=chr(65+selected)
        case['commit']=await commit_label(ctx,case['state'],[chr(65+i) for i in case['allowed']],label,case['name']+' / emit checked code')
        case.update(selected=selected,oracle=oracle,utilities=utilities,
                    regret=utilities[oracle]-utilities[selected],
                    uniform_utility=sum(utilities[i] for i in case['allowed'])/len(case['allowed']))
    return dict(kind=name,cases=cases,
                semantics='Independent bounded cases, not one adaptive trajectory. The model supplies native answer weights. Code checks admissibility and selects the highest-weight permitted code; native GBNF emits that code. The exact utility oracle is a separate baseline.',
                next_gate=DESCRIPTIONS[name][-1])
