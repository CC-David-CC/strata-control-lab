import math
from .instrument_math import page,measure,yes_no,weights,commit_label

PAGE=page('future','Future-success lens','Prefer the path that can still succeed.',
    'A tempting next move can lead nowhere. Look through the next move to its possible endings before choosing it.',
    'An explicit two-step native action policy has four code-checked leaves. Exact rollout success h gives a conditional-policy transform; a separate prompted h is only an estimate. The lab changes finite-action selection and commits codes via GBNF, not a hidden native FUDGE implementation.',
    ['lookahead','conditional policy','semantic value estimate'],
    'Learn future-success values on held-out rollouts, specify the continuation policy, and qualify aligned per-token native score injection before extending to open text.')

def tilt(p,h,beta=1):
    if len(p)!=len(h) or not math.isfinite(beta) or beta<0 or any(not math.isfinite(v) or not 0<=v<=1 for v in [*p,*h]):
        raise ValueError('Finite nonnegative probabilities and control strength required')
    if not math.isclose(sum(p),1,abs_tol=1e-9):raise ValueError('Base probabilities must sum to one')
    scores=[a*(b**beta if beta else 1) for a,b in zip(p,h)];total=sum(scores)
    if not total:raise ValueError('No successful continuation has positive support')
    return [x/total for x in scores]

async def run(ctx,opt):
    rows=[]
    for state,actions in [
        ('Prefix empty. Route A is a short express corridor; B is a longer side corridor. This baseline policy prefers short immediate movement.', ['Take short corridor A','Take longer corridor B']),
        ('Prefix A. The corridor is a cul-de-sac. Neither remaining move reaches the destination within the one-step horizon.', ['Wait at wall','Try the locked exit']),
        ('Prefix B. There is one move left: A detours away; B enters the destination.', ['Take a short detour away','Enter the destination'])]:
        rows.append(await measure(ctx,state,'Choose the next move under this local movement policy.',actions,'Measure base policy at '+state[:12]))
    p0,pa,pb=[weights(r) for r in rows];exact=[0.,pb[1]]
    judges=[]
    for prefix,policy,outcomes in [('A',pa,[False,False]),('B',pb,[False,True])]:
        state=f'Partial route {prefix}. One step remains. Continuation policy probabilities A,B={policy}. Code-checked terminal success for A,B={outcomes}. A single random rollout will follow exactly that policy.'
        judges.append(await yes_no(ctx,state,'Predict the eventual outcome: will this random rollout reach the destination?','Measure prompted future-success proxy'))
    root_q=tilt(p0,exact);branch_q=tilt(pb,[0,1]);commits=[]
    for prefix,q in [('',root_q),('B',branch_q)]:
        pick=max(range(2),key=lambda i:q[i]);label='AB'[pick]
        commits.append(await commit_label(ctx,'Checked route controller at prefix '+repr(prefix),['A','B'],label))
    return dict(policy=rows,root=p0,after_a=pa,after_b=pb,exact_h=exact,
                prompted_h=[weights(r)[0] for r in judges],judges=judges,
                base_success=p0[1]*pb[1],root_conditioned=root_q,child_conditioned=branch_q,
                leaves=[dict(path='AA',success=False),dict(path='AB',success=False),dict(path='BA',success=False),dict(path='BB',success=True)],
                commits=commits,hypothetical=dict(base=[.8,.2],h=[.05,.9]),
                semantics='This is a finite action-prefix policy expressed in ordinary native requests. Exact h refers to the recorded continuation policy. A prompted yes/no weight is a proxy; it is not assumed harmonic, calibrated or equivalent to a trained future discriminator.')
