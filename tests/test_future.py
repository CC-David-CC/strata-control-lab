import random
import pytest
from control_lab.instrument_page_future import tilt

def test_future_example_and_empty_success_support():
    assert tilt([.8,.2],[.05,.9])==pytest.approx([2/11,9/11])
    assert tilt([.8,.2],[0,0],0)==[.8,.2]
    with pytest.raises(ValueError,match='No successful'):tilt([.8,.2],[0,0])

def test_exact_h_transform_matches_conditioning_whole_paths():
    rng=random.Random(451)
    for _ in range(200):
        r,a,b=[rng.uniform(.01,.99) for i in range(3)]
        root=[r,1-r];children=[[a,1-a],[b,1-b]]
        success=[rng.randint(0,1) for i in range(4)]
        if not any(success):success[3]=1
        h=[sum(children[j][k]*success[j*2+k] for k in range(2)) for j in range(2)]
        qroot=tilt(root,h);base_success=sum(root[j]*h[j] for j in range(2))
        for j in range(2):
            qchild=tilt(children[j],success[j*2:j*2+2]) if h[j] else [0,0]
            for k in range(2):
                direct=root[j]*children[j][k]*success[j*2+k]/base_success
                assert qroot[j]*qchild[k]==pytest.approx(direct)
