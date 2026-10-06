"""Verify raw token badges against downloaded native receipts at desktop and phone sizes."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-url', default='http://127.0.0.1:8879')
    ap.add_argument('--output', default='evidence/raw-token-logprobs/browser')
    args = ap.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1040})
        page.on('pageerror', lambda e: errors.append(str(e)))

        def run(name, case=None):
            page.goto(args.base_url + '/lab/' + name + '?manual=1')
            expect(page.locator('#run')).to_be_enabled()
            if case:
                page.locator('#input-case').select_option(case)
            page.locator('#run').click()
            expect(page.locator('#status')).to_have_text('Completed', timeout=60000)
            with page.expect_download() as download:
                page.locator('#download').click()
            return json.loads(Path(download.value.path()).read_text(encoding='utf-8'))['result']

        def scores(selector, tokens):
            badges = page.locator(selector + ' .token-logprob')
            assert badges.count() == len(tokens)
            for i, token in enumerate(tokens):
                badge = badges.nth(i)
                expect(badge).to_be_visible()
                assert float(badge.get_attribute('data-logprob')) == token['logprob']
                assert 'raw ln p' in badge.inner_text()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')

        for width in [1440, 390]:
            page.set_viewport_size({'width': width, 'height': 1040 if width == 1440 else 844})
            for case in ['decision', 'grammar', 'stream', 'selected-only']:
                result = run('wire', case)
                scores('#wire-tokens', result['entries'])
                page.screenshot(path=str(output/f'{case}-{width}.png'), full_page=True)
                checks.append({'page': 'wire', 'case': case, 'width': width,
                               'tokens': len(result['entries']), 'exact_raw_scores': True})
            result = run('candidates')
            scores('#path-tokens', result['paths'][0]['tokens'])
            page.locator('#path-tokens .token').last.click()
            checks.append({'page': 'candidates', 'width': width, 'exact_raw_scores': True})
            result = run('samplers')
            scores('#sampler-run', result['runs'][0]['tokens'])
            checks.append({'page': 'samplers', 'width': width, 'exact_raw_scores': True})
            result = run('pressure')
            page.locator('#lens').select_option('1')
            scores('#instrument-view', [row['token'] for row in result['cases'][0]['rows']])
            checks.append({'page': 'pressure', 'width': width, 'exact_raw_scores': True})

        # Missing scores stay missing; labels are escaped rather than interpreted as HTML.
        markup = page.evaluate("""async () => {
            const {rawTokenMarkup} = await import('/static/token-chip.js');
            const el = document.createElement('div');
            el.innerHTML = rawTokenMarkup({token:'<img src=x onerror=alert(1)>',logprob:null});
            return {images:el.querySelectorAll('img').length,text:el.textContent,
                    raw:el.querySelector('.token-logprob').getAttribute('data-logprob')};
        }""")
        assert markup['images'] == 0 and 'not returned' in markup['text'] and markup['raw'] == ''
        # Delay only the terminal event of a real recorded HTTP response. The UI
        # must attach scores while the request is still in flight, not just later.
        page.goto(args.base_url + '/lab/wire?manual=1')
        expect(page.locator('#run')).to_be_enabled()
        raw = page.request.post(args.base_url + '/api/run/wire',
                                headers={'X-Control-Lab': '1'},
                                data={'mode': 'recorded', 'case': 'stream'}).text()
        blocks = [block for block in raw.split('\n\n') if block.startswith('data: ')]
        result_at = next(i for i, block in enumerate(blocks)
                         if json.loads(block[6:])['type'] == 'result')
        entries = json.loads(blocks[result_at][6:])['result']['entries']
        page.evaluate("""({before,after}) => {
            const realFetch = window.fetch;
            window.fetch = (url, options) => {
                if (!String(url).startsWith('/api/run/')) return realFetch(url, options);
                const stream = new ReadableStream({start(controller) {
                    controller.enqueue(new TextEncoder().encode(before));
                    window.finishRecordedStream = () => {
                        controller.enqueue(new TextEncoder().encode(after));controller.close();
                    };
                }});
                return Promise.resolve(new Response(stream, {headers:{'Content-Type':'text/event-stream'}}));
            };
        }""", {'before': '\n\n'.join(blocks[:result_at])+'\n\n',
                'after': '\n\n'.join(blocks[result_at:])+'\n\n'})
        page.locator('#run').click()
        expect(page.locator('#live-scores .token-logprob')).to_have_count(len(entries))
        assert page.locator('#status').inner_text() == 'Running'
        scores('#live-scores', entries)
        page.evaluate('window.finishRecordedStream()')
        expect(page.locator('#status')).to_have_text('Completed')
        checks.append({'page':'wire', 'case':'delayed-native-SSE',
                       'tokens':len(entries), 'raw_scores_before_completion':True})
        assert not errors, errors
        browser.close()
    receipt = dict(checks=checks, page_errors=errors, escaped_missing_score=True)
    (output/'results.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
