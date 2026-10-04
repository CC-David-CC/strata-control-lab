from control_lab.paths import DATA
import json
from pathlib import Path
import pytest
from control_lab.instrument_page_counterexamples import canonical, evaluate, nonnegative, witness, binary_js


def test_exact_algebra_and_checked_language():
    assert canonical('(((x+1)*(x-1))+1)') == canonical('x*x') == (0,0,1)
    assert canonical('((x+1)-1)') == canonical('((2*x)-x)') == (0,1,0)
    for bad in ["__import__('os').system('anything')", 'x.real', 'x**2', 'x/2', 'True',
                'x*x*x', '1001*x', '[x]', 'y', 'x+'*100+'x']:
        with pytest.raises(ValueError): canonical(bad)


def test_integer_minimum_and_distinct_witnesses():
    assert nonnegative(canonical('x*x-x'))  # Integer minimum 0; real minimum -1/4.
    assert not nonnegative(canonical('x*x-x-1'))
    assert not nonnegative(canonical('-x*x'))
    assert not nonnegative(canonical('x'))
    assert nonnegative(canonical('0'))
    for a in [(0,1,0),(2,3,4),(-5,4,1),(0,0,0)]:
        for b in [(0,1,0),(1,0,0),(0,0,1)]:
            w = witness(a,b)
            assert (w is None) == (a == b)
            if w: assert evaluate(a,w['x']) == w['left'] != w['right'] == evaluate(b,w['x'])
    assert binary_js(.3,.3) == pytest.approx(0)
    assert binary_js(.2,.8) == pytest.approx(binary_js(.8,.2))


def test_native_graph_retains_truth_and_training_pairs():
    d=json.loads((DATA/'captures/counterexamples.json').read_text(encoding='utf-8'))['result']
    assert len(d['nodes']) == 12 and len(d['pairs']) == 66
    for p in d['pairs']:
        a,b=d['nodes'][p['left']],d['nodes'][p['right']]
        assert p['equivalent'] == (canonical(a['expression']) == canonical(b['expression']))
        if p['witness']:
            w=p['witness'];assert evaluate(a['coefficients'],w['x']) != evaluate(b['coefficients'],w['x'])
    assert all(d['rankings'][key] for key in ['equivalent','distinct','collision'])
    assert d['generated']['expression'] in [n['expression'] for n in d['nodes']]
    assert len(d['training_pairs']) == len(d['rankings']['equivalent'])
