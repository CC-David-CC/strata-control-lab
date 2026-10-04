"""Run a trusted Control Lab Python archive with socket operations blocked.

Python standard library only. Works on Windows and Linux without the website.
This executes the Python files in the supplied archive; use your own lab export.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tempfile
import zipfile


def equivalent(a,b):
    if type(a) is bool or type(b) is bool:return type(a) is type(b) and a==b
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):
        return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
    if isinstance(a,dict) and isinstance(b,dict):
        return a.keys()==b.keys() and all(equivalent(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):
        return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    return a==b


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();rows=[];system=platform.platform()
    def block_socket(event,_):
        if event.startswith('socket.'):raise AssertionError('Offline check attempted networking')
    sys.addaudithook(block_socket)
    with tempfile.TemporaryDirectory(prefix='strata-verified-portable-') as directory:
        root=Path(directory)
        with zipfile.ZipFile(args.archive) as archive:
            assert archive.testzip() is None
            names=[n for n in archive.namelist() if n.endswith('.py')]
            assert names and len(names)==len(set(names))
            for name in names:
                assert Path(name).name==name and name.startswith('strata-')
                (root/name).write_bytes(archive.read(name))
        for name in names:
            file=root/name;captured=runpy.run_path(str(file),run_name='inspect_example')['CAPTURED']
            commands=[['--all']]+[['--lesson-only','--value',str(s['value'])] for s in captured['lesson']['states']]
            for i,options in enumerate(commands):
                output=root/'result.json';argv=[str(file),*options,'--output',str(output)]
                script="import sys,runpy\ndef audit(event,args):\n if event.startswith('socket.'): raise AssertionError('Offline example attempted networking')\nsys.addaudithook(audit)\nsys.argv="+repr(argv)+"\nrunpy.run_path("+repr(str(file))+",run_name='__main__')"
                result=subprocess.run([sys.executable,'-I','-c',script],capture_output=True,encoding='utf-8',timeout=60)
                assert result.returncode==0,(name,options,result.stdout,result.stderr)
                actual=json.loads(output.read_text(encoding='utf-8'))
                if i:
                    assert equivalent(actual['calculation'],captured['lesson']['states'][i-1]),(name,options)
                elif captured['receipt']['calls']:
                    for key in ('request','response'):
                        assert [c[key] for c in actual['calls']]==[c[key] for c in captured['receipt']['calls']]
                else:
                    assert actual['mode']=='offline-snapshot' and actual['result']==captured['result']
            rows.append(dict(page=captured['experiment'],mock_calls=len(captured['receipt']['calls']),
                             calculations=len(commands)-1,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    receipt=dict(platform=system,python=sys.version,network_blocked=True,
                 archive_sha256=hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                 calculation_tolerance=dict(relative=1e-12,absolute=1e-12),pages=rows)
    args.output.write_bytes(json.dumps(receipt,indent=2).encode())
    print(json.dumps(dict(pages=len(rows),calculations=sum(r['calculations'] for r in rows),
                         mock_calls=sum(r['mock_calls'] for r in rows),network_blocked=True)))


if __name__=='__main__':main()
