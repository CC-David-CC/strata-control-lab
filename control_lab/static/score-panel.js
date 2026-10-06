import {rawTokenMarkup} from './token-chip.js';
const esc = value => String(value ?? '').replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const json = value => `<pre>${esc(JSON.stringify(value, null, 2))}</pre>`;
const rows = call => (call.response?.choices?.[0]?.logprobs?.content || []);

export function clearScorePanel(target) { target.hidden = true; target.replaceChildren(); }

export function renderScorePanel(page, snapshot, target, inspectRequest) {
  const view = page.score_view;
  target.hidden = false;
  target.dataset.page = page.id;
  target.dataset.rawKind = view.raw_kind;
  target.innerHTML = `<span class="eyebrow">SOURCE / TRANSFORMATION</span><h2>Raw layer / Derived view</h2><div class="score-explanations"><div><h3>Raw layer</h3><p id="score-raw-meaning">${esc(view.raw)}</p></div><div><h3>This page's derived view</h3><p id="score-derived-meaning">${esc(view.derived)}</p></div></div><p class="subtle">${esc(view.scope)}</p><div id="score-source"></div>`;
  const into = target.querySelector('#score-source'), calls = snapshot.receipt.calls;
  if (!calls.length) {
    const emitted = view.raw_kind === 'diagnostic' ? snapshot.result.oracle?.example_rejection?.emitted : null;
    target.dataset.scoreState = emitted?.length ? 'diagnostic' : view.raw_kind;
    into.innerHTML = emitted?.length
      ? `<p class="subtle">Retained target outputs from the existing diagnostic window. Labels below are token IDs; no text or bytes are invented.</p><div class="token-strip">${emitted.map(t => `<span class="token">${rawTokenMarkup({token:'target token ID '+t.token_id,logprob:t.logprob})}</span>`).join('')}</div><details><summary>Exact diagnostic emitted records</summary>${json(emitted)}</details>`
      : `<p class="score-availability">No native Chat token-probability row is present in this run. ${view.raw_kind === 'synthetic' ? 'The sandbox labels its synthetic before/after distributions separately.' : 'The page explains the actual source and units above.'}</p>`;
    return;
  }
  target.dataset.scoreState = 'requests';
  into.innerHTML = `<label class="field"><span>Original request and prefix</span><select id="score-call" aria-label="Raw score request">${calls.map((call,i) => `<option value="${i}">Request ${i+1} · ${rows(call).length} scored answer tokens${call.request.grammar ? ' · grammar' : ''}${call.request.strata_sampler ? ' · sampler' : ''}</option>`).join('')}</select></label><div id="score-call-view"></div>`;
  const select = target.querySelector('#score-call');
  select.value = String(Math.max(0,calls.findIndex(call => rows(call).length)));
  const draw = () => {
    const index = Number(select.value), call = calls[index], tokens = rows(call);
    inspectRequest(index);
    const panel = target.querySelector('#score-call-view');
    panel.innerHTML = `<p class="subtle">${esc(call.provenance)} · ${snapshot.receipt.mode === 'recorded' ? 'original native recording; no new inference' : 'this live HTTP request'} · raw p = exp(raw ln p), with no new normalization.</p>`;
    if (!tokens.length) {
      panel.insertAdjacentHTML('beforeend','<p class="score-availability">This request returned no scored answer tokens. Unscored output, reasoning and tool envelopes do not acquire invented probabilities.</p>');
      return;
    }
    panel.insertAdjacentHTML('beforeend',`<div class="token-strip">${tokens.map((token,i) => `<button type="button" class="token" data-score-token="${i}">${rawTokenMarkup(token)}</button>`).join('')}</div><div id="score-token-details"></div>`);
    const detail = panel.querySelector('#score-token-details');
    const tokenAt = i => {
      const token = tokens[i], sampling = token.strata_sampling;
      panel.querySelectorAll('[data-score-token]').forEach(b => b.classList.toggle('selected',Number(b.dataset.scoreToken) === i));
      detail.innerHTML = `<p class="subtle">Native token ${i} · original bytes ${esc(JSON.stringify(token.bytes))} · raw ln p ${esc(token.logprob)}</p>${sampling ? `<p class="score-selection-weight"><b>Final native selection weight q:</b> ${esc(sampling.probability)}. This is after the requested operators and grammar, separate from raw p.</p>` : '<p class="subtle">This response has no native sampler-weight inspection. Greedy selection or a grammar alone does not supply a returned q.</p>'}<details><summary>Exact original token and alternatives</summary>${json(token)}</details><p class="subtle">Reported top-N alternatives may omit mass. They are not automatically the complete candidate set used by this page's derived view.</p>`;
    };
    panel.querySelectorAll('[data-score-token]').forEach(b => b.onclick = () => tokenAt(Number(b.dataset.scoreToken)));
    tokenAt(0);
  };
  select.onchange = draw;
  draw();
}
