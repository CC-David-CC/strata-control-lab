import math
import pytest
from control_lab.instrument_math import pressure_from_token,contrast,finite_row,pure_request

PROFILE={'chain':['temperature'],'temperature':1.0,'inspect':True}

def token(p,q,support=2):
    return dict(logprob=math.log(p),strata_sampling=dict(probability=q,support=support,
      stages=[dict(operator='grammar',support=support),dict(operator='temperature',support=support)]))

def test_pressure_distinguishes_same_answer_distribution():
    for p,z in [(.594,.99),(.006,.01)]:
        result=pressure_from_token(token(p,.6),PROFILE)
        assert result['mass']==pytest.approx(z)
        direct=.6*math.log(.6/p)+.4*math.log(.4/(z*.4))
        assert result['pressure_nats']==pytest.approx(direct)

def test_log_mass_survives_probability_underflow():
    t=token(.1,.5);t['logprob']=-1000
    result=pressure_from_token(t,PROFILE)
    assert result['mass']==0 and result['pressure_nats']==pytest.approx(1000-math.log(2))

@pytest.mark.parametrize('profile',[{**PROFILE,'temperature':2},dict(chain=['min_p','temperature'],min_p=.05,temperature=1,inspect=True)])
def test_pressure_refuses_modified_distribution(profile):
    with pytest.raises(ValueError,match='pure masking'):pressure_from_token(token(.1,.5),profile)

def test_contrast_zero_strength_and_hard_permission():
    b=[.2,.5,.3];e=[.7,.2,.1];a=[.1,.2,.7]
    assert contrast(b,e,a,0,[0,2])==pytest.approx([.4,0,.6])
    q=contrast(b,e,a,100,[0,2]);assert q[1]==0 and sum(q)==pytest.approx(1)
    with pytest.raises(ValueError):contrast(b,e,a,1,[])

def test_single_row_rejects_partial_token_support():
    entry={**token(.2,.5), 'token':'A','bytes':[65]}
    entry['strata_sampling']['top']=[dict(id=1,bytes=[65],probability=.5)]
    response={'choices':[{'message':{'content':'A'},'finish_reason':'length','logprobs':{'content':[entry]}}]}
    with pytest.raises(ValueError,match='exactly one native token'):
        finite_row(response,pure_request('q',['A','B']),[dict(label='A'),dict(label='B')])
