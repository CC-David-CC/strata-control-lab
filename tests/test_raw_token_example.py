"""Check the supplemental client against unchanged native receipts and byte boundaries."""
import math
import socket

import pytest

from tools.inspect_raw_logprobs import DATA, collect_stream, inspect, recorded_reply
import json


@pytest.mark.parametrize('case', ['decision', 'grammar', 'stream', 'selected-only'])
def test_example_replays_original_native_tokens_without_network(case, monkeypatch):
    monkeypatch.setattr(socket.socket, 'connect', lambda *args: pytest.fail('Offline example attempted HTTP'))
    body = json.loads((DATA/'requests'/(case+'.json')).read_text(encoding='utf-8'))
    reply, _ = recorded_reply(body)
    result = inspect(reply)
    assert result['tokens'] is reply['choices'][0]['logprobs']['content']
    assert result['raw_path_logprob'] == math.fsum(row['logprob'] for row in result['tokens'])


def test_forced_z_keeps_small_raw_probability_outside_topn():
    body = json.loads((DATA/'requests/grammar.json').read_text(encoding='utf-8'))
    reply, _ = recorded_reply(body)
    token = inspect(reply)['tokens'][0]
    assert token['token'] == 'Z' and token['logprob'] < -16
    assert all(row['token'] != 'Z' for row in token['top_logprobs'])


def test_missing_labels_stay_unknown_and_are_not_normalized():
    body = json.loads((DATA/'requests/selected-only.json').read_text(encoding='utf-8'))
    result = inspect(recorded_reply(body)[0])
    assert result['missing_labels'] == ['B']
    assert 'label_weights' not in result


def test_stream_collector_keeps_utf8_fragments_attached_to_native_tokens():
    first = dict(token='\ufffd', bytes=[195], logprob=-1, top_logprobs=[])
    second = dict(token='\ufffd', bytes=[169], logprob=-2, top_logprobs=[])
    chunks = [dict(choices=[dict(delta={}, logprobs={'content': [first]})]),
              dict(choices=[dict(delta={'content': 'é'}, logprobs={'content': [second]}, finish_reason='length')])]
    result = inspect(collect_stream(chunks))
    assert result['tokens'] == [first, second]
    assert result['raw_path_logprob'] == -3


def test_label_conditioning_handles_tiny_raw_mass_without_underflow():
    token = dict(token='A', bytes=[65], logprob=-1001, top_logprobs=[
        dict(token='B', bytes=[66], logprob=-1000)])
    result = inspect({'choices': [dict(message={'content': 'A'}, logprobs={'content': [token]})]})
    assert result['label_weights']['A'] == pytest.approx(.26894142137)
    assert result['label_mass'] == 0  # Floating-point display underflow, not absent scores.
