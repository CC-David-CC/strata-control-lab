import math
from .instrument_math import page,measure,yes_no,weights

PAGE=page('circuit','Probability circuit','Compute with meanings, not guesses.',
    'Keep four possible worlds alive. Add their weights to ask AND, OR and IF without inventing independence.',
    'A joint four-code native measurement gives marginals, conjunction, disjunction and conditional probabilities by arithmetic. Separate yes/no prompts are also checked against Frechet bounds. Consistency does not establish factual accuracy.',
    ['joint meanings','probabilistic logic','consistency'],
    'Use overlapping factors with an explicit consistency solver; evaluate prompt stability and calibration on held-out labelled edits.')

def joint_ops(p):
    if len(p)!=4 or any(not math.isfinite(x) or x<0 for x in p) or not math.isclose(sum(p),1.,abs_tol=1e-9):
        raise ValueError('Four probabilities summing to one are required')
    f=p[1]+p[3];s=p[2]+p[3]
    return dict(F=f,S=s,AND=p[3],OR=1-p[0],F_given_S=p[3]/s if s else None,
                marginal_product=f*s,dependence=p[3]-f*s)

def coherence(f,s,both):
    if any(not 0<=x<=1 for x in (f,s,both)):raise ValueError('Probabilities must lie in [0,1]')
    lo=max(0.,f+s-1);hi=min(f,s)
    return dict(lower=lo,upper=hi,violation=max(lo-both,both-hi,0.))

async def run(ctx,opt):
    original='Parcel 17 weighs 4 kg.'
    edits=['Please note that parcel 17 weighs 4 kg.','Parcel 17 weighs 4 kg.',
           'Please note that parcel 17 weighs 40 kg.','PARCEL 17 IS 40 KG.']
    rows=[]
    for edited in edits:
        state=f'ORIGINAL: {original}\nEDIT: {edited}\nF: parcel number and weight are preserved. S: the edit explicitly uses the polite word please.'
        measurement=await measure(ctx,state,'Which joint state describes the edit?',
            ['Neither F nor S','F only: facts preserved, no requested style','S only: style changed, facts changed','Both F and S'],'Measure four joint semantic states')
        rows.append(dict(original=original,edited=edited,measurement=measurement,operations=joint_ops(weights(measurement))))
    state=f'ORIGINAL: {original}\nEDIT: {edits[0]}'
    separate=[]
    for question in ['Are the original parcel number and weight preserved?',
                     'Does the edit explicitly use the polite word please?',
                     'Are the original parcel number and weight preserved AND is the polite word please used?']:
        separate.append(await yes_no(ctx,state,question,'Independent-prompt consistency probe'))
    values=[weights(row)[0] for row in separate]
    return dict(cases=rows,separate=dict(values=values,measurements=separate,**coherence(*values)),
                hypothetical=dict(joint=[.1,.1,.2,.6],inconsistent=[.9,.9,.1]),
                semantics='Arithmetic is exact relative to each supplied distribution. Different prompts need not form one coherent joint belief. A violated bound identifies an inconsistency, not which estimate is wrong.')
