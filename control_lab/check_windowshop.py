"""Walk every page automatically, run its portable mock, and verify the loop closes."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8878')
    parser.add_argument('--output',default='evidence/walkthrough/browser')
    parser.add_argument('--downloads',required=True,help='Local directory for generated self-contained scripts')
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    downloads=Path(args.downloads).resolve();downloads.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[];outside=[];requests=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport=dict(width=1500,height=1060))
        page.on('pageerror',lambda error:errors.append(str(error)))
        def route(r):
            if not r.request.url.startswith(args.base_url+'/'):outside.append(r.request.url);r.abort()
            else:r.continue_()
        page.route('**/*',route)
        page.on('request',lambda r:requests.append(r.post_data_json) if '/api/run/' in r.url else None)
        catalog=page.request.get(args.base_url+'/api/catalog').json()['pages'];ids=[p['id'] for p in catalog]
        page.clock.install()
        page.goto(args.base_url+'/lab/'+ids[0])
        for at,name in enumerate(ids):
            expected=args.base_url+'/lab/'+name
            expect(page).to_have_url(expected)
            expect(page.locator('#status')).to_have_text('Completed',timeout=30000)
            expect(page.locator('#tour-bar')).to_have_attribute('data-step','0')
            page.clock.pause_at(page.evaluate('Date.now()')/1000+.005)
            assert page.locator('#tour-bar').get_attribute('data-state')=='playing'
            assert page.locator('#request-body').inner_text()
            assert page.locator('#constraint-body').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name
            if at==0:
                plans=page.evaluate("async()=>Object.keys((await import('/static/tour.js')).LESSONS)")
                assert set(plans)==set(ids)
            # Programmatic download preserves autoplay; a real user interaction pauses it.
            with page.expect_download() as pending:page.locator('#python-download').evaluate('e=>e.click()')
            file=downloads/(name+'.py');pending.value.save_as(str(file))
            imported=runpy.run_path(str(file),run_name='qualified_example')
            captured=imported['CAPTURED'];assert captured['experiment']==name
            calls=captured['receipt']['calls']
            if calls:
                assert json.loads(page.locator('#request-body').inner_text())==calls[0]['request']
            script="import sys,runpy\ndef audit(event,args):\n if event.startswith('socket.'): raise AssertionError('Offline example attempted networking: '+event)\nsys.addaudithook(audit)\nsys.argv="+repr([str(file),'--all','--output',str(downloads/(name+'.json'))])+"\nrunpy.run_path("+repr(str(file))+",run_name='__main__')"
            result=subprocess.run([sys.executable,'-I','-c',script],capture_output=True,encoding='utf-8',timeout=60)
            assert result.returncode==0,(name,result.stdout,result.stderr)
            replay=json.loads((downloads/(name+'.json')).read_text(encoding='utf-8'))
            if calls:
                assert [c['response'] for c in replay['calls']]==[c['response'] for c in calls]
                assert [c['request'] for c in replay['calls']]==[c['request'] for c in calls]
            else:assert replay['mode']=='offline-snapshot' and replay['result']==captured['result']
            page.set_viewport_size(dict(width=390,height=844))
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name+' mobile'
            if name in ['choice','samplers','circuit','counterexamples']:
                page.screenshot(path=str(out/(name+'-mobile.png')),full_page=True,animations='disabled')
            page.set_viewport_size(dict(width=1500,height=1060))
            if name in ['choice','samplers','circuit','counterexamples']:
                page.screenshot(path=str(out/(name+'.png')),full_page=True,animations='disabled')
            observed={0};total=int(page.locator('#tour-bar').get_attribute('data-total'))
            next_name=ids[(at+1)%len(ids)]
            for _ in range(total+8):
                if page.url!=expected:break
                assert page.locator('#tour-bar').get_attribute('data-state')=='playing',(name,page.locator('#tour-caption').inner_text())
                page.clock.fast_forward(9000)
                if page.url!=expected:break
                expect(page.locator('#status')).to_have_text('Completed',timeout=30000)
                state=page.locator('#tour-bar').get_attribute('data-state')
                assert state=='playing',(name,page.locator('#tour-caption').inner_text())
                observed.add(int(page.locator('#tour-bar').get_attribute('data-step')))
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name+' phase'
            expect(page).to_have_url(args.base_url+'/lab/'+next_name,timeout=15000)
            assert urlsplit(page.url).query==''
            assert observed==set(range(total)),(name,observed,total)
            row=dict(page=name,autostart=True,phases=total,next=next_name,independent_navigation=True,
                     python_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),mock_calls=len(calls),
                     python_network_blocked=True,desktop_and_mobile=True)
            rows.append(row);print(json.dumps(row),flush=True)
            (out/'progress.json').write_bytes(json.dumps(rows,indent=2).encode())
        assert page.url==args.base_url+'/lab/'+ids[0]
        expect(page.locator('#status')).to_have_text('Completed',timeout=30000)
        page.locator('#tour-toggle').click();expect(page.locator('#tour-bar')).to_have_attribute('data-state','paused')
        count=len(requests);page.clock.fast_forward(120000)
        assert page.url.endswith('/lab/'+ids[0]) and len(requests)==count
        page.locator('#tour-toggle').click();expect(page.locator('#tour-bar')).to_have_attribute('data-state','playing')
        expect(page.locator('#status')).to_have_text('Completed',timeout=30000)
        page.emulate_media(reduced_motion='reduce')
        assert page.locator('.bar-fill').first.evaluate('e=>getComputedStyle(e).animationName')=='none'
        page.locator('#mode').select_option('live') # A trusted interaction must stop auto replay.
        expect(page.locator('#tour-bar')).to_have_attribute('data-state','paused')
        count=len(requests);page.clock.fast_forward(120000);assert len(requests)==count
        assert all(r['mode']=='recorded' for r in requests),requests
        assert not errors,errors;assert not outside,outside
        # The gallery also starts without a click and has an explicit opt-out.
        page.goto(args.base_url)
        page.clock.run_for(13000)
        expect(page).to_have_url(args.base_url+'/lab/choice',timeout=15000)
        page.goto(args.base_url);page.locator('#stay-gallery').click();page.clock.fast_forward(60000)
        assert page.url.rstrip('/')==args.base_url.rstrip('/')
        applied=sum(bool(p.get('applied')) for p in catalog)
        if applied:
            page.locator('[data-filter="applications"]').click()
            expect(page.locator('.experiment-card')).to_have_count(applied)
            page.locator('#search').fill('circuit')
            expect(page.locator('.experiment-card')).to_have_count(1)
            page.locator('#search').fill('')
            page.locator('[data-filter="all"]').click()
        expect(page.locator('.experiment-card')).to_have_count(len(ids))
        page.set_viewport_size(dict(width=1500,height=1060))
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.screenshot(path=str(out/'index-preview.png'),animations='disabled')
        page.screenshot(path=str(out/'index.png'),full_page=True,animations='disabled')
        browser.close()
    result=dict(pages=rows,loop_closed=True,pause_resume=True,live_mode_never_auto_runs=True,
                reduced_motion=True,gallery_autostart_and_opt_out=True,
                console_errors=errors,external_requests=outside,total_recorded_ui_requests=len(requests))
    (out/'results.json').write_bytes(json.dumps(result,indent=2).encode())
    print('Windowshop gate passed: '+str(len(rows))+' autonomous pages and portable examples.',flush=True)


if __name__=='__main__':main()
