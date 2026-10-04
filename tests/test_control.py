from control_lab.paths import DATA
import math,json
from pathlib import Path
import pytest
from control_lab.instrument_math import contrast

def test_log_odds_control_and_absolute_permission():
    b=[.2,.55,.05,.2];e=[.65,.2,.01,.14];a=[.05,.75,.15,.05]
    for alpha in [0,.1,.5,1,3]:
        q=contrast(b,e,a,alpha,[0,1,3])
        change=math.log(q[0]/q[1])-math.log(b[0]/b[1])
        expected=alpha*(math.log(e[0]/a[0])-math.log(e[1]/a[1]))
        assert change==pytest.approx(expected) and q[2]==0
    assert max(range(4),key=lambda i:contrast(b,e,a,0,[0,1,3])[i])==1
    assert max(range(4),key=lambda i:contrast(b,e,a,1,[0,1,3])[i])==0

def test_native_commit_is_owned_by_the_finite_controller():
    data=json.loads((DATA/'captures/control.json').read_text(encoding='utf-8'))['result']
    for c in data['commits']:
        q=contrast(data['base'],data['desired'],data['undesired'],c['alpha'],data['allowed'])
        assert c['distribution']==pytest.approx(q)
        assert c['emitted']['output']['text']==chr(65+c['selected'])
        assert c['selected'] in data['allowed']
