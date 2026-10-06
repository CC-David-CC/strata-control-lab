// A page owns only its short demonstration and one ordinary next-page link.
const $=s=>document.querySelector(s), all=s=>[...document.querySelectorAll(s)];
const point=(target,text,layer='example')=>({target,text,layer});
const select=(target,value,text,focus=target,layer='example')=>({target:focus,text,layer,do(){const e=$(target);if(!e)throw Error('Missing tour control '+target);e.value=String(value);e.dispatchEvent(new Event('change'));}});
const range=(target,value,text,focus=target)=>({target:focus,text,do(){const e=$(target);if(!e)throw Error('Missing tour dial '+target);e.value=String(value);e.dispatchEvent(new Event('input'));}});
const click=(target,text)=>({target,text,do(){const e=$(target);if(!e)throw Error('Missing tour step '+target);e.click();}});
const trace=text=>[point('#trace-frame',text),range('#trace-cursor',1,'The state changes. Code rebuilds what is legal before the next decision.'),{target:'#trace-frame',text:'Now the final recorded state. Replay reveals the outcome, including mistakes.',do(){const e=$('#trace-cursor');e.value=e.max;e.dispatchEvent(new Event('input'));}}];
const lenses=(rows)=>rows.map(([value,text])=>select('#lens',value,text));

// Shorter holds keep the tour moving; explanatory panels and pause remain available.
export const phaseDelay=text=>Math.max(4000,Math.min(6500,text.length*34));
export function comparisonSteps(page){
 const kind=page.score_view.raw_kind,steps=[];
 if($('#score-panel .token-strip'))steps.push(point('#score-panel .token-strip','Original token scores: raw ln p and raw p = exp(ln p). These use the full target vocabulary, before grammar or sampling.','raw'));
 else if(kind==='synthetic'&&$('#sandbox-output .distribution-split'))steps.push(point('#sandbox-output .distribution-split > div:first-child','The before distribution uses disclosed synthetic logits. These are teaching probabilities, not a native model measurement.','synthetic'));
 else steps.push(point('#score-raw-meaning','Start with the actual source and its units. This page has no native Chat probability row to invent.','inputs'));
 if($('#score-token-details .score-selection-weight'))steps.push(point('#score-token-details .score-selection-weight','Now compare the final native selection weight q. Grammar and sampling change q; the original raw p above keeps its meaning.','sampling'));
 steps.push(point('#score-derived-meaning','This page explains what it builds from the measurements: candidate weights, semantic features or code-owned results. Read the changed denominator and units.','derived'));
 return steps;
}

export const LESSONS={
 music:[point('.applied-stage','The staff is a four-note sketch. Native weights and the explicit surprise model are separate ingredients.'),select('#lens',1,'At the cadence, the application admits chord tones C, E and G. D is rejected by the checker.','.context-tape'),range('#dial',1,'This D candidate has a model score but no permission to be emitted here.','.applied-meaning'),point('.applied-baseline','Uniform legal notes and the supplied Markov model are honest simple baselines. No listener-quality claim follows from surprise.')],
 proof:[point('.applied-stage','The proof checker owns the implication and conjunction rules.'),select('#lens',1,'After assuming P AND Q, unpacking that assumption makes progress. These are independent checked states.','.context-tape'),select('#lens',2,'Now P is an actual assumption, so the exact tactic can close this goal.','.context-tape'),range('#dial',2,'A high answer weight never substitutes for a checked proof transition.','.applied-meaning')],
 compiler:[range('#dial',3,'x times 3 is a legal expression but has the wrong meaning. The exact coefficient check rejects it.','.applied-meaning'),range('#dial',1,'x plus x preserves meaning and is cheaper under the stated operation costs.','.applied-meaning'),select('#lens',1,'Change the native prompt’s multiplication cost. A complete four-candidate search is already a strong baseline.','.applied-baseline')],
 divider:[point('.applied-stage','The drawing is an ideal voltage divider. Code evaluates all four resistor-tolerance corners.'),select('#lens',1,'In this recorded 12-to-5-volt case, the model’s preferred pair is substantially worse than enumeration.','.research-stats'),point('.applied-baseline','Exact worst-case error separates a plausible-looking answer from a useful simulated design.')],
 transaction:[point('.applied-stage','The permission grammar cannot freeze a database snapshot. A commit must compare version and stock together.'),select('#lens',1,'With no stock, the checker admits only inspection. The emitted grammar contains that one chosen code.','.research-stats'),point('.grammar-slate:last-child','This is the actual native commit constraint. Version conflicts are demonstrated in the compact calculation above.')],
 camouflage:[select('#lens',1,'A heroic description changes wording while the structured unfinished state stays fixed.','.context-tape'),select('#lens',2,'The calm description is another measurement of the same facts. Compare drift and the direct code baseline.','.research-stats'),point('.applied-baseline','These three examples stayed on the correct greedy action. That is evidence for these fixtures, not universal robustness.')],
 adversary:[select('#lens',1,'A confident manager’s claim does not change the failed-test fact.','.context-tape'),select('#lens',2,'This finite search did not fool the greedy controller. Keep that outcome instead of inventing an attack.','.research-stats'),range('#dial',2,'Declaring success fits the grammar but carries exact toy regret two. Legal syntax is not good judgment.','.applied-meaning')],
 budget:[point('.applied-stage','The sensor likelihood is supplied by code. The model’s answer weight does not replace it.'),select('#lens',2,'At inspection cost 0.5, acting now has greater expected reward. The recorded model still chose inspection.','.research-stats'),point('.applied-baseline','This error costs 0.15 reward units in the toy. A real compute budget needs measured time and validated observation models.')],
 choice:[select('#score-view','raw_probability','First: how likely are these answer tokens in the whole vocabulary?','#distribution-bars','raw'),select('#score-view','weight','Now divide by the mass on our answer set. The same scores become a distribution over declared meanings.','#distribution-bars','derived')],
 boolean:[select('#score-view','raw_probability','A yes/no probe is a small measurement. These are the original token probabilities.','#distribution-bars','raw'),select('#score-view','weight','Condition on the two meanings. Your program can use this number; it is not a truth guarantee.','#distribution-bars','derived')],
 score:[select('#score-view','raw_probability','Start with the raw probability of each declared level. Those scores keep their full-vocabulary denominator.','#distribution-bars','raw'),select('#score-view','weight','Condition on the declared levels to obtain rubric weights. These are a derived distribution.','#distribution-bars','derived'),point('.stats','The rating is the weighted average of those levels, not an extra confidence signal.','derived')],
 candidates:[select('#path-select',1,'A phrase spans several tokens. Its score follows its own exact prefix.'),click('#path-tokens .token-strip button:last-child','Conditional token scores multiply along the path; log scores add.'),select('#path-select',2,'A different branch can win globally even when greedy next-token choices prefer another path.')],
 controller:[point('.decision-path','Only a legal next action can leave this state.'),{target:'.decision-path',text:'Apply the simulated action, then obtain the next recorded decision.',async do(api){$('#apply-step').click();await api.run();}},{target:'.decision-path',text:'The grammar changes again after the edit. Tests come before finishing.',async do(api){$('#apply-step').click();await api.run();}},{target:'.decision-path',text:'The final legal step completes this toy task. No shell command was executed.',async do(api){$('#apply-step').click();await api.run();}}],
 rerank:[point('.source-card:nth-of-type(1)','Each source keeps its text. A narrow question supplies a relevance distribution.'),point('.source-card:nth-of-type(3)','An unrelated source provides a useful comparison. HTTP concurrency does not create GPU batching.')],
 graph:[point('.graph-svg','The model proposes uncertain relationships. Code selects an admissible graph.'),point('.small-table','Rejected alternatives remain inspectable. The solver preserves the original source blocks.')],
 scene:[point('.scene-grid','Code checks geometry; text probes measure described properties.'),point('#human-choice','A person must still judge the rendered result. This text scorer never saw the pixels.')],
 wire:[point('#wire-tokens','Every visible token keeps its score and bytes.'),{target:'#result',text:'A real grammar example: a forced token can retain a tiny raw probability.',async do(api){$('#input-case').value='grammar';await api.run();}},{target:'#result',text:'Now a strict JSON request. Its complete schema appears in the request panel.',async do(api){$('#input-case').value='json-schema';await api.run();}},{target:'#result',text:'A client-owned function call is another output shape; the lab does not execute the tool.',async do(api){$('#input-case').value='tool-call';await api.run();}}],
 speculation:[point('.small-table','The draft proposes. The target verifies. Those probabilities describe different computations.'),point('.stats','A rejected proposal can still be confident. Replay scores are kept separate from the original prediction.')],
 performance:[point('.bars','These are measured whole-request timings on the disclosed machine.'),point('#result details','Cache state, output length and numerical path matter. A shorter bar alone does not isolate kernel overhead.')],
 samplers:[select('#recipe-view',0,'Choose credible candidates before adding heat: Min-P → Temperature.'),select('#recipe-view',1,'Reverse the order. Temperature can change which candidates survive.'),select('#recipe-view',6,'The native grammar first sets the legal support; the sampler shapes preferences within it.'),click('[data-native-token]:last-child','Inspect another generated token. These are native full-vocabulary stage counts.')],
 'sampler-sandbox':[range('#sandbox-heat',.4,'This teaching row is synthetic and complete. Lower heat concentrates it.'),range('#sandbox-heat',1.5,'Raise heat inside the retained support.'),select('#sandbox-recipe','sigma','Sigma selects by logit distance rather than a probability cutoff.'),select('#sandbox-recipe','xtc','XTC removes some obvious options. This sandbox is an explicit simulation.')],
 tictactoe:trace('Native X chooses a legal move; exact minimax O supplies the opponent.'),
 chess:[point('.chessboard','Code enumerates legal moves and checks mate. Legality is only the first test.'),click('#chess-toggle','This is the position actually reached, including the recorded missed mate.'),point('.measure-bars','Letter-label preferences came from a different prompt than UCI generation. Do not merge them into one distribution.')],
 poker:[click('[data-hand="1"]','Change the visible card. The hidden card keeps its stated prior.'),click('[data-hand="2"]','Now compare model choice with exact expected chips. Preference is not payoff.')],
 thermal:trace('A simulated plant changes load; code shields the next state before the model acts.'),
 scheduler:trace('Ready jobs form the legal set. Dependencies and deadlines live in code.'),
 context:[click('[data-context="1"]','Replace outdated text rather than just appending a correction.'),click('[data-context="2"]','Send explicit current state. This edits request context; it does not rewrite arbitrary KV tensor bytes.')],
 observer:trace('Several small semantic probes become a numerical observation vector.'),
 calibration:[range('#calibration-cut',.8,'Demand a stronger answer weight. Some examples are now withheld.'),range('#calibration-cut',1,'At this threshold there may be no retained cases. Confidence must be checked against outcomes.')],
 information:[select('#test-choice',0,'Use disclosed likelihoods to ask which observation is worth buying.'),select('#test-choice',1,'Another test changes the posterior and the cost. These Bayes calculations do not require another model call.')],
 search:[range('#search-cost',0,'Ignore cost: retain the strongest measured semantic score among valid programs.'),range('#search-cost',1,'Charge for complexity. The retained program can change without rewriting any source.')],
 frontier:[range('#forward',120,'Assume a slower forward pass. The engineering estimate changes immediately.'),range('#bandwidth',2,'Now constrain transfer bandwidth. Assumptions stay separate from measured selector time.')],
 'research-map':[click('[data-branch="11"]','A research proposal names a missing capability; it is not an implemented feature.'),click('[data-branch="12"]','Every unusual idea needs a baseline, budget and a way to prove it wrong.'),point('#branch-detail','This is where exploration starts, rather than a promise that the proposal will work.')],
 pressure:[point('.instrument-grid','Both answers are 60/40, but one boundary discards almost all the raw mass.'),range('#dial',15,'Ease the boundary: pressure drops while the conditional answer ratio stays fixed.'),...lenses([[1,'Now inspect a real color grammar and its measured surviving mass.'],[2,'A furniture grammar on the same question creates a different intervention.']]),point('.instrument-equation','Only pure masking at temperature 1 permits this exact log-normalizer identity.')],
 circuit:[point('.instrument-matrix','F means the original facts survived. S means the requested polite style appeared. These are four joint worlds.'),range('#dial',1,'Assume we observed S with certainty. Renormalize the two surviving worlds.'),...lenses([[1,'This native edit preserves the parcel weight and adds “please”.']]),point('.instrument-callout','Separate prompts can disagree with every possible joint distribution. The bound detects inconsistency, not which estimate is wrong.')],
 control:[range('#dial',0,'Start with base preferences inside the legal set.'),range('#dial',2,'Add desired behavior and subtract the undesired direction. The forbidden action stays at zero.'),...lenses([[1,'This labeled synthetic case makes the ranking reversal easy to see.']]),range('#dial',0,'Remove the control signal and compare. No new model request is hidden in this dial.')],
 future:[point('.instrument-network','Only BB reaches the goal in this checked tree. A short first step can be a dead end.'),range('#dial',0,'With lookahead disabled, use the original next-action distribution.'),range('#dial',1,'Exact future value redirects the first step. Conditioning both steps is a separate operation.'),...lenses([[1,'A prompted future-success estimate is only a proxy for the exact policy value.'],[2,'In this synthetic example, weighting 80/20 by 0.05/0.90 favors B at about 82%.']])],
 sensitivity:[point('.heatmap','Columns are controlled interventions. Rows measure which properties moved.'),...lenses([[3,'Adding “URGENT” is a discrete wording change, not a derivative.'],[4,'This held-out combination tests the local approximation; its residual exposes a poor prediction.']]),range('#dial',2,'Penalize collateral changes. The preview searches nine disclosed interventions using the measured matrix.')],
 counterexamples:[point('.instrument-network','Exact algebra fixes meaning while model measurements can move.'),click('[data-pair="1"]','Inspect another equivalent pair. Its source and native probes stay together.'),...lenses([[1,'Search the same graph for different verified properties with the smallest measurement gap.'],[2,'These expressions share both chosen properties. Their collision can be ordinary information loss.']]),range('#dial',-2,'Try a negative integer. The slider illustrates an outcome; canonical coefficients supply the all-integers proof.')]
};

export function createTour(api){
 let version=0,playing=false,timer=null,wake=null,current=null,next=null;
 const bar=$('#tour-bar'),toggle=$('#tour-toggle'),caption=$('#tour-caption'),label=$('#tour-phase');
 function wait(ms){return new Promise(resolve=>{wake=resolve;timer=setTimeout(()=>{timer=null;wake=null;resolve();},ms);});}
 function clear(){clearTimeout(timer);timer=null;wake?.();wake=null;all('.tour-focus').forEach(e=>e.classList.remove('tour-focus'));delete document.body.dataset.tourLayer;delete bar.dataset.layer;}
 function pause(text='Paused. Explore freely, or restart the recorded tour.'){
  version++;playing=false;clear();document.body.classList.remove('tour-playing');toggle.textContent='Restart recorded tour';toggle.setAttribute('aria-pressed','false');caption.textContent=text;label.textContent='TAKE CONTROL';bar.dataset.state='paused';
 }
 function highlight(selector){
  all('.tour-focus').forEach(e=>e.classList.remove('tour-focus'));const node=$(selector);
  if(!node)throw Error('Missing tour view '+selector);node.classList.add('tour-focus');
  if(node.tagName==='DETAILS')node.open=true;
  const room=bar.getBoundingClientRect().top-30,box=node.getBoundingClientRect();
  const top=Math.max(24,(room-Math.min(box.height,room))/2);
  window.scrollBy({top:box.top-top,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
 }
 async function start(page,nextPage,manual=false){
  version++;clear();current=page;next=nextPage;const mine=version;playing=!manual;
  $('#tour-next').href='/lab/'+next.id;$('#tour-next').textContent='Next: '+(next.name||next.id)+' →';
  if(manual){pause();return;}
  document.body.classList.add('tour-playing');toggle.textContent='Pause / explore';toggle.setAttribute('aria-pressed','true');bar.dataset.state='playing';bar.dataset.experiment=page.id;
  label.textContent='AUTOMATIC RECORDED TOUR';caption.textContent='Loading a real recorded example. No model connection or clicks needed.';
  try{
   await api.run();if(mine!==version)return;
   if($('#status').textContent!=='Completed')throw Error('The recorded example did not complete. Inspect its visible error.');
   const steps=[...comparisonSteps(page),point('#lesson-bars','Now the calculated chart. Read its units: these values use this example’s rules, rather than automatically being raw token probabilities.','derived'),{target:'#lesson-state',layer:'derived',text:'Change one setting and watch the calculation respond. These are saved measurements; the comparison makes no hidden model call.',do(){api.showLesson(1);}},point('#result','Now open the full experiment. Its controls expose the measurements behind the compact calculation above.'),...LESSONS[page.id],{target:'#request-body',text:'This is the exact first request, or the disclosed inputs when this example makes no model call. The selector above exposes every saved request.',do(){api.showRequest(0);}},point('#constraint-body','Read the actual GBNF, JSON format and sampler settings here. When a feature was not used, the panel says so.'),point('#request-panel .panel-heading','Download the selected question/rule/result calculation and every mock in one Python file. It works offline and accepts a changed setting with --value.'),point('#next','The next research gate stays explicit. This page will now open the next experiment.')];
   for(let i=0;i<steps.length;i++){
    if(mine!==version)return;
    while(document.hidden){await wait(1000);if(mine!==version)return;}
    const layer=steps[i].layer||'example',duration=phaseDelay(steps[i].text);
    bar.dataset.step=String(i);bar.dataset.total=String(steps.length);bar.dataset.layer=layer;bar.dataset.delayMs=String(duration);document.body.dataset.tourLayer=layer;
    const labels={raw:'RAW PROBABILITY',sampling:'NATIVE SAMPLING WEIGHT',derived:'DERIVED VIEW',synthetic:'SYNTHETIC INPUTS',inputs:'SOURCE & UNITS',example:'EXPERIMENT'};
    label.textContent=`${labels[layer]} · ${String(i+1).padStart(2,'0')} / ${steps.length} · ${page.name||page.id}`;
    caption.textContent=steps[i].text;await steps[i].do?.(api);if(mine!==version)return;
    highlight(steps[i].target);$('#tour-progress').style.width=`${100*(i+1)/steps.length}%`;
    await wait(duration);
   }
   while(document.hidden&&mine===version)await wait(1000);
   if(mine===version)location.assign('/lab/'+next.id); // Full navigation; no state or query passed.
  }catch(error){if(mine===version){pause('Tour paused: '+error.message);bar.dataset.state='error';}}
 }
 toggle.onclick=()=>playing?pause():api.restart();
 document.addEventListener('pointerdown',e=>{if(e.isTrusted&&playing&&!e.target.closest('#tour-bar'))pause();},{capture:true});
 document.addEventListener('keydown',e=>{if(e.isTrusted&&playing&&!e.target.closest('#tour-bar')&&['Tab','Enter',' ','Escape','ArrowDown','ArrowUp','ArrowLeft','ArrowRight'].includes(e.key))pause();},{capture:true});
 document.addEventListener('wheel',e=>{if(e.isTrusted&&playing)pause();},{passive:true});
 window.addEventListener('pagehide',()=>{version++;clear();});
 return {start,pause};
}
