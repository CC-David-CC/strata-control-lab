"""Small, portable calculations behind the question/rule/result panels.

Standard library only. This exact source is included in every Python download.
Inputs are the captured experiment, never an invented new model response. A knob
changes a disclosed calculation on those inputs; it does not rescore a new prompt.
"""
import itertools
import math
import statistics


def _spec(question, rule, knob, default, compare, low, high, integer=False):
    return dict(question=question, rule=rule, knob=knob, default=default,
                compare=compare, low=low, high=high, integer=integer)


LESSON_SPECS = {
    'choice': _spec('Which ticket queue gets this message?', 'Compare the three saved label scores. Heat flattens their relative weights; it adds no evidence.', 'Reweighting temperature', 1, 2, .1, 3),
    'boolean': _spec('Does this message ask to cancel?', 'Normalize the saved Yes and No scores. A number near one is a strong preference, not proof.', 'Reweighting temperature', 1, 2, .1, 3),
    'score': _spec('How serious is the outage?', 'Multiply each rubric value by its answer weight, then add. The rating comes from the whole distribution.', 'Reweighting temperature', 1, 2, .1, 3),
    'candidates': _spec('Read the failure first, or start changing things?', 'Add token logprobs along each saved path, then sum path mass inside each finite group. A length penalty changes the objective.', 'Length penalty exponent', 0, 1, 0, 1),
    'controller': _spec('May the simulated repair take its next step?', 'Keep only state-legal actions. Hold the recorded action if its relative legal weight falls below the threshold.', 'Required legal-action weight', 0, .999, 0, 1),
    'rerank': _spec('Which sources help explain cancellation?', 'Compute each source’s expected relevance separately, then keep those above the cutoff.', 'Minimum relevance', 0, .9, 0, 1),
    'graph': _spec('Which text links can coexist?', 'Search every small edge subset. Reject cycles and competing attachments, then maximize useful edge weight.', 'Edge cost / threshold', .5, .9, .01, .99),
    'scene': _spec('Which valid drawing best fits the instruction?', 'Average the three saved text probes. Optionally charge for disagreement between them; code still checks geometry.', 'Disagreement penalty', 0, 1, 0, 2),
    'wire': _spec('What did the model assign to this actual token?', 'Exponentiate its raw logprob. Sum only the reported alternatives; their top-N list may omit probability mass.', 'Visible token index (zero-based)', 0, 5, 0, 10000, True),
    'speculation': _spec('Why can a draft be rejected?', 'Compare the proposal head and target verification on the same proposed token. They are different distributions.', 'Proposal position (zero-based)', 0, 2, 0, 10000, True),
    'performance': _spec('What did each API path cost on this setup?', 'Recalculate a latency percentile from the original wall-time samples. Different output tasks remain separate.', 'Latency percentile', 50, 90, 0, 100),
    'samplers': _spec('How much did this recipe change the selected token’s weight?', 'Compare its raw target probability with its post-sampler probability. Read support and entropy from the complete native row.', 'Recorded recipe index (zero-based)', 0, 1, 0, 10000, True),
    'sampler-sandbox': _spec('Can we add heat without admitting implausible tokens?', 'Remove logits below max + log(0.05), then divide the survivors by temperature and normalize.', 'Temperature after Min-P', 1.5, .7, .1, 3),
    'tictactoe': _spec('Did a legal move give away a winnable outcome?', 'Solve the saved position by exhaustive minimax. Compare the best legal outcome with the recorded model move.', 'Recorded turn index (zero-based)', 0, 1, 0, 10000, True),
    'chess': _spec('Did the shortlist favor a mating move?', 'Add the saved label weights attached to code-checked mating moves. The separately generated UCI move uses a different prompt.', 'Shortlist temperature', 1, 3, .1, 3),
    'poker': _spec('Should this hand check or bet?', 'Average exact chip payoffs over the two possible opponent cards using the stated calling policy.', 'Opponent call-rate multiplier', 1, 0, 0, 2),
    'thermal': _spec('What happens if we replay the fan commands differently?', 'Step the disclosed thermal equation through the same loads. A fan offset is an open-loop counterfactual, not a new model policy.', 'Fan offset', 0, 20, -60, 60),
    'scheduler': _spec('How much lateness did this legal schedule cause?', 'Add job durations in the recorded order and check dependencies. Charge for finishing after the adjusted deadline.', 'Deadline shift', 0, -3, -10, 10),
    'context': _spec('Did replacing old text change the current-state answer?', 'Recalculate each saved Yes/No distribution and compare the selected wording with the original append-only prompt.', 'Context variant index (zero-based)', 0, 2, 0, 10000, True),
    'observer': _spec('Which action follows from these three semantic measurements?', 'Apply the same explicit threshold rule to every saved report: inspect, verify, finish, or ask.', 'Decision threshold', .5, .999, 0, 1),
    'calibration': _spec('Does demanding stronger answers leave enough coverage?', 'Recalculate Brier error on all six examples and accuracy only on retained examples. Empty coverage has no accuracy.', 'Required answer weight', .5, 1, .5, 1),
    'information': _spec('Which observation is worth buying?', 'Use the stated sensor likelihoods to compute both Bayesian posteriors and expected entropy reduction.', 'Test index (zero-based)', 0, 1, 0, 10000, True),
    'search': _spec('Which valid scene survives a cost penalty?', 'Subtract the chosen cost charge from each saved semantic weight. Reject invalid geometry before ranking.', 'Cost weight', .1, 1, 0, 1),
    'frontier': _spec('Would faster score transfer matter here?', 'Add assumed forward time, a transfer lower bound, and the measured selector. This is a serial cost sketch.', 'Assumed transfer GB/s', 12, 2, .1, 128),
    'research-map': _spec('What would make this research idea testable?', 'Count the disclosed implementation categories, then reveal one branch’s next gate. A proposal is not a native result.', 'Branch index (zero-based)', 0, 12, 0, 10000, True),
    'pressure': _spec('How much original mass did this boundary throw away?', 'At temperature 1 with pure masking, log Z = raw selected logprob − log(selected masked probability). Pressure is −log Z.', 'Native grammar index (zero-based)', 0, 1, 0, 10000, True),
    'circuit': _spec('Can we compute AND without assuming independence?', 'Start with four joint worlds. Optionally condition on noisy evidence of style, then add worlds for each logical operation.', 'Reliability of observing style', .5, 1, .5, 1),
    'control': _spec('Can preference change while forbidden actions stay forbidden?', 'Normalize log(base) + strength × [log(desired) − log(undesired)] inside the legal set.', 'Control strength', 0, 2, 0, 3),
    'future': _spec('Can a less likely first move have a better future?', 'Weight the root policy by exact future success raised to strength. At strength zero use the base policy.', 'Future-value strength', 0, 1, 0, 2),
    'sensitivity': _spec('Which prompt intervention moves this measurement?', 'Rebuild the central finite-difference matrix. Predict a change in hours, with load fixed at +5 points; preserve the measured holdout error.', 'Change in hours remaining', -1, -2, -2, 2),
    'counterexamples': _spec('Can equivalent algebra confuse the observer?', 'Find the equivalent pair with the largest measured log-odds distance. Evaluate its exact coefficients at the chosen integer.', 'Integer x', 2, -2, -10, 10, True),
}


def normalize_logs(logs):
    finite = [x for x in logs if math.isfinite(x)]
    if not finite:
        raise ValueError('No candidate has positive mass')
    maximum = max(finite)
    weights = [math.exp(x-maximum) if math.isfinite(x) else 0. for x in logs]
    total = math.fsum(weights)
    return [w/total for w in weights]


def weights(rows, temperature=1):
    if any(r.get('logprob') is None for r in rows):
        raise ValueError('A complete label measurement is required; missing top-N entries stay unknown')
    return normalize_logs([r['logprob']/temperature for r in rows])


def entropy(p):
    return -math.fsum(x*math.log2(x) for x in p if x)


def _pick(items, value):
    if not 0 <= value < len(items):
        raise ValueError('Index must be 0..'+str(len(items)-1))
    return items[int(value)]


def _rows(names, values):
    return [dict(label=str(n), value=float(v)) for n,v in zip(names,values)]


def _graph(edges, threshold):
    if len(edges)>12:
        raise ValueError('This exact demonstration supports at most 12 edges')
    best, score = [], 0.
    for bits in itertools.product((False,True), repeat=len(edges)):
        selected=[e for e,yes in zip(edges,bits) if yes]
        out, incoming, captions = {}, set(), set()
        good=True
        for e in selected:
            a,b=e['source'],e['target']
            if a==b:good=False;break
            if e['relation']=='caption':
                if a in captions:good=False;break
                captions.add(a)
            else:
                if a in out or b in incoming:good=False;break
                out[a]=b;incoming.add(b)
        for start in out:
            node,visited=start,set()
            while node in out:
                if node in visited:good=False;break
                visited.add(node);node=out[node]
        utility=math.fsum(e['weight']-threshold for e in selected)
        if good and utility>score:best,score=selected,utility
    return best,score


def _ttt(board, turn):
    lines=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
    for a,b,c in lines:
        if board[a]!='.' and board[a]==board[b]==board[c]:return 1 if board[a]=='X' else -1
    if '.' not in board:return 0
    values=[_ttt(board[:i]+turn+board[i+1:],'O' if turn=='X' else 'X') for i,s in enumerate(board) if s=='.']
    return (max if turn=='X' else min)(values)


def calculate_lesson(name, data, value=None):
    spec=LESSON_SPECS[name]
    v=spec['default'] if value is None else value
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not spec['low']<=v<=spec['high'] or (spec['integer'] and int(v)!=v):
        raise ValueError(f"{spec['knob']} must be {'an integer' if spec['integer'] else 'finite'} in [{spec['low']}, {spec['high']}]")
    rows=[];metrics={};note='Calculation on saved inputs; changing this setting makes no new model request.'
    summary='';unit='weight'
    if name in ('choice','boolean','score'):
        p=weights(data['rows'],v);at=max(range(len(p)),key=p.__getitem__)
        rows=_rows([r['label']+' · '+r.get('description','') for r in data['rows']],p)
        metrics=dict(winner=data['rows'][at]['label'],top_weight=p[at],entropy_bits=entropy(p))
        if name in ('boolean','score'):
            metrics['expected_value']=math.fsum(q*r['value'] for q,r in zip(p,data['rows']))
        summary=f"Answer {metrics['winner']} leads with {p[at]:.2%} of the listed-label weight."
        if name=='score':summary=f"Expected rubric value: {metrics['expected_value']:.4f} on the stated 0–1 scale."
    elif name=='candidates':
        paths=data['paths'];logs=[math.fsum(t['logprob'] for t in r['tokens'])/len(r['tokens'])**v for r in paths]
        p=normalize_logs(logs);names=list(dict.fromkeys(r['group'] for r in paths))
        values=[math.fsum(q for q,r in zip(p,paths) if r['group']==g) for g in names];rows=_rows(names,values)
        metrics=dict(winner=names[values.index(max(values))],group_weights=values)
        summary=metrics['winner']+' carries the most relative group weight.'
        note='Only these emitted token paths, with their saved terminators and no EOS. A nonzero length penalty produces preference scores, not path probability.'
    elif name=='controller':
        labels=data['measure']['rows'];p=weights(labels);legal=[i for i,r in enumerate(labels) if r['allowed']]
        mass=math.fsum(p[i] for i in legal);pick=next(i for i,r in enumerate(labels) if r['action']==data['action'])
        q=p[pick]/mass;held=q<v
        rows=_rows([labels[i]['action'] for i in legal],[p[i]/mass for i in legal])
        metrics=dict(held=held,selected_weight=q,next_state=data['state'] if held else data['next_state'])
        summary=('Hold the action.' if held else 'Apply '+data['action']+'.')+' State: '+metrics['next_state']+'.'
    elif name=='rerank':
        values=[math.fsum(q*r['value'] for q,r in zip(weights(s['measure']['rows']),s['measure']['rows'])) for s in data['sources']]
        rows=_rows([s['id'] for s in data['sources']],values);kept=[r['label'] for r in rows if r['value']>=v]
        metrics=dict(retained=kept,scores=values);summary='Retain '+(', '.join(kept) or 'no sources')+' at this cutoff.'
    elif name=='graph':
        selected,utility=_graph(data['edges'],v);rows=_rows([e['source']+' → '+e['target'] for e in selected],[e['weight']-v for e in selected]);unit='utility'
        metrics=dict(selected=[(e['source'],e['target'],e['relation']) for e in selected],utility=utility)
        summary=f'{len(selected)} compatible links, total utility {utility:.4f}.'
        note='Global code constraints select links; utility is not the probability that the document graph is correct.'
    elif name=='scene':
        valid=[c for c in data['candidates'] if c['valid']];values=[]
        for c in valid:
            p=[weights(x['measure']['rows'])[0] for x in c['vector']]
            values.append(statistics.mean(p)-v*statistics.pvariance(p))
        rows=_rows([c['name'] for c in valid],values);unit='utility';metrics=dict(retained=valid[values.index(max(values))]['name'],utilities=values)
        summary='Retain '+metrics['retained']+' among geometry-valid candidates.'
        note='These are saved text judgments. This calculation cannot see the drawing or measure visual appeal.'
    elif name=='wire':
        entry=_pick(data['entries'],v);p=math.exp(entry['logprob']);top=entry.get('top_logprobs',[])
        rows=_rows([x['token'] for x in top],[math.exp(x['logprob']) for x in top]);unit='raw probability'
        metrics=dict(token=entry['token'],raw_probability=p,reported_top_mass=math.fsum(r['value'] for r in rows))
        summary=f"Token {entry['token']!r}: raw probability {p:.6g}."
        note='This is one visible content token at its actual prefix. Reported top-N mass is not the whole vocabulary.'
    elif name=='speculation':
        window=data['oracle']['example_rejection'];r=_pick(window['proposal'],v)
        rows=_rows(['Draft head','Target verification'],[r['draft_probability'],math.exp(r['target_logprob'])]);unit='probability / distinct heads'
        metrics=dict(token_id=r['token_id'],target_sequence_logprob=math.fsum(x['target_logprob'] for x in window['proposal']),draft_target_logprob_gap=r['draft_logprob']-r['target_logprob'])
        summary=f"Proposal token {r['token_id']}: the two heads differ by {metrics['draft_target_logprob_gap']:.4f} log units."
        note='Draft vocabulary and target vocabulary can differ. The gap is a diagnostic, not a calibrated rejection probability.'
    elif name=='performance':
        values=[]
        for r in data['rows']:
            xs=sorted(x['wall_ms'] for x in r['runs']);a=(len(xs)-1)*v/100;lo=math.floor(a);hi=math.ceil(a)
            values.append(xs[lo]+(xs[hi]-xs[lo])*(a-lo))
        rows=_rows([r['name'] for r in data['rows']],values);unit='ms';metrics=dict(percentile=v,times_ms=values)
        summary=f'Percentile {v:g}, recalculated from {data["repeats"]} samples per path.'
        note='Small same-setup samples include network and API cost. JSON answers a different task; this is no universal speed ranking.'
    elif name=='samplers':
        run=_pick(data['runs'],v);token=run['tokens'][0];sample=token['strata_sampling']
        raw=math.exp(token['logprob']);post=sample['probability']
        rows=_rows(['Raw target','After recipe'],[raw,post]);unit='selected token probability'
        metrics=dict(recipe=run['name'],support=sample['support'],raw=raw,selected=post,log_weight_change=math.log(post)-token['logprob'],entropy_bits=sample['entropy']/math.log(2))
        summary=f"{run['name']}: {sample['support']} native tokens remain eligible."
        note='Recipes are separate generations. Entropy and support are full-row native measurements; a top-N slice cannot recover them.'
    elif name=='sampler-sandbox':
        cut=max(data['logits'])+math.log(.05);logs=[x/v if x>=cut else -math.inf for x in data['logits']];p=normalize_logs(logs)
        rows=_rows(data['tokens'],p);metrics=dict(support=sum(x>0 for x in p),entropy_bits=entropy(p),probabilities=p)
        summary=f"{metrics['support']} credible tokens survive; entropy {metrics['entropy_bits']:.3f} bits."
        note='All eight logits are synthetic and visible. This is exact finite-row arithmetic, not a new native receipt.'
    elif name=='tictactoe':
        f=_pick(data['frames'],v);b=f['before'];legal=[i for i,c in enumerate(b) if c=='.'];oracle={i:_ttt(b[:i]+'X'+b[i+1:],'O') for i in legal}
        regret=max(oracle.values())-oracle[f['square']];rows=_rows([str(i+1) for i in legal],list(oracle.values()));unit='X outcome: lose −1 / draw 0 / win 1'
        metrics=dict(regret=regret,square=f['square']+1,oracle=oracle);summary=f"Recorded move: square {f['square']+1}; exact outcome regret {regret}."
    elif name=='chess':
        p=weights(data['measure']['rows'],v);mass=math.fsum(q for q,m in zip(p,data['shortlist']) if m['mate'])
        rows=_rows([m['san'] for m in data['shortlist']],p);metrics=dict(mating_shortlist_weight=mass,generated_uci=data['chosen']['text'],generated_mate=data['mate'])
        summary=f'{mass:.2%} of shortlist weight favors mate; the separate UCI generation '+('mated.' if data['mate'] else 'did not mate.')
        note='The saved legal/mate flags came from python-chess. This portable calculation aggregates them; it is not a replacement chess engine.'
    elif name=='poker':
        ranks=['J','Q','K'];rates={c:min(1,max(0,r*v)) for c,r in data['call_rates'].items()};values={}
        for own in ranks:
            opponents=[c for c in ranks if c!=own];sign=lambda c:1 if ranks.index(own)>ranks.index(c) else -1
            values[own]=dict(check=statistics.mean(sign(c) for c in opponents),bet=statistics.mean((1-rates[c])+rates[c]*2*sign(c) for c in opponents))
        rows=_rows([c+' bet − check' for c in ranks],[values[c]['bet']-values[c]['check'] for c in ranks]);unit='expected chips'
        metrics=dict(values=values,call_rates=rates);summary='Bet when the bar is positive; check when it is negative.'
        note='Uniform remaining-card prior and explicitly assumed opponent policy. Answer weights are not hidden-card beliefs or equilibrium probabilities.'
    elif name=='thermal':
        t=data['frames'][0]['temperature'];temperatures=[]
        for f in data['frames']:
            fan=min(60,max(0,f['fan']+v));t=round(t+.22*f['load']-.32*fan-.04*(t-25),3);temperatures.append(t)
        rows=_rows(range(1,len(temperatures)+1),temperatures);unit='°C';metrics=dict(temperatures=temperatures,mean_error=statistics.mean(abs(t-data['target']) for t in temperatures),violations=sum(t>data['limit'] for t in temperatures))
        summary=f"Mean distance from target: {metrics['mean_error']:.2f}°C; {metrics['violations']} limit violations."
        note='Offset fans are clamped to 0–60; the toy rounds to 0.001°C each step. This replays saved actions without rerunning the shield or model; it may violate the limit. No physical control.'
    elif name=='scheduler':
        done=set();clock=0;late=[]
        for f in data['frames']:
            j=f['job']
            if not set(j['after'])<=done:raise ValueError('Saved schedule violates dependencies')
            clock+=j['duration'];late.append(max(0,clock-j['deadline']-v));done.add(j['id'])
        rows=_rows([f['job']['id'] for f in data['frames']],late);unit='late time units';metrics=dict(total_lateness=sum(late),finish_time=clock)
        summary=f'Total lateness {sum(late):g}; the same dependency-valid order ends at time {clock}.'
    elif name=='context':
        selected=_pick(data['runs'],v);all_weights=[weights(r['measure']['rows'])[1] for r in data['runs']];p=all_weights[int(v)]
        rows=_rows([r['name'] for r in data['runs']],all_weights);metrics=dict(variant=selected['name'],no_weight=p,delta_from_append=p-all_weights[0])
        summary=f"{selected['name']}: keep-still answer weight {p:.3%}."
        note='Saved prompt interventions, not KV tensor mutation. This calculation compares their recorded measurements.'
    elif name=='observer':
        actions=[];triples=[]
        for f in data['frames']:
            p=[weights(x['measure']['rows'])[0] for x in f['vector']];triples.append(p)
            actions.append('inspect failure' if p[0]>v else 'verify' if p[1]>v else 'finish' if p[2]>v else 'ask')
        rows=_rows(['Fault','Missing check','Verified'],triples[0]);metrics=dict(actions=actions,vectors=triples)
        summary=' → '.join(actions)+'.';note='Bars show the first report. The same rule processes all three; correlated probes do not multiply into workflow reliability.'
    elif name=='calibration':
        p=[weights(r['measure']['rows'])[0] for r in data['rows']];truth=[r['truth'] for r in data['rows']];kept=[i for i,q in enumerate(p) if max(q,1-q)>=v]
        brier=statistics.mean((q-y)**2 for q,y in zip(p,truth));accuracy=statistics.mean(int(p[i]>=.5)==truth[i] for i in kept) if kept else None
        rows=_rows([str(i+1) for i in range(len(p))],p);metrics=dict(brier=brier,retained=len(kept),coverage=len(kept)/len(p),accuracy=accuracy)
        summary=f'{len(kept)}/{len(p)} retained; '+(f'{accuracy:.1%} correct in those cases.' if accuracy is not None else 'accuracy is undefined with zero coverage.')
        note='Six disclosed teaching examples, not a held-out calibration benchmark. Brier error still counts every example.'
    elif name=='information':
        t=_pick(data['tests'],v);prior=data['prior'];py=math.fsum(p*l for p,l in zip(prior,t['likelihood']));yes=[p*l/py for p,l in zip(prior,t['likelihood'])];no=[p*(1-l)/(1-py) for p,l in zip(prior,t['likelihood'])]
        gain=entropy(prior)-py*entropy(yes)-(1-py)*entropy(no);rows=_rows(data['faults'],yes)
        metrics=dict(test=t['name'],gain_bits=gain,gain_per_cost=gain/t['cost'],yes=yes,no=no)
        summary=t['name']+f': {gain:.3f} expected bits; {gain/t["cost"]:.3f} bits per cost unit.'
        note='Prior and likelihoods are stated synthetic sensor assumptions. Bars condition on a positive result; no test was actually purchased.'
    elif name=='search':
        valid=[c for c in data['candidates'] if c['valid']];values=[weights(c['measure']['rows'])[0]-v*c['cost']/3 for c in valid]
        rows=_rows([c['id'] for c in valid],values);unit='utility';metrics=dict(retained=valid[values.index(max(values))]['id'],utilities=values)
        summary='Retain '+metrics['retained']+' after charging for cost; invalid geometry is excluded.'
    elif name=='frontier':
        selector=sorted(r['selection_ms'] for r in data['measurements'])[len(data['measurements'])//2];transfer=data['vocabulary']*data['bytes_per_logit']/(v*1e6);total=60+transfer+selector
        rows=_rows(['Assumed forward','Transfer lower bound','Measured host selector'],[60,transfer,selector]);unit='ms'
        metrics=dict(transfer_ms=transfer,serial_ms=total,tokens_per_second=1000/total)
        summary=f'Serial estimate: {total:.3f} ms/token; {1000/total:.2f} tokens/s.'
        note='Forward time is assumed 60 ms. Selector uses the upper-middle measured sample to match the chart. Queue, prefill and network are excluded.'
    elif name=='research-map':
        branch=_pick(data['branches'],v);categories={}
        for b in data['branches']:categories[b['status']]=categories.get(b['status'],0)+1
        rows=_rows(list(categories),list(categories.values()));unit='branches';metrics=dict(branch=branch['name'],gate=branch['gate'],categories=categories)
        summary=branch['name']+': '+branch['gate'];note='This page recomputes an agenda inventory, not an experiment result. Each implemented branch links to its own evidence.'
    elif name=='pressure':
        case=_pick(data['cases'],v);r=case['rows'][0];token=r['token'];q=token['strata_sampling']['probability'];logz=token['logprob']-math.log(q)
        if logz>1e-6:raise ValueError('Pure-mask mass exceeds one')
        z=math.exp(min(0,logz));rows=_rows(['Survived','Removed'],[z,1-z]);unit='original probability mass'
        metrics=dict(grammar=case['name'],mass=z,pressure_nats=-logz,pressure_bits=-logz/math.log(2))
        summary=f"{case['name']}: {z:.4%} survives; pressure {-logz:.4f} nats."
        note='First actual prefix of this native grammar. Exact only for pure masking at temperature 1, not arbitrary sampler recipes or entire grammar languages.'
    elif name=='circuit':
        p=weights(data['cases'][0]['measurement']['rows']);weighted=[p[0]*(1-v),p[1]*(1-v),p[2]*v,p[3]*v];z=math.fsum(weighted);p=[x/z for x in weighted]
        f=p[1]+p[3];s=p[2]+p[3];rows=_rows(['Neither','Facts only','Style only','Both'],p)
        metrics=dict(F=f,S=s,AND=p[3],OR=1-p[0],F_given_S=p[3]/s if s else None,marginal_product=f*s)
        summary=f'Facts AND style: {p[3]:.2%}; multiplying the marginals would give {f*s:.2%}.'
        note='At reliability 0.5 the evidence is uninformative and leaves the native row unchanged. Logical arithmetic is exact relative to that row, not necessarily the world.'
    elif name=='control':
        logs=[math.log(b)+v*(math.log(d)-math.log(u)) if i in data['allowed'] else -math.inf for i,(b,d,u) in enumerate(zip(data['base'],data['desired'],data['undesired']))];p=normalize_logs(logs)
        rows=_rows(list('ABCD'),p);pick=max(range(len(p)),key=p.__getitem__);metrics=dict(probabilities=p,selected=pick,forbidden_mass=math.fsum(p[i] for i in range(len(p)) if i not in data['allowed']))
        summary=f"Action {'ABCD'[pick]} leads; forbidden-action mass stays zero."
        note='Finite-action arithmetic using separately prompted rows of the same model. It is not trained-expert decoding or a native full-vocabulary hook.'
    elif name=='future':
        root=weights(data['policy'][0]['rows']);child=weights(data['policy'][2]['rows']);h=[0,child[1]];p=normalize_logs([math.log(r)+(v*math.log(x) if x else -math.inf) if v else math.log(r) for r,x in zip(root,h)])
        rows=_rows(['A: dead end','B: viable route'],p);success=p[1]*child[1];metrics=dict(root_weights=p,exact_h=h,success_root_only=success,base_success=root[1]*child[1])
        summary=f'{p[1]:.2%} chooses B; leaving the next policy unchanged succeeds {success:.2%} of the time.'
        note='Only BB succeeds in this exact two-step toy. Conditioning both steps is different from steering only the root. No native future-value decoder is claimed.'
    elif name=='sensitivity':
        o=data['observations'];zs=[[math.log(p/(1-p)) for p in row['probabilities']] for row in o]
        matrix=[[(zs[2][i]-zs[1][i])/(2*data['epsilon'][0]),(zs[4][i]-zs[3][i])/(2*data['epsilon'][1])] for i in range(3)]
        delta=[r[0]*v+r[1]*5 for r in matrix];rows=_rows(['Urgency','Load','Damage'],delta);unit='predicted log-odds change'
        observed=[zs[6][i]-zs[0][i] for i in range(3)];held=[r[0]*-1+r[1]*5 for r in matrix]
        metrics=dict(matrix=matrix,predicted_delta=delta,holdout_residual=[a-b for a,b in zip(observed,held)])
        summary=f'Predicted urgency shift {delta[0]:+.3f}; the measured −1h/+5 holdout had error {metrics["holdout_residual"][0]:+.3f}.'
        note='The local linear approximation failed on the measured holdout. Other knob settings are predictions, not newly measured prompt responses.'
    elif name=='counterexamples':
        nodes=data['nodes'];pairs=[]
        for i,a in enumerate(nodes):
            za=[math.log(p/(1-p)) for p in a['p_yes']]
            for j,b in enumerate(nodes[i+1:],i+1):
                if a['coefficients']!=b['coefficients']:continue
                zb=[math.log(p/(1-p)) for p in b['p_yes']];distance=math.sqrt(math.fsum((x-y)**2 for x,y in zip(za,zb)));pairs.append((distance,i,j))
        distance,i,j=max(pairs);a,b=nodes[i],nodes[j];evaluate=lambda c:sum(x*v**k for k,x in enumerate(c))
        rows=_rows([a['expression'],b['expression']],[a['p_yes'][1],b['p_yes'][1]])
        metrics=dict(left=a['expression'],right=b['expression'],margin_distance=distance,left_value=evaluate(a['coefficients']),right_value=evaluate(b['coefficients']))
        summary=f'Equal exact values at x={v:g}: {metrics["left_value"]:g}; observer distance {distance:.3f}.'
        note='Matching canonical coefficients prove equivalence for all integers. Evaluating one x illustrates that proof; it does not establish it. Bars show the nonnegativity probe.'
    else:
        raise ValueError('No portable calculation for '+name)
    return dict(value=v,summary=summary,rows=rows,unit=unit,metrics=metrics,note=note)


def make_lesson(name, data):
    spec=LESSON_SPECS[name]
    try:
        first=calculate_lesson(name,data)
        compare=spec['compare']
        # An edited run can have fewer tokens/turns than the recorded default.
        lengths={'wire':len(data.get('entries',[])), 'samplers':len(data.get('runs',[])),
                 'tictactoe':len(data.get('frames',[])), 'context':len(data.get('runs',[])),
                 'information':len(data.get('tests',[])), 'research-map':len(data.get('branches',[])),
                 'pressure':len(data.get('cases',[]))}
        if name in lengths:compare=min(compare,lengths[name]-1)
        second=calculate_lesson(name,data,compare)
        context=data.get('prompt','').partition('STATE:\n')[2].partition('\nQUESTION:')[0]
        return dict(**spec,states=[first,second],input_excerpt=context[:320]+('…' if len(context)>320 else ''),scope='This panel and its Python calculation reproduce saved measurements. Other page controls are independent views.')
    except (ValueError,KeyError,IndexError,ZeroDivisionError) as error:
        # A genuinely incomplete score or a tool-only wire response stays usable.
        # Do not turn an unavailable lesson into fabricated measurement data.
        return dict(**spec,states=[],unavailable=str(error),scope='This run has no complete inputs for this calculation. Inspect its exact request and result below.')
