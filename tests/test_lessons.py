"""Portable lessons reproduce independently retained page/oracle results."""
import asyncio
import math
import pytest
from control_lab.catalog import PAGES
from control_lab.client import Backend, Context
from control_lab.scenarios import run_page
from control_lab.static.lesson_math import LESSON_SPECS, calculate_lesson, make_lesson, _ttt


@pytest.fixture(scope='module')
def examples():
    async def capture():
        async def emit(*args):pass
        out={}
        async with Backend('recorded') as backend:
            for page in PAGES:
                out[page['id']]=await run_page(Context(backend,emit),page['id'],{})
        return out
    return asyncio.run(capture())


@pytest.mark.parametrize('name',list(LESSON_SPECS))
def test_each_complete_recording_has_two_recalculable_views_and_rejects_invalid_knobs(name,examples):
    data=examples[name];lesson=make_lesson(name,data)
    assert len(lesson['states'])==2,lesson
    assert lesson['states'][0]!=lesson['states'][1]
    for state in lesson['states']:
        assert state==calculate_lesson(name,data,state['value'])
        assert state['summary'] and state['note']
        assert all(math.isfinite(r['value']) for r in state['rows'])
    for invalid in [math.nan,math.inf,True,'1',lesson['low']-1,lesson['high']+1]:
        with pytest.raises(ValueError):calculate_lesson(name,data,invalid)
    if lesson['integer']:
        with pytest.raises(ValueError):calculate_lesson(name,data,.5)


def test_all_lesson_defaults_agree_with_existing_independent_page_calculations(examples):
    def calc(name):return calculate_lesson(name,examples[name])['metrics']
    for name in ('choice','boolean','score'):
        assert calc(name)['top_weight']==pytest.approx(examples[name]['statistics']['top_weight'])
    assert calc('score')['expected_value']==pytest.approx(examples['score']['statistics']['expected_score'])
    assert calc('candidates')['group_weights']==pytest.approx([r['weight'] for r in examples['candidates']['groups']])
    assert calc('controller')['selected_weight']==pytest.approx(examples['controller']['legal_conditional_weight'])
    assert calc('rerank')['scores']==pytest.approx([r['score'] for r in examples['rerank']['sources']])
    assert calc('graph')['utility']==pytest.approx(examples['graph']['solver']['utility'])
    assert calc('scene')['utilities']==pytest.approx([r['score'] for r in examples['scene']['candidates'] if r['valid']])
    assert calc('wire')['raw_probability']==pytest.approx(math.exp(examples['wire']['entries'][0]['logprob']))
    assert calc('speculation')['target_sequence_logprob']==pytest.approx(examples['speculation']['oracle']['example_rejection']['target_sequence_logprob'])
    assert calc('performance')['times_ms']==pytest.approx([r['median_ms'] for r in examples['performance']['rows']])
    s=examples['samplers']['runs'][0]['tokens'][0]
    assert calc('samplers')['selected']==s['strata_sampling']['probability']
    assert calc('samplers')['raw']==pytest.approx(math.exp(s['logprob']))
    assert calc('tictactoe')['regret']==examples['tictactoe']['frames'][0]['regret']
    assert calc('chess')['mating_shortlist_weight']==pytest.approx(sum(r['weight'] for r,m in zip(examples['chess']['measure']['rows'],examples['chess']['shortlist']) if m['mate']))
    for hand in examples['poker']['hands']:
        assert calc('poker')['values'][hand['card']]==pytest.approx(hand['values'])
    assert calc('thermal')['temperatures']==pytest.approx([f['next_temperature'] for f in examples['thermal']['frames']])
    assert calc('scheduler')['total_lateness']==examples['scheduler']['total_lateness']
    assert calc('context')['no_weight']==pytest.approx(examples['context']['runs'][0]['measure']['rows'][1]['weight'])
    assert calc('observer')['actions']==[f['action'] for f in examples['observer']['frames']]
    assert calc('calibration')['brier']==pytest.approx(examples['calibration']['statistics']['brier'])
    assert calc('information')['gain_bits']==pytest.approx(examples['information']['tests'][0]['gain_bits'])
    valid=[c for c in examples['search']['candidates'] if c['valid']]
    assert calc('search')['retained']==max(valid,key=lambda c:c['score']-.1*c['cost']/3)['id']
    f=examples['frontier'];assert calc('frontier')['transfer_ms']==pytest.approx(f['vocabulary']*f['bytes_per_logit']/12e6)
    assert sum(calc('research-map')['categories'].values())==len(examples['research-map']['branches'])
    assert calc('pressure')['mass']==pytest.approx(examples['pressure']['cases'][0]['rows'][0]['mass'])
    for key in ('F','S','AND','OR','F_given_S'):
        assert calc('circuit')[key]==pytest.approx(examples['circuit']['cases'][0]['operations'][key])
    assert calc('control')['probabilities']==pytest.approx(examples['control']['commits'][0]['distribution'])
    assert calc('future')['base_success']==pytest.approx(examples['future']['base_success'])
    for row,expected in zip(calc('sensitivity')['matrix'],examples['sensitivity']['matrix']):assert row==pytest.approx(expected)
    assert calc('sensitivity')['holdout_residual']==pytest.approx(examples['sensitivity']['holdout']['residual'])
    assert calc('counterexamples')['margin_distance']==pytest.approx(examples['counterexamples']['rankings']['equivalent'][0]['margin_distance'])


def test_hand_calculated_joint_worlds_and_observation():
    data={'cases':[{'measurement':{'rows':[{'logprob':math.log(p)} for p in [.1,.1,.2,.6]]}}]}
    m=calculate_lesson('circuit',data)['metrics']
    assert [m[k] for k in ('F','S','AND','OR','F_given_S','marginal_product')]==pytest.approx([.7,.8,.6,.9,.75,.56])
    conditioned=calculate_lesson('circuit',data,1)['metrics']
    assert conditioned['F']==pytest.approx(.75) and conditioned['S']==pytest.approx(1)


def test_same_conditional_answer_different_grammar_pressure():
    def case(z):return {'name':'Synthetic','rows':[{'token':{'logprob':math.log(.6*z),'strata_sampling':{'probability':.6}}}]}
    data={'cases':[case(.99),case(.01)]}
    a=calculate_lesson('pressure',data,0)['metrics'];b=calculate_lesson('pressure',data,1)['metrics']
    assert a['mass']==pytest.approx(.99) and b['mass']==pytest.approx(.01)
    assert b['pressure_nats']-a['pressure_nats']==pytest.approx(math.log(99))


def test_no_coverage_no_accuracy_and_incomplete_scores_stay_unavailable(examples):
    m=calculate_lesson('calibration',examples['calibration'],1)['metrics']
    assert m['retained']==0 and m['accuracy'] is None
    assert make_lesson('wire',{'entries':[]})['states']==[]
    lesson=make_lesson('choice',{'rows':[{'logprob':None}]})
    assert not lesson['states'] and 'missing top-N' in lesson['unavailable']


def test_exact_game_oracle_and_forbidden_action_invariance(examples):
    assert _ttt('XX.OO....','X')==1
    assert _ttt('XXOOOXXOX','X')==0
    for alpha in (0,.5,1,2,3):
        m=calculate_lesson('control',examples['control'],alpha)['metrics']
        assert m['forbidden_mass']==0 and sum(m['probabilities'])==pytest.approx(1)
    with pytest.raises(ValueError,match='Index'):calculate_lesson('wire',examples['wire'],10000)
