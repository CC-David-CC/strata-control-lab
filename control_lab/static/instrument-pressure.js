import {rawTokenMarkup} from './token-chip.js';
import {esc,$,n,pct,info,details,stats,bars,shell,bind} from './instrument-ui.js';
export function render(data,target){
 shell(target,'The cost of a boundary','A confident-looking constrained answer can hide a strong intervention.',
  ['Synthetic: identical 60/40 answers',...data.cases.map(c=>c.name)],{name:'Pressure dial / native token position',min:0,max:100,step:1,value:50});
 bind((index,dial,view)=>{
  if(index===0){
   const z=Math.pow(10,-dial/25),c=-Math.log(z);
   view.innerHTML=`<div class="instrument-grid"><div class="instrument-tile"><h4>Most of the original mass fits</h4><b class="big">99%</b><div class="mass-bar"><i style="width:99%"></i></div>${bars(['A','B'],[.6,.4])}<p>Raw A = 0.594 · raw B = 0.396<br>Pressure = ${n(-Math.log(.99))} nats</p></div><div class="instrument-tile"><h4>Your counterfactual boundary</h4><b class="big">${pct(z)}</b><div class="mass-bar"><i style="width:${100*z}%"></i></div>${bars(['A','B'],[.6,.4])}<p>Raw A = ${n(z*.6,6)} · raw B = ${n(z*.4,6)}<br>Pressure = ${n(c)} nats</p></div></div><div class="instrument-equation">q(A) = 60%, q(B) = 40% in both cases.<br>KL(q || p) = −log Z = ${n(c)} nats on the right.</div>${info('Synthetic teaching distribution. The dial changes surviving raw mass, while preserving the conditional answer ratio. Select a native grammar to inspect measured values.')}`;
  }else{
   const c=data.cases[index-1],at=Math.round(dial/100*(c.rows.length-1)),r=c.rows[at];
   view.innerHTML=`<div class="grammar-slate"><span>ACTUAL NATIVE GRAMMAR</span><code>${esc(c.grammar)}</code></div><pre class="generated-answer">${esc(c.text)}</pre><div class="token-strip">${c.rows.map((x,i)=>`<button class="instrument-token ${i===at?'active':''}" data-position="${i}">${rawTokenMarkup(x.token)}</button>`).join('')}</div>${stats([['Raw mass surviving',pct(r.mass)],['Grammar pressure',n(r.pressure_nats)+' nats'],['Legal native tokens',r.support]])}<div class="mass-bar"><i style="width:${100*r.mass}%"></i></div><div class="instrument-grid"><div class="instrument-tile"><h4>Before masking</h4><b class="big">${pct(Math.exp(r.selected_raw_logprob))}</b><p>Probability of the selected token in the full vocabulary.</p></div><div class="instrument-tile"><h4>After pure masking</h4><b class="big">${pct(r.selected_probability)}</b><p>Its probability among all native grammar-permitted tokens.</p></div></div><div class="instrument-equation">log Z = ${n(r.selected_raw_logprob,7)} − log(${n(r.selected_probability,7)})<br>prefix = ${esc(JSON.stringify(r.prefix))}<br>pressure = ${n(r.pressure_bits)} bits</div>${details('Exact token, native stages and recovered mass',r)}${info(data.semantics)}`;
   view.querySelectorAll('[data-position]').forEach(b=>b.onclick=()=>{$('dial').value=c.rows.length===1?0:Math.round(+b.dataset.position/(c.rows.length-1)*100);$('dial').dispatchEvent(new Event('input'));});
  }
 });
}
