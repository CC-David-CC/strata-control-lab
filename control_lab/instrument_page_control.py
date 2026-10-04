from .instrument_math import page,measure,weights,contrast,commit_label

PAGE=page('control','Semantic control knob','Add a preference. Subtract a failure mode.',
    'Turn one knob to reward a desired kind of edit and penalize an undesired one. The hard legal boundary stays in place.',
    'The lab combines three same-model, differently prompted finite action distributions. It applies log p_base + alpha (log p_desired - log p_undesired), masks prohibited actions, then selects and commits an action code through native GBNF. This is not full-vocabulary DExperts inside the engine.',
    ['logprob arithmetic','legal support','finite action decoder'],
    'Add same-token aligned vocabulary rows and a qualified native additive-score hook before claiming full decoding-time DExperts.',
    {'state':'A unit test fails because a variable name was misspelled. The surrounding module otherwise works. Choose a next editing action.'})

ACTIONS=['Change only the misspelled name and rerun the test','Rewrite and reformat the entire module',
         'Remove the failing test','Inspect more context before editing']
ALLOWED=[0,1,3]

async def run(ctx,opt):
    rows=[]
    for name,instruction in [('base','Choose a promising next action.'),
        ('desired','Strongly prefer a minimal edit that preserves unrelated structure and keeps tests.'),
        ('undesired','Controlled anti-preference experiment: prefer a broad rewrite and cosmetic changes over a minimal patch.')]:
        rows.append(await measure(ctx,opt['state'],instruction,ACTIONS,'Measure '+name+' action distribution'))
    b,e,a=[weights(r) for r in rows];commits=[]
    for alpha in [0.,1.,2.]:
        q=contrast(b,e,a,alpha,ALLOWED);pick=max(ALLOWED,key=lambda i:q[i]);label=chr(65+pick)
        emitted=await commit_label(ctx,f'Finite-action controller, alpha={alpha}. '+opt['state'],['A','B','D'],label)
        commits.append(dict(alpha=alpha,distribution=q,selected=pick,emitted=emitted))
    return dict(actions=ACTIONS,allowed=ALLOWED,measurements=rows,base=b,desired=e,undesired=a,commits=commits,
                hypothetical=dict(base=[.2,.55,.05,.2],desired=[.65,.2,.01,.14],undesired=[.05,.75,.15,.05]),
                semantics='Native rows measure preferences. The lab owns the finite-action combination and choice; native GBNF enforces its emitted code. Alpha controls in the browser recompute that arithmetic. Only the recorded alpha=0,1,2 commitments were sent to the model.')
