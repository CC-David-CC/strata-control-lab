"""Offline headless qualification of any independently installed instrument page."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--page',required=True)
    p.add_argument('--base-url',default='http://127.0.0.1:8878');p.add_argument('--expected-instruments',type=int)
    p.add_argument('--output',help='Separate integration evidence from each independent branch receipt')
    args=p.parse_args();out=Path(args.output) if args.output else Path('evidence/instruments')/args.page/'browser';out.mkdir(parents=True,exist_ok=True)
    errors=[];outside=[];checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1500,'height':1060})
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(r):
            if not r.request.url.startswith(args.base_url+'/'):outside.append(r.request.url);r.abort()
            else:r.continue_()
        page.route('**/*',route)
        catalog=page.request.get(args.base_url+'/api/catalog').json()
        applied=next(x for x in catalog['pages'] if x['id']==args.page).get('applied',False)
        actual=sum(x.get('section')=='instrument' and bool(x.get('applied'))==applied for x in catalog['pages'])
        if args.expected_instruments is not None:assert actual==args.expected_instruments
        args.expected_instruments=actual
        page.goto(args.base_url);expect(page.locator('.experiment-card')).to_have_count(len(catalog['pages']))
        page.locator('[data-filter="applications"]' if applied else '[data-filter="instruments"]').click();expect(page.locator('.experiment-card')).to_have_count(args.expected_instruments)
        checks.append('independent-gallery-discovery')
        page.goto(args.base_url+'/lab/'+args.page+'?manual=1');page.locator('#run').click()
        page.wait_for_function("() => ['Completed','Failed'].includes(document.getElementById('status').textContent)",timeout=120000)
        assert page.locator('#status').inner_text()=='Completed',page.locator('#result').inner_text()
        for option in page.locator('#lens option').all():
            page.locator('#lens').select_option(option.get_attribute('value'))
            assert page.locator('#instrument-view').inner_text()
        page.locator('#lens').select_option('0')
        for attr in ['min','max']:
            value=page.locator('#dial').get_attribute(attr);page.locator('#dial').fill(value);page.locator('#dial').dispatch_event('input')
            expect(page.locator('#dial-value')).to_have_text(chr(65+int(value)) if applied else value)
        value=page.locator('#dial').get_attribute('value')
        page.locator('#dial').fill(value);page.locator('#dial').dispatch_event('input')
        if args.page=='counterexamples':
            before=page.locator('.instrument-equation').inner_text()
            page.locator('[data-pair="1"]').click()
            assert page.locator('.instrument-equation').inner_text()!=before
            expect(page.locator('[data-pair="1"]')).to_have_attribute('aria-pressed','true')
            page.locator('[data-pair="0"]').click()
        checks.append('all-case-selectors-and-control-extremes')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.evaluate('scrollTo(0,0)');page.screenshot(path=str(out/'desktop.png'),full_page=True)
        with page.expect_download() as download:page.locator('#download').click()
        data=json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
        assert data['experiment']==args.page and data['receipt']['mode']=='recorded'
        assert data['receipt']['requests']>0 and all(x['provenance']=='native-strata' for x in data['receipt']['calls'])
        checks.append('exact-native-replay-and-json-export')
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(out/'mobile.png'),full_page=True);checks.append('390px-content-layout')
        page.emulate_media(reduced_motion='reduce')
        if applied:
            assert page.locator('.applied-art').evaluate("e=>[...e.querySelectorAll('*')].every(n=>getComputedStyle(n).animationName==='none')")
        else:
            assert page.locator('.instrument-flow i').first.evaluate("e=>getComputedStyle(e,'::after').animationName")=='none'
        page.locator('#dial').focus();assert page.evaluate('document.activeElement.id')=='dial'
        checks.append('reduced-motion-and-keyboard')
        assert not errors,errors;assert not outside,outside;browser.close()
    result=dict(page=args.page,checks=checks,console_errors=errors,external_requests=outside,installed_instruments=args.expected_instruments)
    (out/'results.json').write_bytes(json.dumps(result,indent=2).encode());print(json.dumps(result))

if __name__=='__main__':main()
