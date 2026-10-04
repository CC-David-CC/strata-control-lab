const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Each drawing is an explanatory sketch. Native timing/threads are never inferred.
export function applicationArt(kind,active=0){
 const green='#d6ed9b',dim='#6c9275',amber='#e4b58f';let body='';
 const text=(x,y,t,size=18)=>`<text x="${x}" y="${y}" text-anchor="middle" fill="${green}" font-size="${size}" font-family="monospace">${esc(t)}</text>`;
 const box=(x,y,w,h,t,on=false)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="${on?'#365d3d':'#193f33'}" stroke="${on?green:dim}"/>${text(x+w/2,y+h/2+5,t,14)}`;
 if(kind==='music'){
  for(let i=0;i<5;i++)body+=`<path d="M45 ${55+i*22}H555" stroke="${dim}" opacity=".65"/>`;
  [0,2,4,7].forEach((pitch,i)=>{const x=110+i*120,y=143-pitch*10;body+=`<ellipse class="app-note ${i===active?'active':''}" cx="${x}" cy="${y}" rx="14" ry="10" fill="${i===active?green:dim}"/><path d="M${x+12} ${y}V${y-46}" stroke="${green}" stroke-width="3"/>${text(x,203,['C','D','E','G'][i])}`;});
 }else if(kind==='proof'){
  body=`<path d="M300 44V95M155 110H445M155 110V150M445 110V150" fill="none" stroke="${dim}" stroke-width="2"/>`+box(220,20,160,42,'(P ∧ Q) ⇒ P',active===0)+box(70,85,170,48,'assume P ∧ Q',active===1)+box(355,85,170,48,'goal P',active===2)+box(94,155,120,42,'P, Q',active===1)+box(385,155,120,42,'check P',active===2);
 }else if(kind==='compiler'){
  body=box(35,72,185,65,'x * 2 + 0')+`<path class="app-flow" d="M232 105H348" stroke="${green}" stroke-width="3" stroke-dasharray="7 7"/>`+box(365,45,190,50,active===3?'x * 3  ✕':active===1?'x + x':active===0?'x * 2 + 0':'2 * x',true)+box(365,129,190,45,active===3?'different meaning':'same coefficients');body+=text(290,210,'meaning first · cost second',13);
 }else if(kind==='divider'){
  body=`<path d="M300 24V49M300 90V115H458M300 115V145M300 185V208M270 208H330M280 216H320" fill="none" stroke="${green}" stroke-width="3"/>`+box(260,49,80,41,'R top',active%2===0)+box(260,145,80,40,'R bot',active%2===1)+text(180,34,'V in',16)+text(470,109,'V out',16)+`<circle class="app-signal" cx="300" cy="115" r="6" fill="${amber}"/>`;
 }else if(kind==='transaction'){
  body=box(35,36,180,55,'snapshot version')+box(375,36,180,55,'current version',true)+`<path class="app-flow" d="M218 65H370" stroke="${green}" stroke-width="3" stroke-dasharray="8 7"/>`+box(180,138,240,52,'match AND stock > 0?',true);body+=text(300,222,'permission ≠ atomic commit',13);
 }else if(kind==='camouflage'){
  body=box(216,20,168,45,'tests_passed=false',true);
  for(let i=0;i<3;i++){const x=36+i*190;body+=`<path d="M300 65L${x+73} 107" stroke="${dim}"/>`+box(x,108,147,82,['plain report','heroic prose','calm status'][i],i===active%3);for(let k=0;k<3;k++)body+=`<path d="M${x+15} ${158+k*9}h${84-k*10}" stroke="${dim}" opacity=".4"/>`;}
 }else if(kind==='adversary'){
  body=`<rect x="32" y="28" width="536" height="167" rx="16" fill="none" stroke="${green}" stroke-dasharray="8 5"/>`+text(300,220,'Every code fits. Not every action helps.',13);
  ['inspect','retry','finish','ask'].forEach((name,i)=>{body+=box(52+i*130,75,107,54,name,i===active);if(i===2)body+=text(105+i*130,164,'regret 2',13);});
 }else if(kind==='budget'){
  body=box(211,17,178,40,'belief .55 / .45')+`<path d="M300 59L145 113M300 59L455 113" stroke="${dim}" stroke-width="2"/>`+box(58,112,174,46,'best act now',active<2)+box(365,112,174,46,'inspect − cost',active===2)+text(145,197,'best reward .55',15)+text(455,197,'reward .90 − c',15);
 }
 return `<svg class="applied-art" viewBox="0 0 600 240" role="img" aria-label="Illustration of ${esc(kind)}; numerical results and exact inputs are adjacent">${body}</svg>`;
}
