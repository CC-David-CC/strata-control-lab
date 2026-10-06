"""Add an updated 39-example archive without replacing the original qualified ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import zipfile

from control_lab.catalog import PAGES


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--downloads', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=Path('control_lab/static/strata-control-lab-39-raw-score-examples.zip'))
    args = ap.parse_args()
    if args.output.exists():
        raise ValueError('Refusing to replace an existing archive')
    original = Path('control_lab/static/strata-control-lab-39-offline-examples.zip')
    original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    files, calls = [], 0
    with tempfile.TemporaryDirectory(prefix='strata-original-examples-') as tmp:
        with zipfile.ZipFile(original) as old, zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as new:
            for page in PAGES:
                name = 'strata-'+page['id']+'-example.py'
                source = (args.downloads/(page['id']+'.py')).read_bytes()
                file = Path(tmp)/name
                file.write_bytes(old.read(name))
                prior = runpy.run_path(str(file), run_name='inspect_original')['CAPTURED']
                current = runpy.run_path(str(args.downloads/(page['id']+'.py')), run_name='inspect_updated')['CAPTURED']
                assert current['score_view'] == page['score_view'], name
                for key in ['request','response']:
                    assert [c[key] for c in prior['receipt']['calls']] == [c[key] for c in current['receipt']['calls']], (name,key)
                calls += len(current['receipt']['calls'])
                info = zipfile.ZipInfo(name, date_time=(2026,10,6,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                new.writestr(info, source, compresslevel=9)
                files.append(dict(file=name,sha256=hashlib.sha256(source).hexdigest(),bytes=len(source)))
    assert hashlib.sha256(original.read_bytes()).hexdigest() == original_hash
    manifest = dict(archive=args.output.as_posix(), sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                    files=files, pages=len(files), native_calls=calls,
                    original_archive_sha256=original_hash, original_archive_unchanged=True,
                    all_original_native_requests_responses_unchanged=True)
    Path('docs/validation/raw-score-archive.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Added 39 updated examples; original archive and all native request/response pairs unchanged')


if __name__ == '__main__':
    main()
