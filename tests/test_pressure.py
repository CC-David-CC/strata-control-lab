from control_lab.paths import DATA
import math,random,json
from pathlib import Path
import pytest
from control_lab.instrument_math import pressure_from_token

def test_mask_pressure_is_kl_for_random_full_distributions():
    rng=random.Random(675)
    profile={'chain':['temperature'],'temperature':1.0,'inspect':True}
    for _ in range(100):
        p=[rng.random() for i in range(20)];p=[x/sum(p) for x in p]
        allowed=rng.sample(range(20),rng.randint(1,19));z=sum(p[i] for i in allowed)
        q={i:p[i]/z for i in allowed};direct=sum(q[i]*math.log(q[i]/p[i]) for i in allowed)
        for i in allowed:
            token=dict(logprob=math.log(p[i]),strata_sampling=dict(probability=q[i],support=len(allowed),stages=[dict(operator=n,support=len(allowed)) for n in ['grammar','temperature']]))
            assert pressure_from_token(token,profile)['pressure_nats']==pytest.approx(direct,abs=1e-12)

def test_native_pressure_is_consistent_with_any_visible_raw_alternative():
    root=DATA/'captures/pressure.json'
    data=json.loads(root.read_text(encoding='utf-8'));checked=0
    for case in data['result']['cases']:
        for row in case['rows']:
            assert 0<=row['mass']<=1 and row['pressure_nats']>=0
            token=row['token'];raw={tuple(t['bytes']):t['logprob'] for t in token['top_logprobs'] if t['bytes'] is not None}
            for q in token['strata_sampling']['top']:
                if tuple(q['bytes']) in raw and q['probability']>0:
                    assert raw[tuple(q['bytes'])]-math.log(q['probability'])==pytest.approx(row['log_mass'],abs=1e-7)
                    checked+=1
    assert checked>=2
