"""Downloaded Strata example: Python 3 standard library; offline by default.

Windows: py strata-example.py
Ubuntu:  python3 strata-example.py
Show a request: python strata-example.py --request 1 --show
Replay all recorded calls: python strata-example.py --all
Recalculate the panel: python strata-example.py --lesson-only
Change its knob: python strata-example.py --lesson-only --value NUMBER
Try ONE request live: python strata-example.py --request 1 --live-url http://127.0.0.1:8080
An optional STRATA_API_KEY environment variable supplies authentication.

CAPTURED is inserted above this runner by the page. It contains this exact run,
with requests, GBNF/JSON settings, responses, streaming chunks and the page result.
Mock mode returns those responses; it performs no inference and opens no socket.
Live mode runs only a selected request. It does not execute tools or adapt a saved
multi-step trace to new answers. No captured API key or authorization header exists.
"""
# __CAPTURED_DATA__
import argparse
import copy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
import urllib.error
import urllib.request

# __LESSON_CODE__


def mock_post(request, fixture):
    if request != fixture['request']:
        raise ValueError('No mock matches the edited request. Supply a new fixture or explicitly choose --live-url.')
    return copy.deepcopy(fixture['response'])


def live_post(base_url, request):
    if not base_url.startswith(('http://', 'https://')):
        raise ValueError('--live-url must be an http(s) Strata address')
    headers = {'Content-Type': 'application/json'}
    if os.environ.get('STRATA_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['STRATA_API_KEY']
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    body = json.dumps(request, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(base_url.rstrip('/')+'/v1/chat/completions', data=body, headers=headers)
    with opener.open(req, timeout=600) as response:
        wire = response.read().decode('utf-8')
    if request.get('stream'):
        events = [line[5:].strip() for line in wire.splitlines() if line.startswith('data:')]
        if not events or events[-1] != '[DONE]':
            raise ValueError('Stream closed without [DONE]')
        chunks = [json.loads(line) for line in events[:-1]]
        if any('error' in chunk for chunk in chunks):
            raise ValueError('Stream reported an error: '+repr(chunks))
        return {'sse_events': chunks, 'wire': wire}
    reply = json.loads(wire)
    if 'error' in reply:
        raise ValueError('Strata reported an error: '+repr(reply['error']))
    return reply


def summarize(response):
    if 'sse_events' in response:
        return str(len(response['sse_events']))+' SSE events; inspect the saved wire response'
    choice = (response.get('choices') or [{}])[0]
    message = choice.get('message', {})
    text = message.get('content') or json.dumps(message.get('tool_calls') or message, ensure_ascii=False)
    entries = (choice.get('logprobs') or {}).get('content') or []
    if entries:
        text += '\n  First visible token raw probability: '+format(math.exp(entries[0]['logprob']), '.7g')
    return text


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=int, default=1, help='1-based request index (default 1)')
    parser.add_argument('--all', action='store_true', help='Replay every mock in this captured run')
    parser.add_argument('--show', action='store_true', help='Print exact selected HTTP request JSON')
    parser.add_argument('--lesson-only', action='store_true', help='Recalculate the captured question/rule/result panel without printing mocked calls')
    parser.add_argument('--value', type=float, help='Change the panel parameter within its documented bounds; offline calculation only')
    parser.add_argument('--live-url', help='Explicitly send ONE request to your compatible Strata server')
    parser.add_argument('--output', type=Path, help='Write responses and their provenance as JSON')
    args = parser.parse_args()
    if args.all and args.live_url:
        parser.error('--all is offline only; saved dependent requests are not a live adaptive controller')
    if args.live_url and (args.lesson_only or args.value is not None):
        parser.error('Lesson calculations use captured evidence. Do not mix --live-url with --lesson-only or --value.')
    calls = CAPTURED['receipt']['calls']
    print('Strata Control Lab / '+CAPTURED['experiment'])
    print('LIVE selected request' if args.live_url else 'OFFLINE MOCK / recorded responses, no inference or network')
    calculation=None
    if not args.live_url:
        spec=CAPTURED.get('lesson')
        if spec and spec.get('states'):
            knob=args.value if args.value is not None else (CAPTURED.get('lesson_view') or {}).get('value',spec['default'])
            try:calculation=calculate_lesson(CAPTURED['experiment'],CAPTURED['result'],knob)
            except (ValueError,KeyError,IndexError,ZeroDivisionError) as error:parser.error(str(error))
            print('\nQUESTION: '+spec['question']+'\nRULE: '+spec['rule'])
            print(spec['knob']+' = '+str(knob)+f" (allowed {spec['low']}..{spec['high']})")
            print('RESULT: '+calculation['summary'])
            print('BOUNDARY: '+calculation['note'])
            print('Reproduces the selected question/rule/result panel; other page dials are independent.')
            print(json.dumps(calculation,ensure_ascii=True,indent=2))
        elif args.lesson_only or args.value is not None:
            parser.error('This captured run has no complete lesson inputs: '+str((spec or {}).get('unavailable','missing calculation')))
    if args.lesson_only:
        result=dict(mode='offline-calculation',calculation=calculation)
    elif not calls:
        if args.live_url:
            parser.error('This page has no HTTP requests: it is analytical or recorded diagnostic evidence')
        print('No HTTP request, GBNF or JSON output constraint was used by this page.')
        print('The included result is a calculation/diagnostic snapshot, not a new model answer.')
        result = dict(mode='offline-snapshot', result=CAPTURED['result'])
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        indexes = range(len(calls)) if args.all else [args.request-1]
        if any(i < 0 or i >= len(calls) for i in indexes):
            parser.error('Request index must be 1..'+str(len(calls)))
        results = []
        for i in indexes:
            fixture = calls[i]
            request = copy.deepcopy(fixture['request'])  # Edit here to try your own live request.
            if args.show:
                print(json.dumps(request, ensure_ascii=True, indent=2))
            response = live_post(args.live_url, request) if args.live_url else mock_post(request, fixture)
            print('Request '+str(i+1)+' / '+str(len(calls))+': '+summarize(response))
            results.append(dict(request=request, response=response,
                                provenance='live-request' if args.live_url else 'mocked-native-recording'))
        result = dict(mode='live' if args.live_url else 'offline-mock', calls=results)
        print('GBNF and JSON settings are in each request. Use --show to inspect them.')
        print('The saved page result is in CAPTURED["result"]; live responses do not recompute that snapshot.')
    if calculation is not None:result['calculation']=calculation
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
