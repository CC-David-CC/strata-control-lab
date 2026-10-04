import {esc,n,pct,info,details,stats,bars,shell,bind} from './instrument-ui.js';

export function render(data,target){
 shell(target,'A microscope that hunts its own blind spots',
  'Code knows when two calculations mean the same thing. We measure how much the model notices.',
  ['Equivalent math, different measurements','Different truth, similar measurements','Different math, identical chosen properties'],
  {name:'Illustrate exact evaluation at integer x',min:-4,max:4,step:1,value:2});
 let chosen=0,previous=-1;
 const draw=(index,x,view)=>{
  if(previous!==index){chosen=0;previous=index;}
  const key=['equivalent','distinct','collision'][index],rank=data.rankings[key],pair=rank[chosen]??rank[0],a=data.nodes[pair.left],b=data.nodes[pair.right];
  const value=node=>node.coefficients.reduce((v,c,i)=>v+c*x**i,0);
  const positions=data.nodes.map((_,i)=>[80+(i%4)*145,45+Math.floor(i/4)*83]);
  view.innerHTML=`<div class="instrument-equation">${esc(a.expression)} <span aria-label="comparison">${pair.equivalent?'≡':'≢'}</span> ${esc(b.expression)}<br><small>${pair.equivalent?'Exactly equivalent for every integer x':'Distinct integer polynomials; a verified counterexample exists'}</small></div>
  <svg class="instrument-network" viewBox="0 0 600 255" role="img" aria-label="Expression graph: controlled transformations join exact source expressions">
   ${data.edges.map(e=>{const [x1,y1]=positions[e.left],[x2,y2]=positions[e.right];return `<path d="M${x1} ${y1}L${x2} ${y2}" fill="none" stroke="${e.equivalent?'#76a764':'#c89463'}" stroke-width="1.5" stroke-dasharray="${e.equivalent?'none':'3 4'}"/>`;}).join('')}
   <path class="signal" d="M${positions[a.id].join(' ')}L${positions[b.id].join(' ')}" fill="none" stroke="#d9f8b0" stroke-width="4"/>
   ${data.nodes.map(node=>{const [cx,cy]=positions[node.id],active=[a.id,b.id].includes(node.id);return `<g><title>${esc(node.expression)}</title><circle cx="${cx}" cy="${cy}" r="${active?21:17}" fill="${active?'#9ec272':'#435b41'}"/><text x="${cx}" y="${cy+4}" text-anchor="middle">E${node.id}</text></g>`;}).join('')}
  </svg>${info('Solid edges preserve the exact polynomial. Dashed edges change it. The bright moving edge is the inspected pair; motion illustrates a comparison, not GPU activity.')}
  ${stats([['Observer distance ‖Δ log-odds‖₂',n(pair.margin_distance)],['Mean binary JS (nats)',n(pair.mean_binary_js_nats,5)],['At x = '+x,value(a)+' versus '+value(b)]])}
  <div class="instrument-grid">${[a,b].map(node=>`<div class="instrument-tile"><h4>E${node.id}: ${esc(node.expression)}</h4>${bars(['Equal to x for all integers','Always nonnegative'],node.p_yes)}<p>Exact answers: ${node.truth.map(v=>v?'yes':'no').join(' / ')}</p><p>Canonical [constant, x, x²]: [${node.coefficients.join(', ')}]</p></div>`).join('')}</div>
  ${info(index===0?'Search objective: keep the exact meaning fixed, maximize movement of the semantic observer. The measurements can be unstable even when the selected yes/no label stays the same.':index===1?'Search objective: find a verified change in at least one measured property that the observer barely separates. A low distance is a candidate test case, not proof of miscalibration.':'Information-loss control: both expressions have the same two exact properties. Even a perfect observer for these questions need not distinguish them. Add a probe before blaming the model.')}
  ${pair.witness?info('Exact distinctness witness: at x='+pair.witness.x+', left='+pair.witness.left+' and right='+pair.witness.right+'. The slider may show another x where they happen to coincide.'):info('Equivalence proof: identical integer coefficients, not agreement on a few slider values.')}
  <h4>Search the finite grammar bank</h4><div class="wide-scroll"><table class="instrument-table"><thead><tr><th>Inspect</th><th>Left → right</th><th>Distance</th><th>Mean JS</th></tr></thead><tbody>${rank.slice(0,8).map((p,i)=>`<tr><td><button class="secondary" data-pair="${i}" aria-pressed="${i===chosen}">Pair ${i+1}</button></td><td>E${p.left} → E${p.right}</td><td>${n(p.margin_distance)}</td><td>${n(p.mean_binary_js_nats,5)}</td></tr>`).join('')}</tbody></table></div>
  ${details('Inspect this pair: unchanged source, algebra and every native measurement',{left:a,right:b,comparison:pair})}
  ${details('Native grammar emission, graph and exportable training-pair references',data)}${info(data.semantics)}`;
  view.querySelectorAll('[data-pair]').forEach(button=>button.onclick=()=>{chosen=+button.dataset.pair;draw(index,x,view);});
 };
 bind(draw);
}
