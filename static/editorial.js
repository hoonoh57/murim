'use strict';
// Pre-production authority lives on the server; disabled tabs are only a usability aid.
let editorialState=null,editorialDraft=null,editorialPid=null,preMode='policy',preVisible=true,editorialSerial=0,editorialNote='';
let inputs={critique:'',instruction:'',answer:'',review:'',reviewer:''};
function editorialAllowed(){return !!editorialState?.approved&&editorialPid===doc?.id}
function preDirty(){return !!(inputs.critique.trim()||inputs.answer.trim()||inputs.review.trim())}
window.addEventListener('beforeunload',e=>{if(preDirty()){e.preventDefault();e.returnValue=''}});
function preEl(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e}
function preButton(root,title,fn){const b=preEl('button',title);b.type='button';b.onclick=()=>{if(!busy)Promise.resolve().then(fn).catch(err)};root.append(b);return b}
function preField(root,label,value,fn,rows=4){const l=preEl('label',label),e=preEl('textarea');e.rows=rows;e.value=value||'';e.oninput=()=>fn(e.value);l.append(e);root.append(l);return e}
function preText(root,text){root.append(preEl('p',text))}
function preCard(root,title){const e=preEl('section');e.className='pre-card';e.append(preEl('h3',title));root.append(e);return e}
function preLayout(){
    $('preTabs').hidden=!doc;
    $('enterProduction').disabled=!editorialAllowed();
    $('editorial').hidden=!doc||!preVisible;
    $('tabs').hidden=preVisible||!editorialAllowed();
    $('workspace').hidden=preVisible||!editorialAllowed();
    for(const id of ['addScene','deleteScene','moveUp','moveDown','saveScene','saveSpeech']){$(id).disabled=true;$(id).title='승인된 시나리오 변경은 00B에서 새 버전으로 재심사하세요'}
    for(const id of ['title','seconds','speech','voiceText'])$(id).readOnly=true;
    document.querySelectorAll('[data-pre]').forEach(e=>e.classList.toggle('active',e.dataset.pre===preMode&&preVisible));
}
async function editorialRefresh(d){
    const seq=++editorialSerial,changed=editorialPid!==d.id;
    if(changed){editorialPid=d.id;editorialState=null;editorialDraft=null;editorialNote='';inputs={critique:'',instruction:'',answer:'',review:'',reviewer:''};preVisible=true;preMode='policy'}
    preLayout();
    const v=await api('/project/'+d.id+'/editorial');
    if(seq!==editorialSerial||doc?.id!==d.id)return;
    const changedToken=editorialState?.token!==v.token;
    editorialState=v;
    if(changed||changedToken||!editorialDraft){editorialDraft=structuredClone(v.latest.plan);editorialNote=''}
    if(!v.approved)preVisible=true;
    preLayout();if(preVisible)drawEditorial();else drawEditorialContext();
    if(changed&&$('notice').textContent.startsWith('작품을 열어 주세요'))notice('작품 열기 완료 · 사전 제작에서 비평과 개선안을 확인하세요');
}
function showEditorial(mode){preMode=mode;preVisible=true;preLayout();drawEditorial()}
function drawEditorialContext(){const e=$('approvedContext');if(!e||!editorialAllowed())return;const plan=editorialState.latest.plan,shot=plan.scenes.find(s=>s.id===sid);e.textContent=shot?'승인 제작안 '+editorialState.latest.revision.slice(0,12)+'\\n시각: '+shot.visual+'\\n동작: '+(shot.motion||'정지 이미지 중심')+'\\n음향: '+shot.sound+'\\n사료: '+shot.facts:'';}
document.querySelectorAll('[data-pre]').forEach(e=>e.onclick=()=>showEditorial(e.dataset.pre));
$('enterProduction').onclick=()=>{if(editorialAllowed()){if(preDirty()){notice('미저장 제작안을 먼저 저장하거나 새로고침하세요',true);return}preVisible=false;preLayout();setTab('story');showSelected();drawEditorialContext()}};
async function preMutate(kind,data){
    // The pasted response is cleared only after a successful server write.
    const id=doc.id;
    await action(async()=>{
        const v=await api('/project/'+id+'/editorial',{token:editorialState.token,action:kind,data});
        if(doc.id!==id)return;
        editorialState=v;editorialDraft=structuredClone(v.latest.plan);editorialNote='';
        if(kind==='prior_capture')inputs.critique='';
        if(kind==='relay_plan'){inputs.answer='';inputs.instruction='';preMode='script'}
        if(kind==='review'){inputs.review='';inputs.reviewer='';preMode='gate'}
        if(kind==='approval')update(await api('/project/'+id));
        if(kind==='feedback'){preVisible=true;preMode='gate';$('reviewText').value='';$('structuralIssues').value='';}
        preLayout();drawEditorial();notice('사전 제작 이력 저장 · '+v.status);
    },'사전 제작안 검증 및 저장 중…');
}

const order=['purpose','audience','policy','story','facts','visual','audio','ending'];
const axisLabels={viewer_value:'시청 가치',narrative:'서사 몰입',historical_evidence:'사실과 근거',visual_design:'시각 설계',audio_design:'음향 설계',coherence:'전체 정합성'};
const sceneLabels={title:'장면 제목',narration:'실제 발화 대본',visual:'화면 연출',motion:'동작',sound:'음향',facts:'사료 및 출처',subtitle:'자막'};
const stateLabels={APPROVED:'제작 승인',HOLD:'검토 대기',REWORK_REQUIRED:'재수정 필요',APPROVAL_REQUIRED:'독립 심사 통과 · 인간 승인 대기'};
function field(root,label,k,rows=4){return preField(root,label,inputs[k],x=>inputs[k]=x,rows)}
function rawDetails(root,label,value){if(!value)return;const d=preEl('details');d.append(preEl('summary',label),preEl('pre',value));root.append(d)}
function copyButton(root,label,make){return preButton(root,label,async()=>{await navigator.clipboard.writeText(make());notice('복사 완료 · 외부 AI에 붙여 넣고 답변 전체를 가져오세요')})}
function changeText(root,oldValue,newValue){
    const row=preEl('div');row.className='pre-grid';
    for(const [title,value] of [['수정 전',oldValue],['수정 후',newValue]]){
        const c=preEl('div');c.className='pre-read';c.append(preEl('h4',title),preEl('p',value||'기록 없음'));row.append(c)}
    root.append(row)
}
function sceneText(s){if(!s)return '해당 장면 없음';return s.title+' · '+(s.frames/24).toFixed(2)+'초\n'+Object.entries(sceneLabels).filter(([k])=>k!=='title').map(([k,label])=>label+': '+(s[k]||'—')).join('\n\n')}
function manuscript(p){return p.scenes.map((s,i)=>String(i+1)+'. '+s.title+' ('+(s.frames/24).toFixed(2)+'초)\n'+(s.narration||'(발화 없음)')).join('\n\n')}
function promptForPlan(v){
    const schema={parent:v.latest.revision,plan:v.latest.plan,note:'기존 결함별 실제 수정 근거와 원본 대비 변경점',prior_issues:['기존 비평 원문에서 발견한 모든 결함을 빠짐없이 추출']};
    return '당신은 실제 콘텐츠를 수정하는 감독·작가입니다. 다음 감독 지시와 비평을 바탕으로 기획과 전체 실제 대본, 장면별 연출을 직접 다시 작성하십시오. 고칠 예정이라는 설명만 하지 말고 완성된 수정 원문을 제출하십시오. 역사 사실과 재연을 분리하고 미확인 출처를 지어내지 마십시오. 기존 실패 원인 전체를 수정하고 새 문제는 숨기지 마십시오. 답변 처음에는 사람이 읽는 원문 대비 개선 요약과 수정 전후 실제 문장 예시를 쓰고, 마지막에는 프로그램이 읽을 json 코드 블록 1개를 넣으십시오. 내부 데이터는 아래 모양 그대로, plan은 일부 패치가 아닌 전체 수정본. 모든 기획 항목·장면 제목·시각·음향·사료를 채우고, 발화 없음은 sound에 이유를 기록하십시오. 장면 id는 12자리 소문자 16진수, frames는 24fps 정수 24~1440. prior_issues는 기존 비평 원문의 전체 구체적 결함 목록이며 점수 예상이나 칭찬은 제외. note에는 실제 바뀐 대본·장면을 지목하십시오. 합격점 또는 심사 결과를 생성하지 마십시오.\n\n감독 수정 지시: '+(inputs.instruction.trim()||'기존 비평의 문제를 모두 해결하고 실제 시나리오를 완성하라.')+'\n\n기존 비평 원문:\n'+(v.prior_raw||v.original.prior_summary||'없음')+'\n\n현재 미해결 문제:\n'+JSON.stringify(v.issues)+'\n\n직전 독립 심사:\n'+(v.review?.raw||'미실행')+'\n\n실제 영상 구조 비평:\n'+JSON.stringify(v.feedback||[])+'\n\n현재 원문 및 프로그램 전달 형식:\n'+JSON.stringify(schema,null,2);
}
function promptForReview(v){
    const schema={revision:v.latest.revision,scores:Object.fromEntries(v.axes.map(x=>[x,null])),evidence:'각 항목의 실제 원문 근거',issues:[],resolutions:v.issues.map(i=>({id:i.id,resolved:false,evidence:'실제 변경 전후 문장, 장면 및 판단 근거'})),verdict:'HOLD'};
    return '당신은 제작에 참여하지 않은 독립 편집 심사자입니다. 아래 기존 원문과 실제 수정본을 비교하여 모든 비평 결함이 실질적으로 해소되었는지 검증하십시오. 단순 변경·추상적 약속은 해결이 아닙니다. 기존 비평 원문에 있는데 목록에서 누락된 문제와 새 문제는 issues에 모두 포함하십시오. 실제 영상/음향은 아직 생성 전이므로 실행 결과나 실제 관객 반응을 평가했다고 주장하지 마십시오. 기획과 실제 대본의 시청 가치, 서사, 역사 근거, 시각 설계, 음향 설계, 장면 간 정합성을 각각 0~10으로 독립 평가하고 자료 부족은 null. 해결하지 못한 결함이 있으면 PASS 금지. 점수 기대나 제작자의 주장은 심사 근거가 아닙니다. 사람이 읽을 수정 전후 평가표와 실제 문장 근거를 먼저 작성하고, 마지막에 아래 형식의 json 코드 블록 1개를 반환하십시오.\n\n기존 비평 원문:\n'+(v.prior_raw||v.original.prior_summary||'없음')+'\n\n기존 원본:\n'+JSON.stringify(v.original.plan,null,2)+'\n\n직전 제작안:\n'+JSON.stringify(v.versions.at(-2)?.plan||v.original.plan,null,2)+'\n\n실제 수정본:\n'+JSON.stringify(v.latest.plan,null,2)+'\n\n영상 구조 비평:\n'+JSON.stringify(v.feedback||[])+'\n\n검증 대상 문제:\n'+JSON.stringify(v.issues)+'\n\n프로그램 전달 형식:\n'+JSON.stringify(schema,null,2);
}
function relayRepair(root,answer,make){copyButton(root,'AI 응답 정리 요청 복사',()=>make()+'\n\n아래는 이미 받은 답변입니다. 내용과 평가를 임의로 개선하거나 변경하지 말고, 위에서 요구한 전달 블록을 완성하십시오. 실제 수정 원문 또는 실제 독립 평가가 없는 경우 그 사실을 명확히 밝히십시오.\n\n'+answer.value)}
function drawDirective(root,v){
    const c=preCard(root,'1. 기존 비평');
    if(v.original.prior_summary)preText(c,v.original.prior_summary+' · 예상 개선 점수는 합격 증거가 아닙니다.');
    if(v.prior_raw){preText(c,'기존 Gemini 응답 원문 보존 완료');rawDetails(c,'비평 원문 펼치기',v.prior_raw)}
    else{
        field(c,'Gemini 비평 답변 전체 붙여넣기','critique',5);
        preButton(c,'비평 원문 저장',()=>preMutate('prior_capture',{raw:inputs.critique}));
        preText(c,v.original.known_failed?'먼저 기존 비평 원문을 저장하세요. 문제 분류와 개선안은 AI에게 맡깁니다.':'기존 비평이 없는 새 작품이라면 다음 단계로 진행할 수 있습니다.');
    }
    if(v.original.known_failed&&!v.prior_raw)return;
    const d=preCard(root,'2. AI에게 무엇을 고치라고 할까요?');
    field(d,'감독의 자연어 수정 지시 (비우면 기존 비평 전체 개선)','instruction',3).placeholder='예: 1842년 자료 사용 오류를 고치고, 첫 3초에 실제 사건으로 몰입시키며 결말까지 완결해 줘.';
    copyButton(d,'수정 요청 복사',()=>promptForPlan(v));
    preText(d,'ChatGPT 또는 Gemini에 붙여넣고 실제로 수정된 답변 전체를 아래에 가져오세요. 프로그램 전달 데이터는 AI가 작성합니다. 직접 형식을 수정할 필요는 없습니다.');
    const a=field(d,'AI가 반환한 수정 답변 전체','answer',5);
    const b=preButton(d,'수정본 저장 및 전후 비교',()=>preMutate('relay_plan',{raw:inputs.answer,instruction:inputs.instruction}));b.classList.add('primary');
    relayRepair(d,a,()=>promptForPlan(v));
    if(!v.latest.original)preButton(d,'현재 수정본 비교 보기',()=>showEditorial('script'));
}
function drawCompare(root,v){
    const c=preCard(root,'실제 대본과 기획의 전후 비교');
    const pair=preEl('div'),bar=preEl('div');bar.className='bar';
    const selects=[];
    for(const [label,initial] of [['기준 버전',0],['비교 버전',v.versions.length-1]]){
        const l=preEl('label',label),s=preEl('select');v.versions.forEach((x,i)=>{const op=preEl('option',i===0?'V0 원본':'V'+i+(x.review?' · '+(x.review.pass?'심사 통과':'재수정'):' · 미심사'));op.value=String(i);s.append(op)});s.value=String(initial);l.append(s);bar.append(l);selects.push(s);}
    c.append(bar,pair);
    function compare(){
        pair.replaceChildren();const from=v.versions[Number(selects[0].value)],to=v.versions[Number(selects[1].value)];
        preText(pair,'V'+selects[0].value+' → V'+selects[1].value+' · '+(to.review?'독립 심사 '+(to.review.total===null?'미평가':to.review.total.toFixed(1)+'/100'):'독립 심사 전'));
        const story=preCard(pair,'실제로 읽게 될 대본 전체');changeText(story,manuscript(from.plan),manuscript(to.plan));
        const changes=preCard(pair,'기획·연출의 실제 변경점');
        let count=0;for(const k of order)if(from.plan[k]!==to.plan[k]){changes.append(preEl('h4',v.fields[k]));changeText(changes,from.plan[k],to.plan[k]);count++}
        const old=from.plan.scenes,newScenes=to.plan.scenes;
        const ids=[...new Set([...old.map(x=>x.id),...newScenes.map(x=>x.id)])];
        for(const id of ids){const a=old.find(x=>x.id===id),b=newScenes.find(x=>x.id===id);if(sceneText(a)!==sceneText(b)||old.indexOf(a)!==newScenes.indexOf(b)){const item=preEl('details');item.append(preEl('summary',(b?.title||a?.title)+(a&&b?' · 변경':b?' · 추가':' · 제거')));changeText(item,a?String(old.indexOf(a)+1)+'번\n'+sceneText(a):'',b?String(newScenes.indexOf(b)+1)+'번\n'+sceneText(b):'');changes.append(item);count++}}
        if(!count)preText(changes,'변경된 내용 없음');
        if(to.note)rawDetails(pair,'AI의 변경 설명 (독립 심사 전 주장)',to.note);
        if(to.raw_response)rawDetails(pair,'AI 수정 응답 원문',to.raw_response);
        if(to.review)reviewSummary(pair,to.review,v);
    }
    selects.forEach(s=>s.onchange=compare);compare();
    preButton(root,'추가 수정 지시',()=>showEditorial('policy'));preButton(root,'독립 심사로 이동',()=>showEditorial('gate'));
}
function reviewSummary(root,r,v){
    const c=preCard(root,'독립 심사 결과 · '+(r.total===null?'미평가':r.total.toFixed(1)+'/100'));
    preText(c,(r.pass?'심사 통과':'제작 보류')+' · '+r.reviewer);
    const table=preEl('table');table.className='pre-table';const tr=preEl('tr');for(const k of ['평가 항목','점수','판정'])tr.append(preEl('th',k));table.append(tr);
    for(const k of v.axes){const x=r.scores[k],row=preEl('tr');for(const val of [axisLabels[k]||k,x===null?'미평가':x+'/10',x===null?'보류':x>=9?'기준 충족':'개선 필요'])row.append(preEl('td',String(val)));table.append(row)}c.append(table);
    if(r.evidence)preText(c,r.evidence);
    if(r.resolutions){for(const item of r.resolutions){const issue=v.all_issues.find(i=>i.id===item.id),d=preCard(c,(item.resolved?'심사자: 해결':'미해결')+' · '+(issue?.description||item.id));preText(d,item.evidence)}}
    for(const x of r.issues)preText(c,'새 문제: '+x.description);
    rawDetails(c,'독립 심사 답변 원문',r.raw);
}
function drawGate(root,v){
    const c=preCard(root,'결함 해결 현황');
    if(v.original.prior_summary)preText(c,v.original.prior_summary+' · 기존 영상 평가와 새 기획 평가는 별도입니다.');
    for(const i of v.issues)preText(c,'미해결/재검증 필요 · '+i.description);
    if(!v.issues.length)preText(c,'추적 중인 미해결 문제 없음. 심사 및 승인 조건은 별도.');
    if(v.review)reviewSummary(root,v.review,v);
    else if(v.ready&&(!v.original.known_failed||v.prior_indexed)&&(!v.prior_raw||v.prior_indexed)){
        const d=preCard(root,'독립 AI에게 실제 수정본 검토 요청');
        copyButton(d,'독립 재심사 요청 복사',()=>promptForReview(v));
        preText(d,'수정 담당 AI와 별도의 심사 세션에 전달하고 답변 전체를 복사해 오세요. 예상 점수나 수정 담당자의 자체 평가를 등록하지 마세요.');
        field(d,'심사 모델·세션 (예: Gemini 별도 세션)','reviewer',1);
        const a=field(d,'독립 심사 답변 전체','review',5);
        preButton(d,'심사 결과 등록',()=>preMutate('review',{raw:inputs.review,reviewer:inputs.reviewer}));
        relayRepair(d,a,()=>promptForReview(v));
    }else preText(root,'먼저 비평을 등록하고 실제 수정본을 완성하세요.');
    if(v.review?.pass&&!v.issues.length&&!v.approved){
        const d=preCard(root,'제작 승인');preText(d,'독립 심사 기준 충족. 실제 원문과 수정 결과를 비교하고 제작 진행 여부를 결정하세요.');
        const who=preField(d,'승인자','',()=>{},1);
        const b=preButton(d,'검토 완료 · 이 수정본으로 제작 승인',()=>{if(confirm('원문 대비 실제 수정과 심사 근거를 검토했으며 현재 버전의 제작을 승인합니까?'))return preMutate('approval',{confirmed:true,approver:who.value,mvml_revision:v.mvml_revision})});b.classList.add('primary');
    }
    if(v.approved)preText(root,'이 버전은 제작 승인 상태입니다. 실제 완성 영상 평가는 별도입니다.');
    if(!v.approved)preButton(root,'다시 개선하기',()=>showEditorial('policy'));
    for(const f of v.feedback||[])rawDetails(root,'실제 영상 비평 · '+f.source.render,f.raw);
}
bind('returnEditorial',async()=>{
    if(!editorialAllowed())throw Error('현재 승인된 제작안이 필요합니다');
    const render=$('renders').value,raw=$('reviewText').value,issues=$('structuralIssues').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
    if(!render||!raw.trim()||!issues.length)throw Error('실제 렌더·비평 원문·구조적 결함 목록 모두 입력하세요');
    if(confirm('현재 제작 승인을 취소하고 기획·시나리오 재심사로 돌아갈까요? 기존 산출물은 보존됩니다.'))await preMutate('feedback',{render,raw,issues});
});
function drawEditorial(){
    const v=editorialState,root=$('prePanel');root.replaceChildren();
    if(!v){$('preStatus').textContent='사전 제작 상태 조회 중';return}
    $('preStatus').textContent='V'+(v.versions.length-1)+' · '+(stateLabels[v.status]||v.status)+' · 미해결 '+v.issues.length+'건 · '+(v.approved?'제작 가능':'제작 잠금');
    if(preMode==='policy')drawDirective(root,v);else if(preMode==='script')drawCompare(root,v);else drawGate(root,v);
    if(v.original.known_failed){const a=preEl('a','기존 실패 영상 다시 보기');a.href=base+p('/baseline');a.target='_blank';a.rel='noopener';root.append(a)}
}
