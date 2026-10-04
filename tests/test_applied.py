"""Exact toy oracles and real recorded applied cases; no GPU needed."""
from control_lab.paths import DATA
import copy
import json
import math
from pathlib import Path
import pytest
from control_lab.static.applied_math import (INITIAL_PROOF,TACTICS,LESSON_SPECS,polynomial,expression_cost,
    proof_step,proof_search,divider,reserve,inspection,calculate_lesson,make_lesson)



@pytest.mark.parametrize('name',list(LESSON_SPECS))
def test_native_cases_remain_checked_and_portable(name):
    capture=json.loads((DATA/'captures'/(name+'.json')).read_text(encoding='utf-8'))
    data=capture['result'];lesson=make_lesson(name,data)
    assert len(lesson['states'])==2 and lesson['states'][0]!=lesson['states'][1]
    before,after=lesson['states']
    assert before['metrics']!=after['metrics'] or before['summary']!=after['summary']
    assert capture['receipt']['requests']==len(data['cases'])*2
    for case in data['cases']:
        assert case['selected'] in case['allowed']
        assert case['commit']['output']['text']==chr(65+case['selected'])
        assert sum(r['weight'] for r in case['measurement']['rows'])==pytest.approx(1)
        assert case['regret']>=0
        assert case['utilities'][case['oracle']]>=case['uniform_utility']-1e-12
    for state in lesson['states']:
        assert state==calculate_lesson(name,data,state['value'])
        assert all(math.isfinite(r['value']) for r in state['rows'])
    for invalid in [math.nan,math.inf,True,'1',lesson['low']-1,lesson['high']+1]:
        with pytest.raises(ValueError):calculate_lesson(name,data,invalid)
    if lesson['integer']:
        with pytest.raises(ValueError):calculate_lesson(name,data,1.5)


def test_equivalence_is_exact_and_never_executes_expression_text():
    assert polynomial('x*2+0')==polynomial('x+x')==polynomial('2*x')==(0,2,0)
    assert polynomial('x*3')!=(0,2,0)
    assert polynomial('(x+1)*(x-1)')==(-1,0,1)
    assert expression_cost('x*2+0',3)==4
    assert expression_cost('x+x',3)==1 and expression_cost('2*x',.5)==.5
    for expression in ["__import__('os').system('no')",'x/2','x**2','x*x*x','y+1','True']:
        with pytest.raises(ValueError):polynomial(expression)


def test_proof_checker_requires_actual_assumptions_and_preserves_state():
    initial=copy.deepcopy(INITIAL_PROOF)
    with pytest.raises(ValueError):proof_step(initial,TACTICS[2])
    state=initial
    for tactic in TACTICS[:3]:state=proof_step(state,tactic)
    assert state['goal'] is None and initial==INITIAL_PROOF
    assert proof_search(2)['proved'] is False
    assert proof_search(3)['path']==TACTICS[:3]
    assert proof_search(3)['checks']==12
    # Independent truth table of (P AND Q) IMPLIES P.
    assert all((not (p and q)) or p for p in (False,True) for q in (False,True))


def test_divider_corners_include_opposing_tolerance_extremes():
    r=divider(1000,2000,5,3.3,.05)
    assert r['nominal']==pytest.approx(10/3)
    assert r['low']==pytest.approx(5*1900/(1050+1900))
    assert r['high']==pytest.approx(5*2100/(950+2100))
    assert r['worst_error']==pytest.approx(max(abs(r['low']-3.3),abs(r['high']-3.3)))
    assert divider(1000,2000,5,3.3,0)['low']==pytest.approx(10/3)
    for args in [(0,2000,5,3.3,.05),(1000,-1,5,3.3,.05),(1000,2000,5,3.3,1)]:
        with pytest.raises(ValueError):divider(*args)


def test_stale_or_duplicate_reserve_never_recreates_stock():
    initial={'stock':1,'version':7};saved=copy.deepcopy(initial)
    assert reserve(initial,6)['reason']=='stale version'
    first=reserve(initial,7);assert first['committed'] and first['record']=={'stock':0,'version':8}
    assert reserve(first['record'],7)['reason']=='stale version'
    assert reserve(first['record'],8)['reason']=='no stock'
    assert initial==saved


def test_inspection_break_even_uses_likelihood_not_answer_weights():
    result=inspection(.55,.9,.1)
    assert result['act']==pytest.approx(.55)
    assert result['inspect']==pytest.approx(.8)
    assert result['gross_value']==pytest.approx(.35)
    assert inspection(.55,.9,.5)['inspect']==pytest.approx(.4)
    assert inspection(.55,.5,0)['inspect']==pytest.approx(.55)


def test_actual_disappointing_native_results_are_preserved():
    read=lambda name:json.loads((DATA/'captures'/(name+'.json')).read_text(encoding='utf-8'))['result']
    assert read('budget')['cases'][2]['regret']==pytest.approx(.15)
    assert read('divider')['cases'][1]['regret']>2
    # This limited bank did not change the greedy action; do not advertise an invented attack.
    assert all(c['regret']==0 for c in read('adversary')['cases'])
