from control_lab.paths import DATA
import json
from pathlib import Path
import pytest
from control_lab.instrument_page_sensitivity import central

def test_response_matrix_recovers_linear_map_in_coordinate_units():
    def z(hours,load):return [2*hours+.3*load, -hours+4*load, 7.]
    assert central(z(8,50),z(4,50),2)==pytest.approx([2,-1,0])
    assert central(z(6,60),z(6,40),10)==pytest.approx([.3,4,0])
    with pytest.raises(ValueError):central([1],[0],0)

def test_native_holdout_is_separate_and_discrete_edit_has_no_derivative():
    d=json.loads((DATA/'captures/sensitivity.json').read_text(encoding='utf-8'))['result']
    assert len(d['observations'])==7 and d['holdout']['intervention']==[-1,5]
    baseline=d['observations'][0]['z'];observed=d['observations'][6]['z']
    assert d['holdout']['observed_delta']==pytest.approx([a-b for a,b in zip(observed,baseline)])
    assert d['discrete_delta']==pytest.approx([a-b for a,b in zip(d['observations'][5]['z'],baseline)])
