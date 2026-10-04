"""Verify portable assembly, literal escaping and the downloadable archive."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import runpy
from .paths import STATIC
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8878')
    parser.add_argument('--downloads',required=True)
    parser.add_argument('--evidence',default='docs/provenance/portable-checks.json')
    parser.add_argument('--manifest',default='docs/provenance/archive.json')
    parser.add_argument('--output',default='evidence/export-check.json')
    args=parser.parse_args()
    downloads=Path(args.downloads).resolve();checks=json.loads(Path(args.evidence).read_text(encoding='utf-8'))
    template=(STATIC/'portable.py').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page()
        page.goto(args.base_url+'/lab/choice?manual=1')
        for row in checks['pages']:
            file=downloads/(row['page']+'.py')
            if not file.exists():file=downloads/('strata-'+row['page']+'-example.py')
            captured=runpy.run_path(str(file),run_name='test_example')['CAPTURED']
            calculator=captured['lesson'].get('calculator','lesson_math')
            assert calculator in ('lesson_math','applied_math')
            code=(STATIC/(calculator+'.py')).read_text(encoding='utf-8')
            result=page.evaluate("async args=>(await import('/static/request-panel.js')).buildPython(...args)",[template,code,captured])
            assert hashlib.sha256(result.encode()).hexdigest()==row['python_sha256'],row['page']
        captured['marker_test']={'text':'# __LESSON_CODE__ # __CAPTURED_DATA__ $& $` $\' \' " \\ \n🧪\u2028end',
                                'looks_like_code':"__import__('os').system('MUST_REMAIN_TEXT')",'bool':True,'null':None}
        result=page.evaluate("async args=>(await import('/static/request-panel.js')).buildPython(...args)",[template,code,captured])
        tree=ast.parse(result)
        actual=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CAPTURED' for t in n.targets))
        assert actual==captured
        with page.expect_download() as dl:page.locator('a[download]').click()
        expected=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
        assert hashlib.sha256(Path(dl.value.path()).read_bytes()).hexdigest()==expected['sha256']
        browser.close()
    result=dict(assembled_files_unchanged=len(checks['pages']),user_text_markers_not_replaced=True,
                python_ast_literal_round_trip=True,archive_http_download_sha256=expected['sha256'])
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_bytes(json.dumps(result,indent=2).encode());print(json.dumps(result))


if __name__=='__main__':main()
