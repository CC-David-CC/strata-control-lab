import {esc,n,pct,info,details,stats,bars,shell,bind,softmax,line} from './instrument-ui.js';
function mix(b,e,a,alpha,allowed){const scores=allowed.map(i=>Math.log(b[i])+alpha*(Math.log(e[i])-Math.log(a[i]))),values=softmax(scores),q=b.map(()=>0);allowed.forEach((i,k)=>q[i]=values[k]);return q;}
export function render(data,target){
 shell(target,'A measurable direction through preference space','Control changes the ranking inside the boundary. It cannot make the forbidden action legal.',
 ['Native: same-model prompt contrast','Synthetic: an obvious rank reversal'],{name:'Control strength α',min:0,max:3,step:.05,value:1});
 bind((index,alpha,view)=>{
  const v=index?data.hypothetical:data,q=mix(v.base,v.desired,v.undesired,alpha,data.allowed),ratios=v.base.map((_,i)=>Math.log(v.desired[i])-Math.log(v.undesired[i]));
  const pick=data.allowed.reduce((best,i)=>q[i]>q[best]?i:best,data.allowed[0]);
  const sweep=Array.from({length:31},(_,i)=>mix(v.base,v.desired,v.undesired,i/10,data.allowed)[0]);
  const committed=!index?data.commits.find(c=>Math.abs(c.alpha-alpha)<1e-8):null;
  view.innerHTML=`<div class="instrument-callout"><span class="instrument-label">FINITE-ACTION DECODER CHOICE</span><h3>${esc(data.actions[pick])}</h3><p>${committed?'Native GBNF commitment exists at this alpha.':'Counterfactual arithmetic preview; no new model call.'}</p></div><div class="instrument-grid"><div class="instrument-tile"><h4>Original action preferences</h4>${bars(data.actions,v.base)}</div><div class="instrument-tile"><h4>After contrast + hard permission</h4>${bars(data.actions,q)}</div></div><div class="instrument-equation">sᵢ = log p_base(i) + α [log p_desired(i) − log p_undesired(i)]<br>qᵢ = softmax(s) over legal actions only</div><table class="instrument-table"><thead><tr><th>Action</th><th>Expert / anti log-ratio</th><th>Permission</th></tr></thead><tbody>${data.actions.map((a,i)=>`<tr class="${i===pick?'active':''}"><td>${esc(a)}</td><td>${n(ratios[i])}</td><td>${data.allowed.includes(i)?'legal':'blocked for every α'}</td></tr>`).join('')}</tbody></table><h4>Weight on the minimal edit as α moves from 0 to 3</h4>${line(sweep)}${stats([['Selected weight',pct(q[pick])],['Forbidden action weight',pct(q[2])]])}${details('Exact distributions and any native commitment',{base:v.base,desired:v.desired,undesired:v.undesired,alpha,combined:q,native_commitment:committed})}${info(data.semantics)}`;
 });
}
