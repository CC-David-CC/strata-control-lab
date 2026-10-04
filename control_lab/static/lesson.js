const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=v=>Math.abs(v)<.0001&&v!==0?v.toExponential(3):v.toLocaleString(undefined,{maximumFractionDigits:4});
let current=null;
export function clearLesson(){current=null;$('lesson-panel').hidden=true;}
export function showLesson(index=0){
 if(!current?.states.length)return;
 index=Math.max(0,Math.min(current.states.length-1,index));const s=current.states[index],panel=$('lesson-panel');
 panel.dataset.state=String(index);panel.dataset.value=String(s.value);
 $('lesson-setting').textContent=current.knob+' = '+number(s.value);
 $('lesson-result').textContent=s.summary;$('lesson-limit').textContent=s.note;
 const visible=s.rows.length>6?[...s.rows].sort((a,b)=>Math.abs(b.value)-Math.abs(a.value)).slice(0,6):s.rows;
 const scale=Math.max(...visible.map(r=>Math.abs(r.value)),1e-12);
 $('lesson-bars').innerHTML=visible.map(r=>`<div class="lesson-row ${r.value<0?'negative':''}"><span title="${esc(r.label)}">${esc(r.label)}</span><div><i style="width:${100*Math.abs(r.value)/scale}%"></i></div><b>${number(r.value)}</b></div>`).join('')||'<p class="lesson-empty">No candidate passes this rule.</p>';
 $('lesson-unit').textContent=s.unit+(s.rows.length>6?' · largest 6 shown; every value below':'')+' · bars scaled to the largest magnitude';
 $('lesson-details').textContent=JSON.stringify(s.metrics,null,2);
 $('lesson-all-rows').textContent=JSON.stringify(s.rows,null,2);
 document.querySelectorAll('[data-lesson-state]').forEach(b=>{b.classList.toggle('selected',+b.dataset.lessonState===index);b.setAttribute('aria-pressed',String(+b.dataset.lessonState===index));});
}
export function renderLesson(lesson){
 current=lesson;const panel=$('lesson-panel');panel.hidden=false;
 $('lesson-question').textContent=lesson.question;$('lesson-rule').textContent=lesson.rule;
 $('lesson-input').textContent=lesson.input_excerpt?'Input: '+lesson.input_excerpt:'';$('lesson-input').hidden=!lesson.input_excerpt;
 $('lesson-scope').textContent=lesson.scope;
 if(!lesson.states.length){$('lesson-state').hidden=true;$('lesson-unavailable').hidden=false;$('lesson-unavailable').textContent=lesson.unavailable;return;}
 $('lesson-state').hidden=false;$('lesson-unavailable').hidden=true;
 $('lesson-presets').innerHTML=lesson.states.map((s,i)=>`<button type="button" data-lesson-state="${i}" aria-pressed="false">${i?'Try a change':'Starting view'} <b>${esc(number(s.value))}</b></button>`).join('');
 document.querySelectorAll('[data-lesson-state]').forEach(b=>b.onclick=()=>showLesson(+b.dataset.lessonState));
 showLesson(0);
}
export function lessonView(){
 if(!current?.states.length)return null;
 const index=+$('lesson-panel').dataset.state;
 return {index,value:current.states[index].value,scope:'Reproduce the selected question/rule/result panel. Other page dials are independent.'};
}
