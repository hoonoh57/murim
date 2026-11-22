'use strict';
// Pre-production authority lives on the server; disabled tabs are only a usability aid.
let editorialState=null,editorialDraft=null,editorialPid=null,preMode='policy',preVisible=true,editorialSerial=0,editorialNote='';
let inputs={critique:'',instruction:'',answer:'',review:'',reviewer:'',candidate:'',final:'',selected:'',basis:'',compile:''};
function editorialAllowed(){return !!editorialState?.approved&&editorialPid===doc?.id}
function preDirty(){return !!(inputs.critique.trim()||inputs.answer.trim()||inputs.review.trim()||(inputs.candidate.trim()&&inputs.candidate!==editorialState?.document_candidates.find(c=>c.revision===inputs.selected)?.text)||inputs.compile.trim()||(inputs.final&&inputs.final!==editorialState?.final_document?.text))}
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
    if(changed){editorialPid=d.id;editorialState=null;editorialDraft=null;editorialNote='';inputs={critique:'',instruction:'',answer:'',review:'',reviewer:'',candidate:'',final:'',selected:'',basis:'',compile:''};preVisible=true;preMode='policy'}
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
        if(kind==='document_candidate'){inputs.selected=v.document_candidates.find(c=>c.text===data.text&&c.basis===data.basis)?.revision||'';inputs.candidate=data.text;inputs.final=data.text;preMode='policy'}
        if(kind==='document_final'){inputs.final=v.final_document.text;inputs.compile='';inputs.basis=v.final_document.revision;inputs.selected='';inputs.candidate='';preMode='script'}
        if(kind==='document_compile'){inputs.compile='';preMode='gate'}
        if(kind==='relay_plan'||kind==='relay_receive'){
            if(v.pending_reply){inputs.answer=v.pending_reply.raw;inputs.instruction=v.pending_reply.instruction;preMode='policy'}
            else{inputs.answer='';inputs.instruction='';preMode='script'}
        }
        if(kind==='review'){inputs.review='';inputs.reviewer='';preMode='gate'}
        if(kind==='approval')update(await api('/project/'+id));
        if(kind==='feedback'){preVisible=true;preMode='gate';$('reviewText').value='';$('structuralIssues').value='';}
        preLayout();drawEditorial();
        if(kind==='document_candidate')$('finalDocumentEditor')?.scrollIntoView({block:'nearest',behavior:'smooth'});
        if(kind==='relay_receive'){
            if(v.pending_reply)notice('답변 원문 보존 · 수정본으로 미적용: '+v.pending_reply.error,true);
            else notice('실제 수정본 V'+(v.versions.length-1)+' 저장 · 전후 비교를 확인하세요');
        }else if(kind==='document_candidate')notice('외부 수정 원문 저장 완료 · 아래에서 최종 원문을 확정하세요');
        else if(kind==='document_final')notice('최종 원문 V'+v.documents.length+' 확정 저장 완료 · 실제 제작 승인과 별도');
        else notice('사전 제작 이력 저장 · '+v.status);
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
function promptForDocument(v,basis){
    return '아래 원문을 직접 고쳐서 전체 수정 원문만 반환하세요. 비평·의견·수정 설명·점수·예상 점수·JSON·코드 블록을 쓰지 마세요. 완성된 기획과 실제 시나리오, 장면 순서·소요 시간·발화·화면·음향·자막·사료 출처를 포함하십시오. 개선되지 않은 부분도 누락하지 말고 전체 문서를 다시 제출하십시오. 확인되지 않은 역사 사실과 출처를 발명하지 마십시오.\n\n감독 지시:\n'+(inputs.instruction.trim()||'기존 비평의 모든 결함을 실제 원문에 반영하여 개선하세요.')+'\n\n참고 비평 (수정 대상이 아니라 기준):\n'+(v.prior_raw||v.original.prior_summary||'없음')+'\n\n최근 독립 심사:\n'+(v.review?.raw||'없음')+'\n\n수정할 원문:\n'+basis.text;
}
function promptForCompile(v){
    const schema={parent:v.latest.revision,document_revision:v.final_document.revision,plan:v.latest.plan,note:'확정 원문 제작 연결 설명',prior_issues:['기존 비평의 모든 구체적 결함']};
    return '이미 인간이 확정한 원문을 제작 데이터로 변환하는 작업입니다. 내용을 다시 쓰거나 새 발화·자막을 창작하지 마세요. 발화와 자막은 확정 원문의 실제 문장을 그대로 가져오세요. 장면별 시간은 24fps 정수 24~1440, id는 고유 12자리 소문자 16진수, 기획·화면·음향·사료 항목을 연결하십시오. 원문에 정보가 없으면 없는 사실을 지어내지 말고 확인 필요라고 표시하세요. 기존 비평의 모든 결함을 prior_issues에 분류하십시오. 독립 심사나 예상 점수는 하지 마세요. 다음 형태의 JSON 객체만 반환하십시오.\n'+JSON.stringify(schema,null,2)+'\n\n확정 원문 (변경 금지):\n'+v.final_document.text+'\n\n기존 비평:\n'+(v.prior_raw||v.original.prior_summary||'없음');
}
function promptForReview(v){
    const schema={revision:v.latest.revision,...(v.final_document?{document_revision:v.final_document.revision}:{}),scores:Object.fromEntries(v.axes.map(x=>[x,null])),evidence:'각 항목의 실제 원문 근거',issues:[],resolutions:v.issues.map(i=>({id:i.id,resolved:false,evidence:'실제 변경 전후 문장, 장면 및 판단 근거'})),verdict:'HOLD'};
    return '당신은 제작에 참여하지 않은 독립 편집 심사자입니다. 아래 기존 원문과 실제 수정본을 비교하여 모든 비평 결함이 실질적으로 해소되었는지 검증하십시오. 인간 확정 원문이 있으면 실제 제작 데이터의 발화·자막·장면 순서·누락·연출 의미가 확정 원문과 일치하는지도 검증하고 불일치는 issues에 기록하십시오. 단순 변경·추상적 약속은 해결이 아닙니다. 기존 비평 원문에 있는데 목록에서 누락된 문제와 새 문제는 issues에 모두 포함하십시오. 실제 영상/음향은 아직 생성 전이므로 실행 결과나 실제 관객 반응을 평가했다고 주장하지 마십시오. 기획과 실제 대본의 시청 가치, 서사, 역사 근거, 시각 설계, 음향 설계, 장면 간 정합성을 각각 0~10으로 독립 평가하고 자료 부족은 null. 해결하지 못한 결함이 있으면 PASS 금지. 점수 기대나 제작자의 주장은 심사 근거가 아닙니다. 사람이 읽을 수정 전후 평가표와 실제 문장 근거를 먼저 작성하고, 마지막에 아래 형식의 json 코드 블록 1개를 반환하십시오.\n\n기존 비평 원문:\n'+(v.prior_raw||v.original.prior_summary||'없음')+'\n\n인간 확정 원문 (제작 데이터 일치 여부도 검증):\n'+(v.final_document?.text||'이전 방식 제작안')+'\n\n기존 원본:\n'+JSON.stringify(v.original.plan,null,2)+'\n\n직전 제작안:\n'+JSON.stringify(v.versions.at(-2)?.plan||v.original.plan,null,2)+'\n\n실제 수정본:\n'+JSON.stringify(v.latest.plan,null,2)+'\n\n영상 구조 비평:\n'+JSON.stringify(v.feedback||[])+'\n\n검증 대상 문제:\n'+JSON.stringify(v.issues)+'\n\n프로그램 전달 형식:\n'+JSON.stringify(schema,null,2);
}
function relayRepair(root,answer,make){copyButton(root,'AI 응답 정리 요청 복사',()=>make()+'\n\n아래는 이미 받은 답변입니다. 내용과 평가를 임의로 개선하거나 변경하지 말고, 위에서 요구한 전달 블록을 완성하십시오. 실제 수정 원문 또는 실제 독립 평가가 없는 경우 그 사실을 명확히 밝히십시오.\n\n'+answer.value)}
function documentBases(v){return [{revision:v.original_text_revision,text:v.original_text,label:'V0 원본'},...v.documents.map((d,i)=>({...d,label:'V'+(i+1)+' 확정 원문'}))]}
function documentSelect(root,label,rows,value,change){
    const l=preEl('label',label),s=preEl('select');for(const r of rows){const o=preEl('option',r.label);o.value=r.revision;s.append(o)}s.value=value;s.onchange=()=>change(s.value);l.append(s);root.append(l);return s
}
function drawDirective(root,v){
    const bases=documentBases(v),latest=bases.at(-1);
    if(!bases.some(x=>x.revision===inputs.basis))inputs.basis=latest.revision;
    const basis=bases.find(x=>x.revision===inputs.basis);
    const selected=v.document_candidates.find(x=>x.revision===inputs.selected&&x.basis===basis.revision);
    const c=preCard(root,'원문과 수정 원문 비교');
    const ctl=preEl('div');ctl.className='bar';c.append(ctl);
    const abandon=()=>!preDirty()||confirm('현재 편집 중인 내용을 저장하지 않고 비교 대상을 바꿀까요?');
    documentSelect(ctl,'기준 원문',bases,basis.revision,x=>{if(!abandon()){drawEditorial();return}inputs.basis=x;inputs.selected='';inputs.candidate='';inputs.final='';drawEditorial()});
    if(v.document_candidates.length)documentSelect(ctl,'저장된 외부 수정본',[{revision:'',label:'새 수정 원문'},...v.document_candidates.map((d,i)=>({...d,label:'수정본 '+(i+1)}))],inputs.selected,x=>{
        if(!abandon()){drawEditorial();return}const candidate=v.document_candidates.find(c=>c.revision===x);inputs.selected=x;inputs.candidate=candidate?.text||'';inputs.final=candidate?.text||'';if(candidate)inputs.basis=candidate.basis;drawEditorial();
    });
    field(c,'추가 수정 지시 (선택 사항)','instruction',2);
    copyButton(c,'원문 재작성 요청 복사',()=>promptForDocument(v,basis));
    copyButton(c,'기준 원문만 복사',()=>basis.text);
    const pair=preEl('div');pair.className='pre-grid';c.append(pair);
    const left=preCard(pair,'원문 · '+basis.label);
    const orig=preField(left,'현재 기준 원문',basis.text,()=>{},18);orig.readOnly=true;
    const right=preCard(pair,'외부 LLM 수정 원문');
    const a=field(right,'수정된 전체 원문 붙여넣기','candidate',18);
    a.placeholder='외부 LLM에서 받은 실제 수정 원문을 그대로 붙여넣으세요.';
    preButton(right,'수정 원문 저장',()=>preMutate('document_candidate',{text:a.value,basis:basis.revision})).classList.add('primary');
    if(selected)preText(right,'수정 원문 저장됨 · 내용을 다시 바꿨다면 저장 버튼을 누르세요.');
    if(v.pending_reply&&!inputs.candidate){preButton(right,'이전 수신 답변 가져오기',()=>{inputs.candidate=v.pending_reply.raw;drawEditorial()})}
    const final=preCard(root,'최종 확정 원문');final.id='finalDocumentEditor';
    if(selected){
        preText(final,'위 두 원문을 비교한 후 아래 문서를 직접 보완하거나 필요한 문장을 복사하여 조합하세요.');
        const edit=field(final,'최종 원문 (직접 편집 가능)','final',18);
        preButton(final,'수정 원문 전체 사용',()=>{edit.value=selected.text;inputs.final=selected.text});
        preButton(final,'기준 원문 전체 사용',()=>{edit.value=basis.text;inputs.final=basis.text});
        preButton(final,'최종 원문 확정 저장',()=>{
            if(a.value!==selected.text)throw Error('위 수정 원문이 변경되었습니다. 먼저 수정 원문 저장을 눌러 주세요.');
            if(confirm('이 문서를 새 확정본으로 저장할까요? 제작 승인과는 별개입니다.'))return preMutate('document_final',{text:edit.value,candidate:selected.revision,confirmed:true})
        }).classList.add('primary');
    }else preText(final,'오른쪽 수정 원문을 저장하면 여기에 편집 가능한 최종 원문이 나타납니다.');
    const history=preCard(root,'참고 자료 · 필요할 때만 열기');
    if(v.prior_raw)rawDetails(history,'기존 Gemini 비평 원문',v.prior_raw);
    else{const q=field(history,'기존 비평 원문 (있는 경우)','critique',4);preButton(history,'비평 저장',()=>preMutate('prior_capture',{raw:q.value}))}
}
function drawCompare(root,v){
    const c=preCard(root,'원문 확정 이력');
    const bases=documentBases(v);
    if(!v.documents.length){preText(c,'아직 확정 원문이 없습니다. 00A에서 수정 원문을 비교하고 확정하세요.');preButton(c,'원문 비교로 이동',()=>showEditorial('policy'));return}
    const pair=preEl('div'),l=documentSelect(c,'비교 기준',bases,bases[0].revision,compare),r=documentSelect(c,'확정본',bases,bases.at(-1).revision,compare);
    c.append(pair);
    function compare(){pair.replaceChildren();const a=bases.find(x=>x.revision===l.value),b=bases.find(x=>x.revision===r.value);if(a&&b)changeText(pair,a.text,b.text)}
    compare();
    copyButton(c,'선택한 확정 원문 복사',()=>bases.find(d=>d.revision===r.value).text);
    preButton(c,'추가 원문 수정',()=>{inputs.basis=bases.at(-1).revision;inputs.selected='';inputs.candidate='';inputs.final='';showEditorial('policy')});
    preButton(c,'제작 연결 및 독립 검증으로 이동',()=>showEditorial('gate'));
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
    if(v.final_document&&!v.document_linked){
        const c=preCard(root,'확정 원문 저장 완료 · 제작 연결 대기');
        rawDetails(c,'사용자가 확정한 원문',v.final_document.text);
        preText(c,'원문 저장은 끝났습니다. 실제 제작을 시작할 때만 이 문서를 장면·음성 데이터로 연결하고 독립 심사를 진행합니다. 이 과정은 원문을 다시 고치는 작업이 아닙니다.');
        copyButton(c,'확정 원문 제작 연결 요청 복사',()=>promptForCompile(v));
        const a=field(c,'외부 AI 제작 연결 답변 전체','compile',6);
        preButton(c,'제작 데이터 연결',()=>preMutate('document_compile',{raw:a.value}));return;
    }
    if(!v.final_document&&!v.approved){preText(root,'먼저 00A에서 실제 수정 원문을 비교하고 최종 확정본을 저장하세요.');preButton(root,'원문 비교로 이동',()=>showEditorial('policy'));return}
    if(v.final_document&&v.document_linked){const link=preCard(root,'확정 원문과 실제 제작 대본 확인');changeText(link,v.final_document.text,manuscript(v.latest.plan));preText(link,'발화·자막의 원문 포함 여부는 서버가 확인했습니다. 장면 순서, 누락 및 연출 의미 일치는 독립 심사에서 확인합니다.');}
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
    $('preStatus').textContent='원문 V'+v.documents.length+' · 수정 원문 '+v.document_candidates.length+'개 · '+(v.approved?'제작 승인':v.final_document?'원문 확정 · 제작 잠금':'원문 편집 · 제작 잠금');
    if(preMode==='policy')drawDirective(root,v);else if(preMode==='script')drawCompare(root,v);else drawGate(root,v);
    if(v.original.known_failed){const a=preEl('a','기존 실패 영상 다시 보기');a.href=base+p('/baseline');a.target='_blank';a.rel='noopener';root.append(a)}
}
