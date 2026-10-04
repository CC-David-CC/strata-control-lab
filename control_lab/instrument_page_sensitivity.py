from .instrument_math import page,yes_no,weights,margin

PAGE=page('sensitivity','Semantic sensitivity','Find the direction that moves meaning.',
    'Change one thing at a time. Measure how far each semantic signal moves, including the ones you meant to leave alone.',
    'Log-odds vectors are measured from native yes/no rows. Central finite differences use hours and percentage points as explicit units. A discrete wording edit stays a difference vector. A combined held-out intervention checks the limits of a local linear prediction.',
    ['log-odds','response matrix','controlled perturbations'],
    'Repeat across templates, epsilon scales, label permutations and held-out states before fitting a controller or interpreting a stable direction.')

QUESTIONS=['Is the parcel urgent under the stated numeric deadline rule?',
           'Is the machine highly loaded under the stated numeric load rule?',
           'Does the parcel require manual review under the stated damage rule?']

def central(plus,minus,epsilon):
    if epsilon<=0 or len(plus)!=len(minus):raise ValueError('A positive coordinate step and matching observations are required')
    return [(a-b)/(2*epsilon) for a,b in zip(plus,minus)]

async def run(ctx,opt):
    cases=[('baseline',6,50,''),('hours minus',4,50,''),('hours plus',8,50,''),
           ('load minus',6,40,''),('load plus',6,60,''),
           ('discrete label',6,50,'The printed parcel label says URGENT.'),
           ('held-out combined',5,55,'')]
    observations=[]
    for name,hours,load,extra in cases:
        state=(f'Parcel hours_remaining={hours}. Machine load_percent={load}. damage_report=false. '
               'Definitions: urgent means hours_remaining <= 4; highly loaded means load_percent >= 60; '
               'manual review means damage_report is true. '+extra)
        probes=[await yes_no(ctx,state,q,name+' / '+str(i+1)) for i,q in enumerate(QUESTIONS)]
        observations.append(dict(name=name,hours=hours,load=load,state=state,probes=probes,
            probabilities=[weights(row)[0] for row in probes],z=[margin(row) for row in probes]))
    columns=[central(observations[2]['z'],observations[1]['z'],2),central(observations[4]['z'],observations[3]['z'],10)]
    matrix=[list(x) for x in zip(*columns)];baseline=observations[0]['z'];du=[-1,5]
    predicted=[sum(row[j]*du[j] for j in range(2)) for row in matrix]
    observed=[a-b for a,b in zip(observations[6]['z'],baseline)]
    return dict(observations=observations,questions=QUESTIONS,matrix=matrix,
                coordinates=['hours remaining','load percentage points'],epsilon=[2,10],
                holdout=dict(intervention=du,predicted_delta=predicted,observed_delta=observed,residual=[a-b for a,b in zip(observed,predicted)]),
                discrete_delta=[a-b for a,b in zip(observations[5]['z'],baseline)],
                semantics='These are finite differences of native prompt measurements, not backpropagation or physical causal derivatives. The three probes may share errors. The local controller preview uses the estimated matrix and makes no new inference call.')
