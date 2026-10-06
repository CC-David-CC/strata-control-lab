"""Audit all 39 actual page displays, native receipts and non-token exceptions."""
import argparse
import json
import math
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-url', default='http://127.0.0.1:8879')
    ap.add_argument('--output', default='evidence/every-score-view')
    args = ap.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1040})
        page.on('pageerror', lambda error: errors.append(str(error)))
        catalog = page.request.get(args.base_url+'/api/catalog').json()['pages']
        for definition in catalog:
            name = definition['id']
            page.goto(args.base_url+'/lab/'+name+'?manual=1')
            expect(page.locator('#run')).to_be_enabled()
            page.locator('#run').click()
            expect(page.locator('#status')).to_have_text('Completed', timeout=60000)
            with page.expect_download() as download:
                page.locator('#download').click()
            snapshot = json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
            assert snapshot['score_view'] == definition['score_view']
            expect(page.locator('#score-panel')).to_be_visible()
            assert page.locator('#score-raw-meaning').inner_text() == definition['score_view']['raw']
            assert page.locator('#score-derived-meaning').inner_text() == definition['score_view']['derived']
            calls = snapshot['receipt']['calls']
            counts = []
            if calls:
                # All requests, including deliberately unscored latency arms.
                for i, call in enumerate(calls):
                    page.locator('#score-call').select_option(str(i))
                    entries = (call['response']['choices'][0].get('logprobs') or {}).get('content') or []
                    badges = page.locator('#score-panel .token-logprob')
                    assert badges.count() == len(entries), (name, i)
                    for j, token in enumerate(entries):
                        assert float(badges.nth(j).get_attribute('data-logprob')) == token['logprob']
                        value = float(page.locator('#score-panel .token-probability').nth(j).get_attribute('data-probability'))
                        assert math.isclose(value, math.exp(token['logprob']), rel_tol=1e-14, abs_tol=0)
                    if not entries:
                        assert 'no scored answer tokens' in page.locator('#score-call-view').inner_text()
                    assert page.locator('#request-select').input_value() == str(i)
                    counts.append(len(entries))
                assert sum(counts), name
            elif name == 'speculation':
                emitted = snapshot['result']['oracle']['example_rejection']['emitted']
                badges = page.locator('#score-panel .token-logprob')
                assert badges.count() == len(emitted)
                for i, token in enumerate(emitted):
                    assert float(badges.nth(i).get_attribute('data-logprob')) == token['logprob']
            else:
                assert name in ['sampler-sandbox', 'frontier', 'research-map']
                assert page.locator('#score-panel .token-logprob').count() == 0
                assert 'No native Chat token-probability row' in page.locator('#score-panel').inner_text()
            for width in [1440,390]:
                page.set_viewport_size({'width':width,'height':1040 if width==1440 else 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (name,width)
            page.set_viewport_size({'width':1440,'height':1040})
            if name in ['choice','samplers','pressure','compiler','sampler-sandbox','frontier','speculation']:
                page.locator('#score-panel').screenshot(path=str(out/(name+'.png')))
            checks.append(dict(page=name,raw_kind=definition['score_view']['raw_kind'],
                               requests=len(calls),scored_tokens=sum(counts),
                               request_token_counts=counts,derived_explanation=True,
                               exports_keep_contract=True,desktop_phone_no_overflow=True))
            print(name+': raw source, derived meaning and every request checked',flush=True)
        assert len(checks)==39 and not errors,errors
        browser.close()
    (out/'results.json').write_text(json.dumps(dict(pages=checks,page_errors=errors),indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
