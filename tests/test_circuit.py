import pytest
from control_lab.instrument_page_circuit import joint_ops,coherence

def test_joint_example_and_undefined_conditioning():
    result=joint_ops([.1,.1,.2,.6])
    for key,value in dict(F=.7,S=.8,AND=.6,OR=.9,F_given_S=.75,marginal_product=.56).items():
        assert result[key]==pytest.approx(value)
    assert joint_ops([.5,.5,0,0])['F_given_S'] is None
    with pytest.raises(ValueError):joint_ops([1,1,1,1])

def test_every_small_joint_satisfies_frechet_without_independence():
    for a in range(11):
        for b in range(11-a):
            for c in range(11-a-b):
                d=10-a-b-c;result=joint_ops([v/10 for v in (a,b,c,d)])
                assert coherence(result['F'],result['S'],result['AND'])['violation']<1e-14
    assert coherence(.9,.9,.1)['violation']==pytest.approx(.7)
