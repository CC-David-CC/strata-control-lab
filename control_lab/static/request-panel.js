const $=id=>document.getElementById(id);
let captured=null, titles=[];
export function clearRequests(){captured=null;$('request-select').innerHTML='';$('request-body').textContent='Loading the recorded example…';$('constraint-body').textContent='The exact output constraint will appear here.';$('python-download').disabled=true;}
export function showRequest(index){
 if(!captured)return;
 const calls=captured.receipt.calls;
 if(!calls.length){
  $('request-select').disabled=true;
  $('request-kind').textContent='No HTTP request in this experiment';
  $('request-body').textContent=JSON.stringify(captured.result,null,2);
  $('constraint-body').textContent='No HTTP request, GBNF or JSON output constraint. This page uses disclosed calculations or recorded native diagnostics. The Python file recalculates its question/rule/result panel from these saved inputs.';
  return;
 }
 index=Math.max(0,Math.min(calls.length-1,index));$('request-select').value=String(index);$('request-select').disabled=false;
 const call=calls[index],r=call.request;
 $('request-kind').textContent=`POST /v1/chat/completions · ${captured.receipt.mode==='recorded'?'recorded native request':'this live run'} · ${index+1} of ${calls.length}`;
 $('request-body').textContent=JSON.stringify(r,null,2);
 $('constraint-body').textContent=[r.grammar?'GBNF\n'+r.grammar:'GBNF: none in this request',r.response_format?'JSON format\n'+JSON.stringify(r.response_format,null,2):'JSON output format: none',r.strata_sampler?'Sampler\n'+JSON.stringify(r.strata_sampler,null,2):''].filter(Boolean).join('\n\n');
}
export function setRequests(snapshot,steps){
 captured=structuredClone(snapshot);titles=snapshot.receipt.calls.map(c=>steps.find(s=>s.request&&JSON.stringify(s.request)===JSON.stringify(c.request))?.title);
 $('request-select').replaceChildren(...snapshot.receipt.calls.map((_,i)=>new Option(`${i+1}. ${titles[i]||'Native request'}`,String(i))));
 showRequest(0);$('python-download').disabled=false;
}
// JSON strings are compatible Python string literals; booleans/null need their Python spellings.
export function pythonLiteral(value,depth=0){
 const indent='    '.repeat(depth),next=indent+'    ';
 if(value===null)return 'None';if(typeof value==='boolean')return value?'True':'False';
 if(typeof value==='string')return JSON.stringify(value);
 if(typeof value==='number'){if(!Number.isFinite(value))throw Error('Non-finite number in export');return String(value);}
 if(Array.isArray(value))return value.length?'[\n'+value.map(x=>next+pythonLiteral(x,depth+1)).join(',\n')+'\n'+indent+']':'[]';
 return Object.keys(value).length?'{\n'+Object.entries(value).map(([key,v])=>next+JSON.stringify(key)+': '+pythonLiteral(v,depth+1)).join(',\n')+'\n'+indent+'}':'{}';
}
export function buildPython(template,lessonCode,snapshot){
 for(const marker of ['# __CAPTURED_DATA__','# __LESSON_CODE__'])if(template.split(marker).length!==2)throw Error('Python runner must contain one '+marker+' insertion point');
 // Replace only original template markers. Never rescan inserted user/model text.
 return '# -*- coding: utf-8 -*-\n'+template.replace(/# __(CAPTURED_DATA|LESSON_CODE)__/g,(_match,name)=>name==='CAPTURED_DATA'?'CAPTURED = '+pythonLiteral(snapshot):lessonCode);
}
$('request-select').addEventListener('change',e=>showRequest(+e.target.value));
$('request-copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('request-body').textContent);$('request-copy').textContent='Copied';setTimeout(()=>$('request-copy').textContent='Copy request',1600);}catch{$('request-export-note').textContent='Clipboard access was unavailable. Select the visible request text to copy it, or download Python.';}});
$('python-download').addEventListener('click',async()=>{
 if(!captured)return;
 const snapshot=structuredClone(captured),button=$('python-download');snapshot.lesson_view=lessonView();button.disabled=true;
 try{
  const calculator=snapshot.lesson?.calculator||'lesson_math';
  if(!['lesson_math','applied_math'].includes(calculator))throw Error('Unknown portable calculator');
  const [response,calculation]=await Promise.all([fetch('/static/portable.py'),fetch('/static/'+calculator+'.py')]);if(!response.ok||!calculation.ok)throw Error('Python runner or calculation could not load');
  const [template,lessonCode]=await Promise.all([response.text(),calculation.text()]);
  const source=buildPython(template,lessonCode,snapshot);
  const url=URL.createObjectURL(new Blob([source],{type:'text/x-python;charset=utf-8'})),a=document.createElement('a');
  a.href=url;a.download=`strata-${snapshot.experiment}-example.py`;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
 }catch(error){$('request-export-note').textContent=error.message;}finally{button.disabled=false;}
});
import {lessonView} from './lesson.js';
