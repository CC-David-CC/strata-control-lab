"""Failure boundaries for the downloadable standard-library request runner."""
from control_lab.paths import STATIC
import io
import json
from pathlib import Path
import runpy
import sys
import urllib.request
import pytest

RUNNER=STATIC/'portable.py'


def test_mock_is_exact_and_does_not_mutate_its_fixture():
    module=runpy.run_path(str(RUNNER))
    fixture={'request':{'messages':[{'role':'user','content':'emoji 🧪 and "quotes"'}]},
             'response':{'choices':[{'message':{'content':'A'}}]}}
    response=module['mock_post'](fixture['request'],fixture)
    response['choices'][0]['message']['content']='mutated'
    assert fixture['response']['choices'][0]['message']['content']=='A'
    with pytest.raises(ValueError,match='No mock matches'):
        module['mock_post']({'messages':[]},fixture)


def test_explicit_live_request_preserves_schema_and_uses_environment_auth(monkeypatch):
    module=runpy.run_path(str(RUNNER));sent=[];handlers=[]
    body={'model':'x','messages':[{'role':'user','content':'hi'}],
          'response_format':{'type':'json_schema','json_schema':{'name':'answer','schema':{'type':'object'}}}}
    class Opener:
        def open(self,request,timeout):
            sent.append(request)
            assert timeout==600
            return io.BytesIO(b'{"choices": []}')
    def opener(handler):handlers.append(handler);return Opener()
    monkeypatch.setattr(urllib.request,'build_opener',opener)
    monkeypatch.setenv('STRATA_API_KEY','synthetic-test-key')
    assert module['live_post']('http://localhost:8080/',body)=={'choices':[]}
    assert json.loads(sent[0].data)==body and sent[0].full_url=='http://localhost:8080/v1/chat/completions'
    assert sent[0].get_header('Authorization')=='Bearer synthetic-test-key'
    assert handlers[0].redirect_request(None,None,None,None,None,None) is None


@pytest.mark.parametrize('wire',[
    'data: {"choices": []}\n\n',
    'data: {"error": "synthetic failure"}\n\ndata: [DONE]\n\n'])
def test_broken_live_stream_cannot_look_completed(monkeypatch,wire):
    module=runpy.run_path(str(RUNNER))
    class Opener:
        def open(self,*args,**kwargs):return io.BytesIO(wire.encode())
    monkeypatch.setattr(urllib.request,'build_opener',lambda handler:Opener())
    with pytest.raises(ValueError):module['live_post']('http://localhost:8080',{'stream':True})


def test_live_trace_is_not_misrepresented_as_an_adaptive_controller(monkeypatch):
    module=runpy.run_path(str(RUNNER))
    monkeypatch.setattr(sys,'argv',['example.py','--all','--live-url','http://localhost:8080'])
    with pytest.raises(SystemExit) as exc:module['main']()
    assert exc.value.code==2


def test_invalid_url_never_builds_a_transport(monkeypatch):
    module=runpy.run_path(str(RUNNER))
    def forbidden(*args):raise AssertionError('Must not open a transport')
    monkeypatch.setattr(urllib.request,'build_opener',forbidden)
    with pytest.raises(ValueError):module['live_post']('file:///private',{})
