"""Check every automatic phase and both portable lesson settings, without a model."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
from playwright.sync_api import sync_playwright,expect


def run_offline(file,output,value=None):
    argv=[str(file),'--lesson-only','--output',str(output)]
    if value is not None:argv+=['--value',str(value)]
    script="import sys,runpy\ndef audit(event,args):\n if event.startswith('socket.'): raise AssertionError('Offline calculation attempted network')\nsys.addaudithook(audit)\nsys.argv="+repr(argv)+"\nrunpy.run_path("+repr(str(file))+",run_name='__main__')"
    result=subprocess.run([sys.executable,'-I','-c',script],capture_output=True,encoding='utf-8',timeout=60)
    assert result.returncode==0,(file,result.stdout,result.stderr)
    return json.loads(output.read_text(encoding='utf-8'))['calculation']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8878')
    parser.add_argument('--output',default='evidence/quality/browser')
    parser.add_argument('--downloads',required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    downloads=Path(args.downloads).resolve();downloads.mkdir(parents=True,exist_ok=True)
    errors=[];outside=[];rows=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();p=browser.new_page(viewport=dict(width=1500,height=1060))
        p.on('pageerror',lambda error:errors.append(str(error)))
        def route(r):
            if not r.request.url.startswith(args.base_url+'/'):outside.append(r.request.url);r.abort()
            else:r.continue_()
        p.route('**/*',route);p.emulate_media(reduced_motion='reduce');p.clock.install()
        catalog=p.request.get(args.base_url+'/api/catalog').json()['pages'];ids=[x['id'] for x in catalog]
        p.goto(args.base_url+'/lab/'+ids[0])
        for index,name in enumerate(ids):
            expect(p).to_have_url(args.base_url+'/lab/'+name)
            expect(p.locator('#status')).to_have_text('Completed',timeout=30000)
            expect(p.locator('#tour-bar')).to_have_attribute('data-step','0')
            p.clock.pause_at(p.evaluate('Date.now()')/1000+.005)
            assert p.locator('#lesson-unavailable').is_hidden(),name
            with p.expect_download() as dl:p.locator('#python-download').evaluate('e=>e.click()')
            file=downloads/(name+'.py');dl.value.save_as(str(file));saved=runpy.run_path(str(file),run_name='test_example')['CAPTURED']
            for state in saved['lesson']['states']:
                actual=run_offline(file,downloads/(name+'-'+str(state['value'])+'.json'),state['value'])
                assert actual==state,(name,actual,state)
            phases=[];total=int(p.locator('#tour-bar').get_attribute('data-total'))
            while p.url.endswith('/lab/'+name):
                expect(p.locator('#status')).to_have_text('Completed',timeout=30000)
                expect(p.locator('.tour-focus')).to_have_count(1)
                step=int(p.locator('#tour-bar').get_attribute('data-step'))
                assert p.locator('#tour-bar').get_attribute('data-state')=='playing'
                visible=[]
                for label,width,height in [('desktop',1500,1060),('phone',390,844)]:
                    p.set_viewport_size(dict(width=width,height=height))
                    # Reframe the current target using the same available viewport policy.
                    p.evaluate("()=>{const e=document.querySelector('.tour-focus');const b=document.querySelector('#tour-bar').getBoundingClientRect(),r=e.getBoundingClientRect();window.scrollBy(0,r.top-Math.max(24,(b.top-30-Math.min(r.height,b.top-30))/2));}")
                    box=p.locator('.tour-focus').bounding_box();bar=p.locator('#tour-bar').bounding_box()
                    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,step,label,'overflow')
                    shown=max(0,min(box['y']+box['height'],bar['y']-12)-max(box['y'],0))
                    assert shown>=min(90,box['height'])-2,(name,step,label,box,bar,'target hidden')
                    target=p.locator('.tour-focus').get_attribute('class') or ''
                    if step in (0,1) or (catalog[index].get('applied') and any(c in target for c in ('applied-stage','applied-meaning','research-stats'))):
                        p.screenshot(path=str(out/(name+'-'+label+'-'+str(step)+'.png')),animations='disabled')
                    visible.append(dict(viewport=label,target_height=round(box['height']),visible_height=round(shown)))
                delay=int(p.locator('#tour-bar').get_attribute('data-delay-ms'));assert 4000<=delay<=6500
                phases.append(dict(step=step,caption=p.locator('#tour-caption').inner_text(),layer=p.locator('#tour-bar').get_attribute('data-layer'),hold_ms=delay,views=visible))
                p.set_viewport_size(dict(width=1500,height=1060));p.clock.fast_forward(delay+20)
                if p.url.endswith('/lab/'+name):
                    expect(p.locator('#tour-bar')).not_to_have_attribute('data-step',str(step))
            assert any(x['layer']=='derived' for x in phases),name
            assert phases[0]['layer'] in ('raw','synthetic','inputs'),name
            assert {x['step'] for x in phases}==set(range(total)),(name,[x['step'] for x in phases],total)
            next_name=ids[(index+1)%len(ids)];expect(p).to_have_url(args.base_url+'/lab/'+next_name)
            rows.append(dict(page=name,phase_count=total,phases=phases,portable_calculations=2,
                             python_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),network_blocked=True))
            print(name+': both calculations and '+str(total)+' phases passed',flush=True)
            (out/'progress.json').write_bytes(json.dumps(rows,indent=2).encode())
        expect(p.locator('#status')).to_have_text('Completed',timeout=30000)
        # A manually selected compact view, rather than its default, is exported.
        p.locator('[data-lesson-state="1"]').click()
        with p.expect_download() as dl:p.locator('#python-download').click()
        file=downloads/'selected-view.py';dl.value.save_as(str(file))
        saved=runpy.run_path(str(file),run_name='test_example')['CAPTURED']
        assert saved['lesson_view']['index']==1
        assert run_offline(file,downloads/'selected-view.json')==saved['lesson']['states'][1]
        assert not errors,errors;assert not outside,outside;browser.close()
    result=dict(pages=rows,loop_closed=True,selected_view_export=True,console_errors=errors,external_requests=outside)
    (out/'results.json').write_bytes(json.dumps(result,indent=2).encode())


if __name__=='__main__':main()
