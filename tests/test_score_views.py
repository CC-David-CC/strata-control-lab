"""Every page must disclose its raw source and distinct derived calculation."""
from control_lab.catalog import PAGES
from control_lab.score_views import SCORE_VIEWS


def test_every_example_has_its_own_raw_and_derived_contract():
    assert len(PAGES) == 39
    assert {p['id'] for p in PAGES} == set(SCORE_VIEWS)
    assert len({p['score_view']['derived'] for p in PAGES}) == 39
    for page in PAGES:
        view = page['score_view']
        assert all(view[key] for key in ['raw', 'derived', 'scope', 'raw_kind'])
        assert 'Missing top-N alternatives stay unknown' in view['scope']


def test_no_probability_row_is_invented_for_non_model_examples():
    kinds = {page['id']: page['score_view']['raw_kind'] for page in PAGES}
    assert kinds['sampler-sandbox'] == 'synthetic'
    assert kinds['frontier'] == kinds['research-map'] == 'no_token_row'
    assert kinds['speculation'] == 'diagnostic'
    assert sum(value == 'native' for value in kinds.values()) == 35


def test_legal_set_instruments_disclose_recovered_label_probability():
    for page in PAGES:
        if page.get('section') == 'instrument':
            assert 'recover raw label p' in page['score_view']['raw']
            assert 'direct target score' in page['score_view']['raw']
