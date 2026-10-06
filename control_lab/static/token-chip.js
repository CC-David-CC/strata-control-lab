// Display the score already carried by the native token; never rescore its text.
const esc = value => String(value ?? '').replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function rawTokenMarkup(token) {
  const text = String(token.token ?? '').replace(/\n/g, '↵').replace(/\t/g, '⇥');
  const valid = typeof token.logprob === 'number' && Number.isFinite(token.logprob);
  const full = valid ? String(token.logprob) : '';
  const shown = valid ? token.logprob.toPrecision(6) : 'not returned';
  const p = valid ? Math.exp(token.logprob) : null;
  const probability = p === null ? 'not returned' : p === 0 ? 'underflows; use ln p' : p.toPrecision(6);
  return `<span class="token-text">${esc(text)}</span><small class="token-logprob" data-logprob="${esc(full)}" title="Raw target log-probability: ${esc(full || 'not returned')}">raw ln p ${esc(shown)}</small><small class="token-probability" data-probability="${p === null ? '' : p}">raw p ${esc(probability)}</small>`;
}
