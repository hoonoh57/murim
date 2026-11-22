'use strict';
// Pre-production authority lives on the server; disabled tabs are only a usability aid.
let editorialState=null,editorialDraft=null,editorialPid=null,preMode='policy',preVisible=true,editorialSerial=0,editorialNote='';
function editorialAllowed(){return !!editorialState?.approved&&editorialPid===doc?.id}
function preDirty(){return editorialDraft&&editorialState&&JSON.stringify(editorialDraft)!==JSON.stringify(editorialState.latest.plan)}
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
    if(changed){editorialPid=d.id;editorialState=null;editorialDraft=null;editorialNote='';preVisible=true;preMode='policy'}
    preLayout();
    const v=await api('/project/'+d.id+'/editorial');
    if(seq!==editorialSerial||doc?.id!==d.id)return;
    const changedToken=editorialState?.token!==v.token;
    editorialState=v;
    if(changed||changedToken||!editorialDraft){editorialDraft=structuredClone(v.latest.plan);editorialNote=''}
    if(!v.approved)preVisible=true;
    preLayout();if(preVisible)drawEditorial();else drawEditorialContext();
}
function showEditorial(mode){preMode=mode;preVisible=true;preLayout();drawEditorial()}
function drawEditorialContext(){const e=$('approvedContext');if(!e||!editorialAllowed())return;const plan=editorialState.latest.plan,shot=plan.scenes.find(s=>s.id===sid);e.textContent=shot?'승인 제작안 '+editorialState.latest.revision.slice(0,12)+'\\n시각: '+shot.visual+'\\n동작: '+(shot.motion||'정지 이미지 중심')+'\\n음향: '+shot.sound+'\\n사료: '+shot.facts:'';}
document.querySelectorAll('[data-pre]').forEach(e=>e.onclick=()=>showEditorial(e.dataset.pre));
$('enterProduction').onclick=()=>{if(editorialAllowed()){if(preDirty()){notice('미저장 제작안을 먼저 저장하거나 새로고침하세요',true);return}preVisible=false;preLayout();setTab('story');showSelected();drawEditorialContext()}};
async function preMutate(kind,data){
    if(kind!=='plan'&&preDirty())throw Error('편집 중인 제작안을 먼저 새 버전으로 저장하세요');
    const id=doc.id;
    await action(async()=>{
        const v=await api('/project/'+id+'/editorial',{token:editorialState.token,action:kind,data});
        if(doc.id!==id)return;
        editorialState=v;editorialDraft=structuredClone(v.latest.plan);editorialNote='';
        if(kind==='approval')update(await api('/project/'+id));
        if(kind==='feedback'){preVisible=true;preMode='gate';$('reviewText').value='';$('structuralIssues').value='';}
        preLayout();drawEditorial();notice('사전 제작 이력 저장 · '+v.status);
    },'사전 제작안 검증 및 저장 중…');
}
const sceneLabels={title:'장면 제목',frames:'길이(초)',narration:'실제 성우 발화 대본 (의도적 무음은 음향 설계에서 설명)',visual:'시각 설계·사용할 원작/이미지/구도',motion:'동작 영상 지시 (정지 이미지면 비움)',sound:'성우·음악·효과음·정적의 설계',facts:'사료 출처·역사 사실/재연 구분',subtitle:'실제 자막'};
function uuidScene(){return Array.from(crypto.getRandomValues(new Uint8Array(6)),n=>n.toString(16).padStart(2,'0')).join('')}
function prePlanSave(root){
    const note=preField(root,'수정 이유와 원본 대비 변경 내용 (필수)',editorialNote,x=>editorialNote=x,3);
    preButton(root,'수정 제작안 새 버전 저장',()=>preMutate('plan',{plan:editorialDraft,note:note.value}));
    preText(root,'미완성 초안도 버전으로 저장할 수 있습니다. 필수 항목을 모두 작성한 저장본만 심사할 수 있습니다. 같은 내용은 새 버전으로 인정하지 않으며 새 버전은 이전 승인을 잠급니다.');
}
function prePrompt(v){
    return '제작 전 독립 편집 심사입니다. 아직 영상·음성은 생성하지 않았습니다. 실제 영상 품질 점수나 예상 합격점은 만들지 마세요. 작품 기획과 실제 장면별 대본의 완결성, 시청자 가치, 사실 출처, 화면·음향 설계, 전체 시나리오와 장면의 일관성을 엄정히 심사하세요. 기존 문제의 해결 여부를 개별 ID와 실제 변경 문장/장면의 근거로 검증하세요. 모든 부족한 점을 issues에 빠짐없이 기록하세요. score는 0~10 또는 자료 부족 null, 근거를 evidence에 기록. 구체적인 결함이나 미확인이 있으면 PASS 금지. 실제 제작안의 독립 판단만 반환하세요. JSON 객체만 반환: '+JSON.stringify({revision:v.latest.revision,scores:Object.fromEntries(v.axes.map(x=>[x,null])),evidence:'축별 판단 근거',issues:['구체적 결함; 없으면 빈 배열'],resolutions:v.issues.map(i=>({id:i.id,resolved:false,evidence:'수정된 원문 증거 또는 미해결 원인'})),verdict:'FAIL 또는 HOLD 또는 PASS'},null,2)+'\n\n미해결 문제:\n'+JSON.stringify(v.issues,null,2)+'\n\n기존 비평 원문(누락 지적사항도 확인):\n'+(v.prior_raw||v.original.prior_summary||'없음')+'\n\n제작 후 구조 결함 비평:\n'+JSON.stringify(v.feedback||[],null,2)+'\n\n심사 대상 제작안:\n'+JSON.stringify(v.latest.plan,null,2);
}
function rewritePanel(root,v){
    const c=preCard(root,'외부 LLM 수정안 작성 · 인간 매개');
    preText(c,'기존 작품/제작안의 모든 실패 원인을 해결하는 새 기획과 실제 시나리오를 요청합니다. 예상 합격점을 만들지 말고 실제 독립 재심사를 받으세요. 외부 전송 권리는 사용자가 확인합니다.');
    const prompt='당신은 이 작품의 수정 담당 감독·작가·미술 및 음향 감독입니다. 이전 실패 결과를 근거로 목적과 시청자 가치, 제작 방침, 전체 실제 시나리오와 장면별 연출을 재설계하세요. 기존 문제 각각을 수정된 내용에 반영하고 역사 사실과 재연 구분, 출처, 미확인 사항을 명시하세요. 확인되지 않은 사료와 권리, 비교작, 데이터와 점수는 발명하지 마세요. 화면·음성 효과를 추가하는 데 그치지 말고 구조적 원인을 고치세요. 전체 실제 대본을 장면 순서에 맞게 작성하세요. 필요하면 장면 추가/삭제·순서 변경을 하되 id는 기존 유지 또는 새 12자리 소문자 16진수. frames는 24fps 정수 24~1440. narration이 비면 sound에 의도적 무음 근거를 명시. motion은 정지 화면이면 빈 문자열. 각 장면 필드 및 제작안 필드의 형식을 그대로 지키세요. JSON 객체 {plan: 완전한 제작안, note: 문제 ID별 원본 대비 구체적 수정 이유와 근거}만 반환하세요. 기존 비평: '+(v.prior_raw||v.original.prior_summary||'미등록')+'\n문제 목록: '+JSON.stringify(v.issues,null,2)+'\n제작 후 비평: '+JSON.stringify(v.feedback||[],null,2)+'\n현재 심사: '+(v.review?.raw||'미실행')+'\n현재 계획 JSON: '+JSON.stringify(v.latest.plan,null,2);
    const request=preField(c,'수정 요청서',prompt,()=>{},7);request.readOnly=true;
    preButton(c,'수정 요청서 복사',async()=>{await navigator.clipboard.writeText(request.value);notice('수정 요청서 복사 · 외부 LLM과 인간 매개')});
    const response=preField(c,'외부 수정안 JSON 붙여넣기 (아직 저장·승인되지 않음)','',()=>{},7);
    preButton(c,'수정안 초안으로 불러오기',()=>{
        const result=JSON.parse(response.value),candidate=result.plan;
        const sameKeys=(a,b)=>a&&typeof a==='object'&&Object.keys(a).sort().join(',')===Object.keys(b).sort().join(',');
        if(!sameKeys(candidate,v.latest.plan)||!Array.isArray(candidate.scenes)||!candidate.scenes.length||candidate.scenes.some(s=>!sameKeys(s,v.latest.plan.scenes[0]))||typeof result.note!=='string')throw Error('제작안 JSON 형식 불일치');
        if(Object.keys(v.fields).some(k=>typeof candidate[k]!=='string')||candidate.scenes.some(s=>typeof s.frames!=='number'||Object.keys(s).some(k=>k!=='frames'&&typeof s[k]!=='string')))throw Error('제작안 필드 유형 오류');
        editorialDraft=structuredClone(candidate);editorialNote=result.note;showEditorial('policy');notice('외부 수정안 초안 로드 · 직접 검토 및 새 버전 저장 필요');
    });
}
bind('returnEditorial',async()=>{
    if(!editorialAllowed())throw Error('현재 승인된 제작안이 필요합니다');
    const render=$('renders').value,raw=$('reviewText').value,issues=$('structuralIssues').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
    if(!render||!raw.trim()||!issues.length)throw Error('실제 렌더·비평 원문·구조적 결함 목록 모두 입력하세요');
    if(confirm('현재 제작 승인을 취소하고 기획·시나리오 재심사로 돌아갈까요? 기존 산출물은 보존됩니다.'))await preMutate('feedback',{render,raw,issues});
});
function drawEditorial(){
    const v=editorialState,root=$('prePanel');root.replaceChildren();
    if(!v||!editorialDraft){$('preStatus').textContent='사전 제작 상태 조회 중';return}
    $('preStatus').textContent=v.status+' · 원본 포함 '+v.versions.length+'개 제작안 · 미해결 '+v.issues.length+'개 · '+(v.approved?'제작 진입 가능':'제작 잠금');
    if(preMode==='policy'){
        preText(root,'기획과 시나리오를 확정한 후에만 제작합니다. 실제 영상 심사와 기획 심사는 별도입니다.');
        for(const [k,label] of Object.entries(v.fields))preField(root,label,editorialDraft[k],x=>editorialDraft[k]=x);
        prePlanSave(root);
        preButton(root,'시나리오·장면 설계로 이동',()=>showEditorial('script'));
        if(!preDirty())rewritePanel(root,v);
    }else if(preMode==='script'){
        preText(root,'이 장면 목록의 순서·제목·길이·실제 발화 대본이 승인 후 타임라인에 반영됩니다. 기존 실패 장면의 미디어는 자동 배치하지 않습니다.');
        editorialDraft.scenes.forEach((s,i)=>{
            const c=preCard(root,(i+1)+'. '+s.title);
            for(const [k,label] of Object.entries(sceneLabels)){
                if(k==='frames'){const l=preEl('label',label),n=preEl('input');n.type='number';n.min='1';n.max='60';n.step='0.0416667';n.value=s.frames/24;n.oninput=()=>s.frames=Math.round(Number(n.value)*24);l.append(n);c.append(l)}
                else preField(c,label,s[k],x=>s[k]=x,k==='title'?1:3);
            }
            if(i>0)preButton(c,'↑ 장면 순서',()=>{[editorialDraft.scenes[i-1],editorialDraft.scenes[i]]=[s,editorialDraft.scenes[i-1]];drawEditorial()});
            if(i+1<editorialDraft.scenes.length)preButton(c,'↓ 장면 순서',()=>{[editorialDraft.scenes[i+1],editorialDraft.scenes[i]]=[s,editorialDraft.scenes[i+1]];drawEditorial()});
            if(editorialDraft.scenes.length>1)preButton(c,'장면 제거',()=>{if(confirm('초안에서 장면을 제거할까요?')){editorialDraft.scenes.splice(i,1);drawEditorial()}});
        });
        preButton(root,'+ 새 장면',()=>{editorialDraft.scenes.push({id:uuidScene(),title:'새 장면',frames:144,narration:'',visual:'',motion:'',sound:'',facts:'',subtitle:''});drawEditorial()});
        prePlanSave(root);
    }else{
        if(preDirty()){preText(root,'저장되지 않은 기획 또는 시나리오가 있습니다. 먼저 새 버전을 저장해야 심사할 수 있습니다.');prePlanSave(root);return}
        const original=preCard(root,'기존 실제 작품의 비평 · 원본 보존');
        if(v.original.prior_summary)preText(original,v.original.prior_summary);
        if(v.prior_raw)original.append(preEl('pre',v.prior_raw));
        else if(!v.review){
            const raw=preField(original,'Gemini 기존 비평 원문 붙여넣기','',()=>{},6);
            const issues=preField(original,'원문에서 확인한 모든 결함 (한 줄에 한 건; 요약 누락 확인)','',()=>{},5);
            preButton(original,'기존 비평 원문 및 결함 등록',()=>preMutate('prior_review',{raw:raw.value,issues:issues.value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean)}));
        }
        for(const f of (v.feedback||[])){const fc=preCard(root,'실제 영상에서 돌아온 비평 · '+f.source.render);preText(fc,'영상 SHA-256 '+f.source.sha256);fc.append(preEl('pre',f.raw))}
        const todo=preCard(root,'미해결 결함 (새 수정본의 재심사에서 검증)');
        for(const i of v.issues)preText(todo,i.id+' · '+i.description);
        if(!v.issues.length)preText(todo,'등록된 미해결 결함 없음. 독립 심사 및 인간 승인은 별도.');
        const comparison=preCard(root,'프로젝트별 원본 / 수정본 비교');
        const select=preEl('select');for(const [i,p] of v.versions.entries()){const o=preEl('option',(i+1)+' · '+p.revision.slice(0,12)+' · '+p.note);o.value=String(i);select.append(o)}select.value=String(v.versions.length-1);comparison.append(select);
        const pair=preEl('div');pair.className='pre-grid';comparison.append(pair);
        function compare(){pair.replaceChildren();for(const [name,p] of [['원본',v.versions[0]],['비교본',v.versions[Number(select.value)]]]){const c=preCard(pair,name);c.append(preEl('pre',JSON.stringify(p.plan,null,2)));if(p.review){preText(c,'심사 '+p.review.reviewer+' · '+(p.review.total===null?'미평가':p.review.total.toFixed(1)+'/100')+' · '+(p.review.pass?'PASS':'FAIL/HOLD'));c.append(preEl('pre',p.review.raw))}}}
        select.onchange=compare;compare();
        if(v.review){const c=preCard(root,'현재 버전 독립 심사 결과');preText(c,v.review.reviewer+' · '+(v.review.total===null?'미평가':v.review.total.toFixed(1)+'/100')+' · '+(v.review.pass?'PASS':'FAIL/HOLD'));c.append(preEl('pre',v.review.raw))}
        else if(!v.latest.original&&v.ready){
            const c=preCard(root,'Gemini 등 독립 심사 · 인간 매개');
            const prompt=preField(c,'저장된 수정본 심사 요청서',prePrompt(v),()=>{},8);prompt.readOnly=true;
            preButton(c,'심사 요청서 복사',async()=>{await navigator.clipboard.writeText(prompt.value);notice('복사 완료: 별도 독립 세션에 전달하세요')});
            const who=preField(c,'심사 모델·버전 / 독립 세션 식별자','',()=>{},1);
            const raw=preField(c,'심사 응답 JSON 원문','',()=>{},8);
            preButton(c,'독립 심사 원문 등록',()=>preMutate('review',{reviewer:who.value,raw:raw.value}));
        }
        rewritePanel(root,v);
        if(!v.review&&!v.ready)preText(root,'기획·시나리오 필수 항목이 아직 미완성입니다. 00A/00B에서 작성한 수정본을 저장하세요.');
        if(v.review?.pass&&!v.approved){
            const c=preCard(root,'최종 인간 승인 · 승인된 장면 설계 전달');
            preText(c,'심사 95점 이상, 모든 축 9점 이상, 미해결 결함 0건을 서버에서 확인합니다. 실제 응답·결함 해결 증거·사료·시나리오 일치 여부를 직접 검토하세요.');
            const approver=preField(c,'승인자','',()=>{},1),label=preEl('label'),check=preEl('input');check.type='checkbox';label.append(check,document.createTextNode('모든 문제의 실제 해결과 수정안을 검토했고 이 버전의 제작을 승인합니다.'));c.append(label);
            preButton(c,'승인 및 타임라인 생성',()=>{if(!check.checked)throw Error('인간 승인 확인 필요');return preMutate('approval',{confirmed:true,approver:approver.value,mvml_revision:v.mvml_revision})});
        }
        if(v.approved)preText(root,'승인된 버전: '+v.latest.revision+' · 실제 결과물 품질 심사는 별도.');
        preText(root,'기준 원본 M-VML 리비전: '+v.original.source_revision);
        if(v.original.known_failed){const a=preEl('a','기존 실패 작품 A 재생 (읽기 전용)');a.href=base+p('/baseline');a.target='_blank';a.rel='noopener';root.append(a)}
    }
}
