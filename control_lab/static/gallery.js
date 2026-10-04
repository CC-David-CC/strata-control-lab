const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels={choice:'Choice',boolean:'Yes / no',score:'Rubric score',candidates:'Grammar branches',controller:'State controller',rerank:'Source ranking',graph:'Document graph',scene:'Scene search',wire:'Token inspector',speculation:'Draft & target',performance:'Latency frontier'};
let pages=[],filter='all';
const category=p=>p.applied?'applications':p.section==='instrument'?'instruments':p.section!=='research'?'foundations':['samplers','sampler-sandbox'].includes(p.id)?'sampling':['tictactoe','chess','poker','thermal','scheduler','context','observer'].includes(p.id)?'control':'research';
function art(p,i){const color=i%3===0?'#e6b58d':'#d7f39e';let shapes='';
 if(p.applied)return applicationArt(p.id,i%4);
 if(p.id==='pressure'){shapes=`<rect x="42" y="52" width="236" height="18" rx="6" fill="#e6b58d"/><rect x="42" y="52" width="229" height="18" rx="6" fill="${color}"/><rect x="42" y="96" width="236" height="18" rx="6" fill="#e6b58d"/><rect x="42" y="96" width="9" height="18" rx="3" fill="#d7f39e"/>`;}
 else if(p.id==='circuit'){for(let k=0;k<4;k++)shapes+=`<rect x="${108+k%2*55}" y="${30+Math.floor(k/2)*55}" width="47" height="47" rx="8" fill="${color}" opacity="${[.2,.2,.45,1][k]}"/>`;}
 else if(p.id==='control'){for(let k=0;k<5;k++)shapes+=`<path d="M45 ${30+k*24}C125 ${30+k*24} 175 ${140-k*28} 275 ${140-k*28}" stroke="${k===2?'#e6b58d':color}" opacity="${k===2?.25:.8}" stroke-width="2" fill="none"/>`;}
 else if(p.id==='future'){shapes=`<path d="M160 25L90 80L45 130M90 80L130 130M160 25L230 80L190 130M230 80L275 130" fill="none" stroke="${color}" stroke-width="2"/>`;[[160,25],[90,80],[230,80],[45,130],[130,130],[190,130],[275,130]].forEach(([x,y],k)=>shapes+=`<circle cx="${x}" cy="${y}" r="${k===6?12:7}" fill="${k===6?color:'#527952'}"/>`);}
 else if(p.id==='sensitivity'){for(let k=0;k<6;k++)shapes+=`<rect x="${104+k%2*58}" y="${20+Math.floor(k/2)*43}" width="50" height="35" rx="5" fill="${k%2?color:'#e6b58d'}" opacity="${.25+k*.13}"/>`;}
 else if(['tictactoe','chess','scheduler','controller'].includes(p.id)){for(let y=0;y<3;y++)for(let x=0;x<3;x++){const k=x+y*3;shapes+=`<rect x="${119+x*29}" y="${35+y*29}" width="24" height="24" rx="3" fill="${(i+k)%3===0?color:'none'}" stroke="${color}" opacity="${.3+k*.065}"/>`;}}
 else if(['thermal','frontier','performance','context'].includes(p.id)){for(let k=0;k<3;k++)shapes+=`<path d="M25 ${115-k*15} C75 ${110-k*26} 76 ${24+k*10} 122 ${63+k*12} S195 ${112-k*26} 218 ${55+k*10} S270 ${64+k*20} 297 ${28+k*10}" fill="none" stroke="${color}" opacity="${1-k*.25}" stroke-width="${k===0?2:1}"/>`;}
 else if(['samplers','sampler-sandbox','wire','choice','score','boolean'].includes(p.id)){for(let k=0;k<16;k++){const h=12+Math.exp(-Math.pow((k-7)/(3+i%3),2))*72;shapes+=`<rect x="${35+k*16}" y="${132-h}" width="9" height="${h}" rx="3" fill="${color}" opacity="${k>3&&k<11?.85:.2}"/>`;}}
 else{for(let k=0;k<7;k++){const a=k*Math.PI*2/7,cx=160+64*Math.cos(a),cy=80+49*Math.sin(a);shapes+=`<path d="M160 80 L${cx} ${cy}" stroke="${color}" opacity=".3"/><circle cx="${cx}" cy="${cy}" r="${k%2?6:10}" fill="${k%2?'#1b3b32':color}" stroke="${color}"/>`;}shapes+='<circle cx="160" cy="80" r="17" fill="#d7f39e"/>';}
 return `<svg viewBox="0 0 320 160" aria-hidden="true">${shapes}</svg>`;}
function draw(){const query=$('search').value.toLowerCase();const visible=pages.filter(p=>(filter==='all'||category(p)===filter)&&[p.name,p.id,p.title,p.simple,...p.features].join(' ').toLowerCase().includes(query));$('count-note').textContent=`${visible.length} OF ${pages.length} EXPERIMENTS`;$('empty').hidden=!!visible.length;
 $('cards').innerHTML=visible.map(p=>{const i=pages.indexOf(p);return `<a class="experiment-card" href="/lab/${p.id}"><div class="card-art"><span>${String(i+1).padStart(2,'0')} / ${esc(category(p).toUpperCase())}</span>${art(p,i)}<i>CONCEPT SKETCH</i></div><div class="card-content"><h3>${esc(p.name||labels[p.id]||p.title)}</h3><p>${esc(p.simple)}</p><div class="card-foot"><span>${p.data_kind==='analytic'?'ANALYTIC / NO INFERENCE':p.id==='speculation'?'NATIVE DIAGNOSTIC RECORDING':'RECORDED NATIVE + LIVE'}</span><b>↗</b></div></div></a>`;}).join('');}
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>{x.classList.toggle('selected',x===b);x.setAttribute('aria-pressed',x===b?'true':'false');});draw();}));$('search').addEventListener('input',draw);
try{const response=await fetch('/api/catalog');if(!response.ok)throw new Error('Catalog unavailable');const c=await response.json();pages=c.pages;$('experiment-count').textContent=pages.length;$('nav-count').textContent=pages.length;$('recording-count').textContent=c.recordings;draw();}catch(e){$('cards').textContent=e.message;}
const canvas=$('machine'),ctx=canvas.getContext('2d'),reduce=matchMedia('(prefers-reduced-motion: reduce)');let paused=reduce.matches,visible=true,raf=0,time=0,last=0;
function resize(){const dpr=Math.min(devicePixelRatio,2);canvas.width=canvas.clientWidth*dpr;canvas.height=canvas.clientHeight*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);paint();}new ResizeObserver(resize).observe(canvas);
function paint(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const middle=h*.46,xs=[w*.19,w*.5,w*.81];
 ctx.strokeStyle='#55795d45';ctx.lineWidth=1;for(let y=80;y<h-95;y+=28){ctx.beginPath();ctx.moveTo(22,y);ctx.lineTo(w-22,y);ctx.stroke();}
 for(let k=0;k<9;k++){const y=middle+(k-4)*18;ctx.beginPath();ctx.moveTo(0,y);ctx.bezierCurveTo(w*.3,y,w*.4,middle+(k-4)*7,w*.52,middle+(k-4)*7);ctx.bezierCurveTo(w*.68,middle+(k-4)*7,w*.77,middle,w,middle);ctx.strokeStyle=k<2||k>6?'#749a6230':'#b4d99255';ctx.stroke();}
 for(let i=0;i<3;i++){ctx.save();ctx.translate(xs[i],middle);ctx.rotate(i===1?time*.09:0);ctx.strokeStyle=i===1?'#def899':'#86b78a';ctx.lineWidth=i===1?2:1;const r=i===1?67:43;ctx.beginPath();ctx.arc(0,0,r,0,2*Math.PI);ctx.stroke();for(let k=0;k<24;k++){let a=k*Math.PI/12;ctx.beginPath();ctx.moveTo(Math.cos(a)*(r+6),Math.sin(a)*(r+6));ctx.lineTo(Math.cos(a)*(r+10),Math.sin(a)*(r+10));ctx.stroke();}ctx.restore();}
 for(let k=0;k<47;k++){const u=(time*.09+k/47)%1,lane=(k%9)-4,x=u*w;const pull=Math.min(1,Math.max(0,(u-.34)/.51));const y=middle+lane*18*(1-pull);const blocked=(k%9<2||k%9>6)&&u>.49;if(blocked)continue;ctx.fillStyle=k%3===0?'#ecb085':'#d7f39e';ctx.globalAlpha=.28+.65*Math.sin(Math.PI*u);ctx.beginPath();ctx.arc(x,y,u>.53?2.4:1.8,0,2*Math.PI);ctx.fill();}ctx.globalAlpha=1;
 ctx.font='10px Consolas, monospace';ctx.fillStyle='#c9e9b1';ctx.textAlign='center';ctx.fillText('p(token | state)',xs[0],middle+4);ctx.fillText('allowed',xs[1],middle+4);ctx.fillText('next',xs[2],middle+4);
}
function loop(ts){if(!paused&&visible&&!document.hidden){time+=Math.min(.05,(ts-(last||ts))/1000);paint();}last=ts;raf=requestAnimationFrame(loop);}raf=requestAnimationFrame(loop);
new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;}).observe(canvas);
function motion(){document.body.classList.toggle('motion-off',paused);$('motion').textContent=paused?'Play motion':'Pause motion';$('motion').setAttribute('aria-pressed',paused?'true':'false');paint();}
$('motion').addEventListener('click',()=>{paused=!paused;motion();});reduce.addEventListener('change',e=>{paused=e.matches;motion();});motion();

let tourSeconds=12,autoEntry=true;
const stay=()=>{autoEntry=false;$('gallery-tour-note').textContent='Browse at your own pace. Every experiment starts its recorded walkthrough when opened.';$('stay-gallery').textContent='Index stays open';};
$('stay-gallery').onclick=stay;
document.addEventListener('pointerdown',e=>{if(e.isTrusted)stay();},{capture:true});
document.addEventListener('keydown',e=>{if(e.isTrusted)stay();},{capture:true});
document.addEventListener('wheel',e=>{if(e.isTrusted)stay();},{passive:true});
if(new URLSearchParams(location.search).has('manual'))stay();
setInterval(()=>{if(!autoEntry||document.hidden)return;tourSeconds--;if(tourSeconds<=0){autoEntry=false;location.assign('/lab/choice');}else $('gallery-tour-note').textContent=`The recorded walkthrough starts in ${tourSeconds} seconds. Every page explains itself, then opens the next.`;},1000);
import {applicationArt} from './applied-art.js';
