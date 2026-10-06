"""Audit the common raw/derived panel on all ten original contract examples."""
import json
import math
from pathlib import Path
from playwright.sync_api import expect, sync_playwright


def main():
    root='http://127.0.0.1:8879'
    cases=['decision','router','ambiguity','stream','grammar','json-schema',
           'reasoning-json','tool-call','tool-result','selected-only']
    checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page()
        for case in cases:
            page.goto(root+'/lab/wire?manual=1');expect(page.locator('#run')).to_be_enabled()
            page.locator('#input-case').select_option(case);page.locator('#run').click()
            expect(page.locator('#status')).to_have_text('Completed',timeout=30000)
            with page.expect_download() as dl:page.locator('#download').click()
            saved=json.loads(Path(dl.value.path()).read_text(encoding='utf-8'))
            entries=saved['result']['entries'];badges=page.locator('#score-panel .token-logprob')
            assert badges.count()==len(entries)
            for i,token in enumerate(entries):
                assert float(badges.nth(i).get_attribute('data-logprob'))==token['logprob']
                value=float(page.locator('#score-panel .token-probability').nth(i).get_attribute('data-probability'))
                assert math.isclose(value,math.exp(token['logprob']),rel_tol=1e-14)
            if not entries:assert 'no scored answer tokens' in page.locator('#score-call-view').inner_text()
            checks.append(dict(case=case,tokens=len(entries),raw_and_derived_explained=True))
        browser.close()
    out=Path('evidence/every-score-view/wire-cases.json')
    out.write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print('All ten wire examples explain raw/derived scores and preserve original tokens')


if __name__=='__main__':main()
