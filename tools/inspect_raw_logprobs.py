"""Show original token scores and A/B conditioning; replay native receipts by default.

Standard library only. Run from a source checkout. --live-url explicitly enables HTTP.
The existing 39 portable examples and all bundled recordings are left unchanged.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from urllib.request import Request, urlopen

DATA = Path(__file__).resolve().parents[1] / 'control_lab' / 'data'


def recorded_reply(body):
    key = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                   separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    paths = sorted((DATA / 'recordings').glob('*/' + key + '-*.json'))
    if not paths:
        raise ValueError('No exact native recording for this request')
    record = json.loads(paths[0].read_text(encoding='utf-8'))
    if record['request'] != body or record.get('provenance') != 'native-strata':
        raise ValueError('Recording provenance or request differs')
    return record['response'], str(paths[0].relative_to(DATA))


def collect_stream(chunks):
    text, entries, finish = '', [], None
    for chunk in chunks:
        if 'error' in chunk:
            raise ValueError(str(chunk['error']))
        for choice in chunk.get('choices', []):
            text += (choice.get('delta') or {}).get('content') or ''
            entries.extend((choice.get('logprobs') or {}).get('content') or [])
            finish = choice.get('finish_reason') or finish
    if finish is None:
        raise ValueError('Stream ended without a terminal choice')
    return {'choices': [{'message': {'content': text}, 'finish_reason': finish,
                         'logprobs': {'content': entries}}]}


def live_reply(body, url):
    headers = {'Content-Type': 'application/json'}
    if os.environ.get('STRATA_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['STRATA_API_KEY']
    req = Request(url.rstrip('/') + '/v1/chat/completions',
                  data=json.dumps(body).encode(), headers=headers)
    with urlopen(req, timeout=600) as response:
        if not body.get('stream'):
            return json.load(response)
        chunks = []
        done = False
        for raw in response:
            line = raw.decode('utf-8').strip()
            if not line.startswith('data:'):
                continue
            value = line[5:].strip()
            if value == '[DONE]':
                done = True
                break
            chunks.append(json.loads(value))
        if not done:
            raise ValueError('Stream ended without [DONE]')
        return collect_stream(chunks)


def inspect(reply, labels=('A', 'B')):
    choice = reply['choices'][0]
    entries = (choice.get('logprobs') or {}).get('content')
    if not entries:
        raise ValueError('No token logprobs: build and serve the compatible native Strata branch')
    text = choice['message'].get('content') or ''
    if bytes(b for row in entries for b in row['bytes']) != text.encode('utf-8'):
        raise ValueError('Token bytes do not reproduce the original answer')
    for row in entries:
        if not math.isfinite(row['logprob']) or row['logprob'] > 0:
            raise ValueError('Invalid raw token logprob')
    first = entries[0]
    available = {bytes(row['bytes']): row['logprob'] for row in first['top_logprobs']
                 if row.get('bytes') is not None}
    available[bytes(first['bytes'])] = first['logprob']
    values = {label: available.get(label.encode('utf-8')) for label in labels}
    missing = [label for label, value in values.items() if value is None]
    total = math.fsum(row['logprob'] for row in entries)
    result = dict(tokens=entries, raw_path_logprob=total, raw_path_probability=math.exp(total),
                  label_raw_logprobs=values, missing_labels=missing)
    if not missing:
        peak = max(values.values())
        normalizer = math.fsum(math.exp(lp - peak) for lp in values.values())
        result['label_weights'] = {label: math.exp(lp - peak) / normalizer
                                   for label, lp in values.items()}
        result['label_mass'] = math.fsum(math.exp(lp) for lp in values.values())
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case', choices=['decision', 'grammar', 'stream', 'selected-only'], default='decision')
    ap.add_argument('--live-url', help='Explicitly call a compatible Strata server instead of replay')
    ap.add_argument('--json', action='store_true', help='Include unchanged original token objects')
    args = ap.parse_args()
    body = json.loads((DATA / 'requests' / (args.case + '.json')).read_text(encoding='utf-8'))
    if args.live_url:
        reply, source = live_reply(body, args.live_url), 'fresh HTTP request to ' + args.live_url
    else:
        reply, path = recorded_reply(body)
        source = 'recorded native Strata receipt: ' + path
    result = inspect(reply)
    if args.json:
        print(json.dumps(dict(source=source, request=body, **result), ensure_ascii=False, indent=2))
        return
    print(source)
    for i, row in enumerate(result['tokens']):
        print(f"token {i}: {row['token']!r} bytes={row['bytes']} raw ln p={row['logprob']:.17g} p={math.exp(row['logprob']):.9g}")
    print('First target row, exact label bytes:')
    for label, lp in result['label_raw_logprobs'].items():
        print(f'  {label}: unknown (outside returned scores)' if lp is None
              else f'  {label}: raw ln p={lp:.17g} p={math.exp(lp):.9g}')
    if 'label_weights' in result:
        print('Lab conditional A/B weights:', result['label_weights'])
        print('Raw mass on those exact labels:', result['label_mass'])
    else:
        print('No complete label distribution; missing labels stay unknown.')
    print('Raw scores precede temperature and grammar. Label weights are a separate calculation, not calibrated truth.')


if __name__ == '__main__':
    main()
