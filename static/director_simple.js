/* GPT-style facade. Human-relay actions only until the underlying workflow is validated. */
(() => {
"use strict";
const $ = id => document.getElementById(id);
const token = document.body.dataset.token;
const root = "/studio/simple/api";
const studioRoot = "/studio/api";
let project = null, director = null, directorToken = "", editorial = null, ready = false, stage = "scenario", productions = [];

function say(message, bad=false) { $("message").textContent=message; $("message").classList.toggle("error",!!bad); }
function node(tag, text, className) { const el=document.createElement(tag); if(text!==undefined)el.textContent=text; if(className)el.className=className; return el; }
function button(text, onClick, cls) { const el=node("button",text,cls);el.type="button";el.onclick=()=>Promise.resolve().then(onClick).catch(fail);return el; }
function fail(err) { say(err.message||String(err),true); }
async function api(path, obj) {
  const options = obj===undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json","X-Murim-Studio":token},body:JSON.stringify(obj)};
  const response = await fetch(root+path,options);
  const value = await response.json();
  if(!response.ok || value.error) throw Error(value.error || "HTTP "+response.status);
  return value;
}
async function studio(path, body) {
  const response=await fetch(studioRoot+path,{method:"POST",headers:{"X-Murim-Studio":token},body});
  const value=await response.json();
  if(!response.ok||value.error)throw Error(value.error||"등록 실패");
  return value;
}
function route(suffix) { if(!project)throw Error("프로젝트를 선택하세요");return "/project/"+project.id+suffix; }
function clear(el) { el.replaceChildren(); }
function option(value,text){const el=node("option",text);el.value=value;return el;}
function id16(s){return String(s||"").slice(0,12);}
async function refreshProjects(preferred) {
  const r=await api("/projects"), sel=$("projects"), show=$("showArchived").checked;
  const selected=preferred || project?.id || "";
  sel.replaceChildren(option("","작품 선택"));
  for(const p of r.projects)if(show||!p.archived)sel.append(option(p.id,p.title+(p.archived?" (보관)":"")));
  if(Array.from(sel.options).some(x=>x.value===selected))sel.value=selected;
  else if(!preferred&&sel.options.length>1)sel.selectedIndex=1;
}
async function load(pid) {
  if(!pid){$("workspace").hidden=true;project=null;return;}
  const r=await api("/project/"+pid);
  project=r.project;director=r.director;directorToken=r.director_token;editorial=r.editorial;ready=r.storyboard_ready;
  $("projects").value=pid;$("newTitle").value=project.title;
  $("workspace").hidden=false;
  $("archive").textContent=director.archived?"보관 해제":"보관";
  $("editorialStatus").textContent=editorial.approved?"G1/G2 시나리오 승인됨":"제작 보류 · "+editorial.status;
  drawScenes();drawGallery();drawStage();
  say(project.title+" · "+(editorial.approved?"시나리오 승인":"시나리오 감수 필요")+(ready?" · 스토리보드 확정":""));
}
function drawScenes() {
  const box=$("scenarioScenes");clear(box);
  for(const s of editorial.scenes){
    const row=node("div",undefined,"scene-card"),span=node("div");
    span.append(node("strong",s.title),node("small",(s.frames/24).toFixed(1)+"초 · "+(s.visual||"시각 설명 없음")));
    row.append(span);box.append(row);
  }
  $("editorialStatus").textContent=editorial.approved?"시나리오 정식 승인 · 이미지 후보 선정 가능":"G1/G2 품질 잠금 · 기존 Studio에서 사람 매개 심사와 최종 승인을 완료하세요";
}
function drawGallery() {
  const rootEl=$("candidateGallery");clear(rootEl);
  const headings={character:"주인공·등장인물",style:"화풍",prop:"소품",location:"장소"};
  const slots=["character","style","prop","location",...editorial.scenes.map(s=>"scene:"+s.id)];
  for(const slot of slots) {
    const wrap=node("section",undefined,"gallery-section");
    const title=slot.startsWith("scene:") ? "스토리보드 · "+(editorial.scenes.find(s=>s.id===slot.slice(6))?.title||slot) : headings[slot];
    wrap.append(node("h3",title));
    const items=director.candidates.filter(c=>c.slot===slot);
    if(!items.length){wrap.append(node("p","등록된 후보 없음","hint"));rootEl.append(wrap);continue;}
    const grid=node("div",undefined,"candidate-grid");
    for(const c of items) {
      const chosen=director.selected[slot]===c.id;
      const card=node("div",undefined,"candidate"+(chosen?" selected":""));
      const image=node("img");image.alt=c.label||"등록 이미지";image.loading="lazy";
      image.src=studioRoot+route("/asset/"+c.asset);
      const caption=node("strong",c.label||c.asset.slice(0,14));
      card.append(image,caption,button(chosen?"✓ 선택됨":"이 이미지 선택",async()=>{
        const result=await api(route("/select"),{director_token:directorToken,candidate:c.id});
        directorToken=result.director_token;await load(project.id);stage="board";drawStage();
      },chosen?"primary":""));
      grid.append(card);
    }
    wrap.append(grid);rootEl.append(wrap);
  }
  const missing=["character","style",...editorial.scenes.map(s=>"scene:"+s.id)].filter(s=>!director.selected[s]);
  $("boardStatus").textContent=ready?"VML 확정 완료 · 참조 이미지 연결됨":missing.length?"미선정 "+missing.length+"개 · 주인공·화풍·모든 장면 이미지를 선택하세요":"모든 필수 이미지 선택됨 · 확정할 수 있습니다";
  $("confirmBoard").disabled=!editorial.approved||director.archived||(!missing.length&&ready)||!!missing.length;
}
function drawStage() {
  document.querySelectorAll("[data-stage]").forEach(b=>b.classList.toggle("active",b.dataset.stage===stage));
  $("scenarioPanel").hidden=stage!=="scenario";$("boardPanel").hidden=stage!=="board";$("productionPanel").hidden=stage!=="production";
  $("stepBoard").disabled=!editorial.approved;$("stepProduction").disabled=!ready;
  const sceneSelect=$("scenePick"),prodSelect=$("productionScene");
  const prior=sceneSelect.value, before=prodSelect.value;
  for(const sel of [sceneSelect,prodSelect]){
    sel.replaceChildren();
    for(const scene of editorial.scenes)sel.append(option(scene.id,scene.title));
  }
  if(editorial.scenes.some(s=>s.id===prior))sceneSelect.value=prior;
  if(editorial.scenes.some(s=>s.id===before))prodSelect.value=before;
  $("scenePickLabel").hidden=$("role").value!=="scene";
  if(stage==="production"&&ready) refreshProduction().catch(fail);
}
async function refreshProduction() {
  const r=await api(route("/production"));productions=r.shots;clear($("productionList"));
  for(const shot of r.shots){
    const row=node("div",undefined,"scene-card"),label=node("div");
    label.append(node("strong",shot.title),node("small",shot.seconds.toFixed(1)+"초 · "+(shot.video_asset?"실제 영상 후보 등록됨":"사람매개 영상 생성 필요")));
    row.append(label,button(shot.video_asset?"영상 후보 보기":"동작 지시문",()=>shot.video_asset?showCandidate(shot):showPrompt("motion",shot.id)));
    $("productionList").append(row);
  }
  $("resultStatus").textContent="제작 상태: "+r.state+" · 자동 영상 품질 검증은 미완료";
  await renderList();
}
function showCandidate(shot){
  const video=$("resultVideo");video.src=studioRoot+route("/asset/"+shot.video_asset);
  video.hidden=false;$("resultEmpty").hidden=true;
  $("resultStatus").textContent="생성 후보 · 실제 영상 ("+shot.title+") · 품질 승인 전";
}
async function renderList() {
  const r=await fetch(studioRoot+route("/renders")).then(x=>x.json());
  const box=$("renderList");clear(box);
  for(const entry of r.renders||[])box.append(button("저장된 렌더 · "+id16(entry.id),()=>{
    const video=$("resultVideo");video.src=studioRoot+route("/render/"+entry.id);
    video.hidden=false;$("resultEmpty").hidden=true;
    $("resultStatus").textContent="실제 렌더 · "+entry.id+" · 작품성 승인과 별개";
  }));
}
function go(name){if(name==="board"&&!editorial.approved){say("시나리오 G1/G2 정식 승인부터 진행하세요",true);return;}
  if(name==="production"&&!ready){say("스토리보드 이미지 확정 후 진행하세요",true);return;}
  stage=name;drawStage();}
async function showPrompt(mode,scene){
  if(!project)throw Error("프로젝트를 선택하세요");
  const extra=mode==="motion"?"&scene="+encodeURIComponent(scene||$("productionScene").value):"";
  const r=await api(route("/relay")+"?mode="+mode+extra);
  $("relayText").value=r.prompt+($("instruction").value.trim()?"\n\n감독 추가 지시:\n"+$("instruction").value.trim():"");
  say("인간매개 프롬프트 준비됨 · GPT에 전달하고 실제 생성된 결과만 등록하세요");
}
async function copyPrompt(){
  const text=$("relayText").value;
  if(!text)throw Error("먼저 프롬프트를 생성하세요");
  if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(text);
  else{$("relayText").focus();$("relayText").select();if(!document.execCommand("copy"))throw Error("브라우저에서 직접 복사하세요");}
  say("프롬프트 복사 완료");
}
$("create").onclick=async()=>{
  try{
    const title=$("newTitle").value.trim();const r=await api("/projects",{title});
    await refreshProjects(r.id);stage="scenario";await load(r.id);
  }catch(e){fail(e);}
};
$("reload").onclick=async()=>{try{stage="scenario";await load($("projects").value);}catch(e){fail(e);}};
$("projects").onchange=()=>{stage="scenario";load($("projects").value).catch(fail);};
$("showArchived").onchange=()=>refreshProjects().catch(fail);
$("rename").onclick=async()=>{try{
  if(!project)throw Error("프로젝트를 열어 주세요");
  await api(route("/project-action"),{action:"rename",title:$("newTitle").value,revision:project.revision,director_token:directorToken});
  await refreshProjects(project.id);await load(project.id);
}catch(e){fail(e);}};
$("archive").onclick=async()=>{try{
  if(!project)throw Error("프로젝트를 열어 주세요");
  if(!window.confirm(director.archived?"보관 해제하시겠습니까?":"프로젝트를 보관할까요? 실제 원본 파일은 삭제되지 않습니다."))return;
  const action=director.archived?"restore":"archive";
  await api(route("/project-action"),{action,director_token:directorToken});
  await refreshProjects();await load(project.id);
}catch(e){fail(e);}};
$("stepScenario").onclick=()=>go("scenario");$("stepBoard").onclick=()=>go("board");$("stepProduction").onclick=()=>go("production");
$("openEditorial").onclick=()=>{if(!project)return fail(Error("프로젝트 선택 필요"));$("editorialFrame").src="/studio/";$("editorialDialog").showModal();};
$("closeEditorial").onclick=()=>{$("editorialDialog").close();$("editorialFrame").src="about:blank";load(project.id).catch(fail);};
$("role").onchange=()=>{$("scenePickLabel").hidden=$("role").value!=="scene";};
$("buildPrompt").onclick=()=>showPrompt(stage==="scenario"?"scenario":stage==="board"?"storyboard":"motion").catch(fail);
$("copyPrompt").onclick=()=>copyPrompt().catch(fail);
$("imageForm").onsubmit=async e=>{e.preventDefault();try{
  if(!editorial?.approved)throw Error("시나리오 승인 필요");
  const file=$("imageFile").files[0];if(!file)throw Error("이미지를 선택하세요");
  const data=new FormData();data.append("file",file);data.append("kind","image");data.append("source",$("imageSource").value.trim());data.append("rights",$("imageRights").value.trim());data.append("revision",project.revision);
  say("이미지 후보를 등록하고 있습니다...");
  const result=await studio(route("/asset"),data);
  const role=$("role").value;const x=await api(route("/candidate"),{director_token:directorToken,role,scene:role==="scene"?$("scenePick").value:null,asset:result.imported,label:$("imageLabel").value.trim()||file.name});
  directorToken=x.director_token;
  await load(project.id);stage="board";drawStage();$("imageFile").value="";
  say("실제 이미지 에셋 등록 완료 · 후보를 선택하세요");
}catch(err){fail(err);}};
$("confirmBoard").onclick=async()=>{try{
  if(!window.confirm("시나리오와 선택한 모든 스토리보드 이미지를 확정하여 VML에 반영할까요?"))return;
  await api(route("/confirm"),{director_token:directorToken,revision:project.revision,confirmed:true,approver:"로컬 사용자 명시 승인"});
  stage="production";await load(project.id);say("스토리보드 선택이 VML에 반영됐습니다 · 영상 모델 검증 전 인간매개 경로");
}catch(e){fail(e);}};
$("videoForm").onsubmit=async e=>{e.preventDefault();try{
  if(!ready)throw Error("스토리보드 승인 필요");
  const file=$("videoFile").files[0];if(!file)throw Error("실제 영상 파일을 선택하세요");
  const sid=$("productionScene").value;
  const data=new FormData();data.append("file",file);data.append("kind","video");data.append("source",$("videoSource").value.trim());data.append("rights",$("videoRights").value.trim());data.append("revision",project.revision);
  say("영상 무결성과 재생 정보를 확인하고 등록합니다...");
  const result=await studio(route("/asset"),data);
  await api(route("/attach-video"),{revision:result.revision,scene:sid,asset:result.imported});
  await load(project.id);stage="production";drawStage();say("실제 영상 후보를 등록했습니다 · 시청 품질 승인은 별도");
}catch(err){fail(err);}};
refreshProjects().then(async()=>{
  if($("projects").value){stage="scenario";await load($("projects").value);}
}).catch(fail);
})();
