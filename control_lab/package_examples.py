"""Package the exact portable files qualified by check_quality or check_windowshop."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads',required=True)
    parser.add_argument('--evidence',default='evidence/quality/browser/results.json')
    parser.add_argument('--output',default='evidence/strata-control-lab-offline-examples.zip')
    parser.add_argument('--manifest',default='evidence/quality/archive.json')
    args=parser.parse_args();checks=json.loads(Path(args.evidence).read_text(encoding='utf-8'))
    if not checks.get('loop_closed'):raise ValueError('Only a completed, closed-loop qualification may be packaged')
    rows=checks['pages'];source=Path(args.downloads);destination=Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    Path(args.manifest).parent.mkdir(parents=True,exist_ok=True)
    names=[r['page'] for r in rows]
    if len(names)!=len(set(names)):raise ValueError('Duplicate page in qualification')
    readme=f'''STRATA CONTROL LAB — {len(rows)} PORTABLE EXAMPLES

Python 3 standard library only. No server, GPU, credentials, packages or network
is needed. Each file includes the exact requests, GBNF/JSON/sampler settings,
recorded replies, page inputs and the calculation from its question/rule/result
panel. Every calculation was run with network operations blocked.

Windows PowerShell:
  py .\\strata-choice-example.py
  py .\\strata-pressure-example.py --lesson-only --value 1

Ubuntu / Linux:
  python3 ./strata-choice-example.py
  python3 ./strata-pressure-example.py --lesson-only --value 1

Inspect a request:  python strata-scene-example.py --request 1 --show
Replay every mock: python strata-samplers-example.py --all
Save calculation:  python strata-circuit-example.py --lesson-only --output result.json

The default reproduces the starting compact panel. --lesson-only omits verbose
mock responses. --value changes that panel's named, bounded parameter. The script
prints its meaning, valid range, result and limitations. Python contains the
actual arithmetic: this is more than printing a cached conclusion.

Changing a parameter recalculates saved measurements, not new model inference.
Other page sliders and the saved multi-step trace are independent views. A
request edit needs a matching new fixture or an explicit live request. Analytical
pages say when no HTTP request, GBNF or JSON constraint was used.

ONE explicit live request to a compatible Strata server:
  python strata-pressure-example.py --request 1 --live-url http://127.0.0.1:8080
STRATA_API_KEY may supply your configured key; no key is embedded here. --live-url
cannot be combined with --all, --value or --lesson-only. A live selected request
does not run an adaptive controller or recompute the saved page result. No client
tool or shell command is executed. Broken/error SSE streams fail visibly.

The website's Download Python + mocks button captures its currently selected
compact panel. This archive contains the tested starting views. Native receipts
remain distinct from synthetic inputs and user-controlled assumptions. UI motion
illustrates the algorithm; it is not GPU telemetry.

Qualification: {args.evidence}
Rubric: docs/CONTROL_LAB_QUALITY_RUBRIC.md (v1, frozen before grading).
'''
    manifest=[]
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        def add(name,data):
            info=zipfile.ZipInfo(name,date_time=(2026,10,4,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        add('README.txt',readme.encode('utf-8'))
        for row in rows:
            data=(source/(row['page']+'.py')).read_bytes();digest=hashlib.sha256(data).hexdigest()
            if digest!=row['python_sha256']:raise ValueError('Qualified script changed: '+row['page'])
            name='strata-'+row['page']+'-example.py';add(name,data)
            manifest.append(dict(file=name,sha256=digest,bytes=len(data)))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None or len(archive.namelist())!=len(rows)+1:raise ValueError('Archive integrity failure')
    result=dict(archive=destination.as_posix(),sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),bytes=destination.stat().st_size,files=manifest)
    Path(args.manifest).write_bytes(json.dumps(result,indent=2).encode())
    print(json.dumps(dict(archive=result['archive'],bytes=result['bytes'],examples=len(rows))))


if __name__=='__main__':main()
