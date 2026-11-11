// Standalone continuation of the supplied November 8 handoff.
// Presentation and source review only. Frozen DATA is never rewritten.
const completionRoomCameras=new Set(['isometric','r062-primary-shell',
 'r063-bath-finish','r067-powder-survey','r067-wc-survey']);
let completionManualCamera=false;
let completionFraming=false;
let completionSafeRect=null;

function sourceReview(room=current(),inst=instance()){
 const audited=nativeSourceReview(room,inst);if(audited)return audited;
 const a=inst?.architecture,plan=room?.full_room_plan||{},holds=[];
 const area=a?{wallFaceSF:a.floor_polygon_area_ft2,
  drawingStudySF:a.drawing_display_area_ft2,
  historicalSF:plan.source_floor_area_ft2,
  differencePercent:a.drawing_vs_wall_face_difference_percent,
  unresolved:Boolean(a.area_conflict_flag)}:null;
 if(area?.unresolved)holds.push('Room area and adjacency remain unresolved.');
 const kind=room?.program?.kind;
 if(kind==='PRIMARY_WALK_IN_LINEAR')holds.push('Basin, shower and linear-drain installation: UNLOCATED.');
 if(kind==='TUB_OR_WALK_IN_UNSELECTED')holds.push('Tub versus walk-in: UNSELECTED. The plan symbol is a reference.');
 if(a?.selected_tub_unlocated_reason)holds.push('Selected tub: 3D UNLOCATED. No installed tub is shown.');
 if(room?.id==='PH-POWDER')holds.push('Basin: UNLOCATED. Its illustrative footprint does not fit the native countertop bounds.');
 if(room?.id==='TX-POWDER')holds.push('Wall finish: NO PICK. Basin and faucet are not selected or located.');
 if(room?.id==='TX-POWDER2')holds.push('Basin: UNSELECTED. Selected faucet installation: UNLOCATED.');
 if(room?.id==='PH-BATH4')holds.push('311 is the wet room; 310 is separate context. The historic material pool stays combined once.');
 const wc=wcSourceAnchors(inst).length>0;
 if(wc)holds.push(state.fixtureStudies?
  'Generic WC study shown; body, offset and mounting are unverified. Native insertion remains available in Source lines.':
  'WC body and support are unverified. Native insertion plan locators are shown; optional 3D studies remain available.');
 if(a?.selected_tub_proxy)holds.push('Tub footprint is nominal and source-fitted; its body, depth and connections are illustrative.');
 return {room:room?.id,instance:inst?.room_number,area,holds,
  roomMembershipCertified:false,geometryBasis:'Saved native wall curves and hosted openings; room assignment inferred',
  nativeWallIds:[...(a?.native_wall_ids||[])],wallReceipt:a?.wall_receipt_id||null,
  fixtureStudies:Boolean(state.fixtureStudies),hasWC:wc,
  liveRevitVerified:false,selectionDataChanged:false};
}

function installViewerCompletion(){
 state.fixtureStudies=false;
 const sheet=document.createElement('style');
 sheet.textContent=`
 button:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{outline:2px solid #efcba1;outline-offset:3px}
 #viewer-v2-toolbar{top:144px;max-width:calc(100% - 42px);right:20px;align-items:flex-start}
 #viewer-view-options{position:relative;color:#edf4f7;font-size:11px}
 #viewer-view-options>summary{list-style:none;cursor:pointer;min-height:30px;display:flex;align-items:center;gap:7px}
 #viewer-view-options>summary::after{content:'▾';color:#c7a985}
 #viewer-view-options[open]>summary::after{content:'▴'}
 .viewer-secondary-controls{position:absolute;top:37px;left:0;display:flex;flex-wrap:wrap;gap:7px;width:310px;max-width:calc(100vw - 32px);max-height:280px;overflow:auto;padding:14px;background:#14212ef8;border:1px solid #82919a;border-radius:7px;box-shadow:0 12px 30px #07121e99;z-index:18}
 #viewer-view-options[open]{z-index:18}
 #stage .stage-top{top:20px;left:20px;right:20px}
 #stage .stage-top>div:first-child{max-width:calc(100% - 180px)}
 #stage .stage-top .scene-note{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:11px}
 #stage .stage-top .alert{max-width:170px;font-size:10px;line-height:1.4}
 #viewer-v2-info{display:none}
 #viewer-v2-fidelity{max-height:44px;bottom:72px;font-size:10px;line-height:1.45}
 #viewer-source-review{padding:13px 14px;margin:14px 0;background:#1b2832;border:1px solid #596a72;border-left:3px solid #ccb08b;border-radius:5px;font-size:11px;line-height:1.6}
 #viewer-source-review strong{color:#f0d3ad;font-size:12px}
 #viewer-source-review .source-area{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0}
 #viewer-source-review .source-area span{color:#a9b8c3;font-size:10px;display:block}
 #viewer-source-review .source-area b{display:block;color:#eef1ed;font-size:15px;font-variant-numeric:tabular-nums}
 #viewer-source-review p{margin:6px 0;color:#c4cfd5}
 #viewer-source-review button{padding:0;border:0;background:none;color:#e9c99e;text-decoration:underline;text-underline-offset:3px;font:inherit;cursor:pointer}
 #viewer-v2-source{font-size:11px;line-height:1.55}
 #viewer-v2-source strong{color:#d8e2e5}
 #viewer-source-holds{margin:8px 0 0;padding-left:16px;color:#b7c6ce}
 #viewer-source-holds li{margin-top:7px}
 #viewer-focus-bar{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;max-width:calc(100% - 32px);scroll-padding-inline-start:95px}
 #viewer-focus-bar>*{flex-shrink:0}
 #viewer-focus-exit{position:sticky;left:0;z-index:4;box-shadow:6px 0 8px #0d1c29e8}
 #viewer-focus-caption{max-width:calc(100% - 36px);font-size:10px;line-height:1.5}
 #stage.viewer-focus-active>#viewer-v2-toolbar{display:none!important}
 .viewer-study-legend{position:absolute;z-index:9;right:18px;bottom:116px;max-width:250px;padding:9px 12px;color:#d6e0e4;background:#10212ce8;border:1px solid #647a86;border-radius:5px;font-size:10px;line-height:1.6;pointer-events:none}
 .viewer-study-legend[hidden]{display:none}
 .viewer-study-legend strong{color:#e9c99e}
 #stage.viewer-focus-active .viewer-study-legend{bottom:104px}
 @media(max-width:1200px) and (min-width:861px){#stage .stage-top>div:first-child{max-width:100%}#stage .stage-top .alert{display:none}h1{font-size:22px}}
 @media(max-width:860px){
  #app{grid-template-rows:60px 68px minmax(560px,1fr) auto}
  #room-list{display:flex;gap:5px}
  #room-list .room-btn{flex:0 0 auto;min-width:145px}
  aside.right{overflow:visible;padding:24px 18px}
  #stage{height:calc(100svh - 128px);min-height:560px}
  .brand{font-size:12px}.brand small{font-size:8px;letter-spacing:.14em}.tag{font-size:9px;white-space:nowrap}
  #stage .stage-top{top:12px;left:12px;right:12px}
  #stage .stage-top>div:first-child{width:100%;max-width:100%;padding:10px 12px}
  #stage .stage-top h1{font-size:19px;margin:5px 0}
  #stage .stage-top .scene-note{display:none}
  #stage .stage-top .alert{display:none}
  #viewer-v2-toolbar{top:94px;left:12px;right:12px;max-width:calc(100% - 24px);gap:5px}
  #viewer-v2-toolbar>.viewer-select{max-width:140px}
  #viewer-v2-toolbar>.viewer-btn,#viewer-view-options>summary{min-height:33px}
  .viewer-secondary-controls{position:fixed;top:285px;left:12px;right:12px;width:auto;max-height:40svh}
  #stage>.tools{top:auto;bottom:72px;left:12px;right:auto;flex-direction:row;gap:5px}
  #stage>.tools .tool{font-size:10px;min-width:0;padding:7px 9px}
  #viewer-v2-fidelity{left:12px;right:12px;bottom:112px;max-height:34px;padding:5px 8px;font-size:9px}
  .stage-bottom{left:12px;right:12px;bottom:12px}
  .stage-bottom .hud{padding:7px 9px;font-size:10px;max-width:100%}
  .stage-bottom #model-count{display:none}
  #viewer-focus-bar{left:8px;right:8px;max-width:calc(100% - 16px);padding:8px}
  #viewer-focus-room-label{display:none}
  #viewer-focus-bar .viewer-select{max-width:120px}
  #viewer-focus-bar .viewer-btn,#viewer-focus-bar .viewer-select{min-height:35px}
  #viewer-focus-caption{left:12px;bottom:51px;max-width:calc(100% - 24px);font-size:9px;padding:6px 8px;letter-spacing:0}
  .viewer-study-legend{right:12px;bottom:156px;font-size:9px;max-width:195px;padding:6px 8px}
  #stage.viewer-focus-active .viewer-study-legend{bottom:120px}
 }
 `;
 document.head.append(sheet);
 const options=document.createElement('details');options.id='viewer-view-options';
 options.innerHTML='<summary class="viewer-btn">Camera & source</summary><div class="viewer-secondary-controls" role="group" aria-label="Camera and source controls"></div>';
 const primary=new Set(['viewer-instance','viewer-mode-full','viewer-mode-study',
  'viewer-mode-context','viewer-compare-ab','viewer-focus-enter']);
 for(const child of [...toolbar.children])if(!primary.has(child.id))options.lastElementChild.append(child);
 toolbar.append(options);
 toolbar.setAttribute('aria-label','Bathroom view controls');
 const wcButton=document.createElement('button');wcButton.id='viewer-fixture-studies';
 wcButton.className='viewer-btn';wcButton.type='button';
 wcButton.title='Optional generic WC bodies: appearance studies with unverified mounting and installation. No new native geometry.';
 options.lastElementChild.prepend(wcButton);
 const galleryButton=document.createElement('button');galleryButton.id='viewer-open-gallery';
 galleryButton.type='button';galleryButton.className='viewer-btn';galleryButton.textContent='Room gallery';
 galleryButton.onclick=()=>{options.open=false;gallery().catch(e=>runtimeErrors.push('GALLERY: '+e.message));};
 options.lastElementChild.append(galleryButton);
 const focusButton=wcButton.cloneNode(true);focusButton.id='viewer-focus-fixture-studies';
 document.getElementById('viewer-focus-traces').after(focusButton);
 wcButton.onclick=focusButton.onclick=()=>{
  state.fixtureStudies=!state.fixtureStudies;applyFixtureStudyVisibility();
  updateCompletionSummary();renderer.render(scene,camera);
 };
 const legend=document.createElement('div');legend.className='viewer-study-legend';
 legend.id='viewer-fixture-legend';legend.hidden=true;stage.append(legend);
 const review=document.createElement('section');review.id='viewer-source-review';
 review.setAttribute('aria-label','Source review and placement holds');programLabel.before(review);
 const canvasLabel='Interactive bathroom study. Drag to orbit, Shift and drag to pan, scroll to zoom.';
 canvas.setAttribute('aria-label',canvasLabel);canvas.setAttribute('role','img');
 document.querySelector('.side-note').textContent='13 bathroom types · 26 physical A/B instances. Saved Revit wall and opening evidence, with inferred room membership. Fixture installation holds remain explicit.';
 document.querySelector('.foot').textContent='Saved read-only Revit evidence. Native wall positions and category bounds are distinct from inferred room footprints and illustrative fixtures. Maker imagery is a digital finish proxy. This viewer changes no Revit or procurement records.';
 document.getElementById('error').textContent='This offline viewer needs a WebGL-enabled browser. No internet connection or Revit file is required.';
 // Emissive cards are in a separate synthetic studio environment, never in
 // modelGroup or source evidence. They create readable ceramic reflections
 // without inventing bathroom windows, ceiling fittings or material picks.
 const oldEnvironment=scene.environment;
 const studio=new THREE.Scene();studio.background=new THREE.Color(0x777f83);
 for(const [position,size,intensity] of [
  [[-9,7,5],[5,10],3.8],[[7,8,-5],[8,5],2.3],[[0,15,0],[8,10],3.0]]){
  const card=new THREE.Mesh(new THREE.PlaneGeometry(...size),
   new THREE.MeshBasicMaterial({color:new THREE.Color(1,.96,.90).multiplyScalar(intensity),side:THREE.DoubleSide}));
  card.position.fromArray(position);card.lookAt(0,3,0);studio.add(card);
 }
 const environmentTarget=pmrem.fromScene(studio,.08,.1,80);
 scene.environment=environmentTarget.texture;oldEnvironment?.dispose();
 studio.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 orbit.addEventListener('start',()=>{completionManualCamera=true;});
 options.addEventListener('toggle',()=>{
  if(options.open&&state.compareAB){state.compareAB=false;updateABCompare();updateFocusViewControls();}
 });
 document.addEventListener('keydown',e=>{if(e.key==='Escape')options.open=false;});
 document.addEventListener('pointerdown',e=>{
  if(options.open&&!options.contains(e.target))options.open=false;
 });
 completionInstalled=true;
 Object.assign(window.__viewerDebug,{getSourceReview:sourceReview,
  getCompletionEvidence:completionEvidence,
  setFixtureStudies:enabled=>{state.fixtureStudies=Boolean(enabled);applyFixtureStudyVisibility();updateCompletionSummary();}});
}

function updateCompletionSummary(){
 const review=sourceReview();
 const area=review.area;
 const fmt=v=>Number.isFinite(v)?v.toFixed(2):'Unknown';
 document.getElementById('viewer-source-review').innerHTML=
  '<strong>'+htmlEscape(review.instance)+' · Source review</strong>'+
  (area?.unresolved?'<div class="source-area"><div><span>Derived wall-face area</span><b>'+fmt(area.wallFaceSF)+' SF</b></div><div><span>Drawing study area</span><b>'+fmt(area.drawingStudySF)+' SF</b></div></div><p>Area / room attribution unresolved ('+fmt(area.differencePercent)+'% difference). Historical quantities are unchanged.</p>':'<p>Native walls and hosted openings retained. Room membership remains inferred.</p>')+
  '<button type="button" id="viewer-open-source-holds">'+review.holds.length+' placement / source note'+(review.holds.length===1?'':'s')+' →</button>';
 document.getElementById('viewer-open-source-holds').onclick=()=>{
  roomEvidence.open=true;roomEvidence.scrollIntoView({block:'nearest',behavior:'smooth'});
 };
 const originalProgram=programLabel.dataset.fullProgram||programLabel.innerHTML;
 programLabel.innerHTML='<strong>Program:</strong> '+htmlEscape(current()?.program?.plumbing_truth||'Unselected')+
  '<div>'+htmlEscape(current()?.has_pick?'Frozen finish selections retained.':'No independent tile pick; neutral / retained surfaces.')+'</div>';
 const content=document.getElementById('viewer-evidence-content');
 let notes=document.getElementById('viewer-source-hold-details');
 if(!notes){notes=document.createElement('div');notes.id='viewer-source-hold-details';content.prepend(notes);}
 notes.innerHTML='<strong>Placement and source review</strong><ul id="viewer-source-holds">'+
  review.holds.map(x=>'<li>'+htmlEscape(x)+'</li>').join('')+'</ul>'+
  '<details style="margin:12px 0"><summary>Full program and source context</summary>'+originalProgram+'</details>';
 const legend=document.getElementById('viewer-fixture-legend');
 const wcMeshes=renderObjects.filter(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'&&o.userData.kind==='toilet');
 legend.hidden=state.mode!=='full'||!wcMeshes.length;
 legend.innerHTML=state.fixtureStudies?
  '<strong>ILLUSTRATIVE WC STUDY</strong><br>Generic body, offset and mounting are unverified. Native source coordinates are unchanged.':
  '<strong>WC · SOURCE LOCATOR</strong><br>Ring = native insertion projected into plan. Generic 3D bodies are available in Camera & source.';
 const note=area?.unresolved?'Area attribution unresolved · '+fmt(area.wallFaceSF)+' vs '+fmt(area.drawingStudySF)+' SF. ':
  'Source wall-face study · Room membership inferred. ';
 fidelity.textContent=note+(review.holds.length?'Placement holds remain in Source review. ':'')+'Original walls, openings and frozen quantities retained.';
 const active=document.querySelector('#room-list .room-btn.active');
 if(innerWidth<=860&&active){const parent=document.querySelector('aside.left');parent.scrollLeft=Math.max(0,active.offsetLeft-parent.clientWidth/2+active.clientWidth/2);}
}

function wcSourceAnchors(inst=instance()){
 const a=inst?.architecture,anchors=[];
 if(a?.toilet_proxy_anchor)anchors.push({wc:a.toilet_proxy_anchor,number:inst.room_number});
 const adjacent=a?.adjacent_zone_geometry;
 // 310A is a WIC: nearby native fixture records are NOT closet contents.
 // Only the independently identified 310B bathroom gets a visible locator.
 if(adjacent?.number==='310B'&&/bath/i.test(adjacent.label||'')){
  const item=adjacent.native_fixture_evidence?.find(x=>x.kind==='toilet'&&x.native_insertion_ft);
  if(item)anchors.push({number:adjacent.number,wc:{
   local_native_insertion_xz_ft:item.location_local_xz_ft,native_plumbing_id:item.id,
   native_insertion_ft:item.native_insertion_ft,receipt_id:item.receipt_id}});
 }
 return anchors;
}

function createWCNativeLocators(){
 if(state.mode!=='full')return;
 for(const {wc,number} of wcSourceAnchors()){
  const p=wc.local_native_insertion_xz_ft;
  if(!p?.every(Number.isFinite))continue;
  const ring=new THREE.Mesh(new THREE.RingGeometry(.12,.16,40),
   new THREE.MeshBasicMaterial({color:0xc5ad87,transparent:true,opacity:.90,depthTest:false,depthWrite:false,side:THREE.DoubleSide}));
  ring.rotation.x=-Math.PI/2;ring.position.set(p[0],.045,p[1]);ring.renderOrder=8;
  ring.userData={category:'SOURCE_WC_PLAN_LOCATOR',kind:'WC native insertion (plan projection)',
   revit_id:wc.native_plumbing_id,receipt_id:wc.receipt_id,room_number:number,
   native_insertion_ft:wc.native_insertion_ft,plan_projection_only:true,
   actual_wc_family_solid:false,installed_height_verified:false,
   source:'Native plumbing insertion XY retained exactly. Y=.045ft is a display-only plan projection, not the source installation height, a ceramic body, pedestal or carrier.'};
  modelGroup.add(ring);renderObjects.push(ring);
 }
}

function applyFixtureStudyVisibility(){
 const meshes=renderObjects.filter(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'&&o.userData.kind==='toilet');
 for(const o of meshes)o.visible=Boolean(state.fixtureStudies);
 for(const o of renderObjects)if(o.userData.category==='SOURCE_WC_PLAN_LOCATOR')o.visible=!state.fixtureStudies||state.sourceTraces;
 for(const id of ['viewer-fixture-studies','viewer-focus-fixture-studies']){
  const b=document.getElementById(id);b.hidden=state.mode!=='full'||!meshes.length;
  b.textContent='WC study '+(state.fixtureStudies?'ON':'OFF');b.setAttribute('aria-pressed',String(state.fixtureStudies));
 }
 document.body.dataset.viewerFixtureStudies=String(state.fixtureStudies);
}

function updateStudioLighting(){
 if(state.mode==='context')return;
 const b=physicalBounds();if(!b||b.isEmpty())return;
 const center=b.getCenter(new THREE.Vector3()),size=b.getSize(new THREE.Vector3());
 const extent=Math.max(size.x,size.z,7);
 main.position.set(center.x-extent*.75,center.y+extent*1.2,center.z+extent*.85);
 main.target.position.copy(center);scene.add(main.target);
 const span=Math.max(8,extent*1.15);
 Object.assign(main.shadow.camera,{left:-span,right:span,top:span,bottom:-span,near:.1,far:extent*7});
 main.shadow.camera.updateProjectionMatrix();main.shadow.normalBias=.025;
 keyLight.position.set(center.x+extent*.2,b.max.y+1.5,center.z+extent*.15);
 // The source wall ghost remains available as an analytical section cue,
 // with a quieter opacity so it does not read as a second opaque assembly.
 for(const o of renderObjects){const ghost=o.userData?.review_ghost;if(ghost?.material)ghost.material.opacity=.045;}
}

function updateCompletionPresentation(){
 programLabel.dataset.fullProgram=programLabel.innerHTML;
 createWCNativeLocators();applyFixtureStudyVisibility();
 updateCompletionSummary();updateStudioLighting();
 if(completionRoomCameras.has(state.preset)&&state.mode==='full')frameCompletionCamera();
 renderer.render(scene,camera);
 if(nativeAuditInstalled)updateNativeAuditUI();
}

function completionViewportRect(){
 const w=stage.clientWidth,h=stage.clientHeight,s=stage.getBoundingClientRect();
 const mobile=innerWidth<=860;
 let top=state.focusView?document.getElementById('viewer-focus-bar').getBoundingClientRect().bottom-s.top+18:
  toolbar.getBoundingClientRect().bottom-s.top+20;
 const bottom=state.focusView?105:mobile?155:125;
 top=Math.min(top,h*.44);
 return {left:mobile?18:28,right:w-(mobile?18:28),top,bottom:h-bottom};
}

function frameCompletionCamera(){
 if(completionFraming||(state.mode!=='full'&&!nativeContextActive()))return;
 const b=physicalBounds();if(!b||b.isEmpty())return;
 completionFraming=true;
 try{
  const r=completionViewportRect(),w=stage.clientWidth,h=stage.clientHeight;
  const safeW=Math.max(100,r.right-r.left),safeH=Math.max(120,r.bottom-r.top);
  const center=b.getCenter(new THREE.Vector3());
  const direction=camera.position.clone().sub(orbit.target).normalize();
  const right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),direction).normalize();
  const up=new THREE.Vector3().crossVectors(direction,right).normalize();
  camera.fov=44;camera.aspect=w/h;
  const tanH=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
  let distance=0;
  for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){
   const p=new THREE.Vector3(x,y,z).sub(center),depth=p.dot(direction);
   distance=Math.max(distance,Math.abs(p.dot(right))/(tanH*camera.aspect*safeW/w)+depth,
    Math.abs(p.dot(up))/(tanH*safeH/h)+depth);
  }
  distance=Math.max(distance*1.065,4);
  orbit.target.copy(center);camera.position.copy(center).addScaledVector(direction,distance);
  camera.near=.025;camera.far=Math.max(1100,distance*5);
  camera.setViewOffset(w,h,w/2-(r.left+r.right)/2,h/2-(r.top+r.bottom)/2,w,h);
  camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
  completionSafeRect=r;
 }finally{completionFraming=false;}
}

function setCamera(preset,force=true){
 completionManualCamera=false;camera.clearViewOffset();
 if(nativeAuditInstalled&&nativeGeometryActive()&&preset==='top'){
  const b=physicalBounds(),center=b.getCenter(new THREE.Vector3());
  state.preset='top';camera.up.set(0,1,0);orbit.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(0,20,.001));orbit.update();
  frameCompletionCamera();applyNativeViewState();if(force)renderer.render(scene,camera);return;
 }

 if(nativeAuditInstalled&&current()?.id==='PH-BATH4'&&nativeGeometryActive()&&preset!=='top'){
  const b=physicalBounds(),center=b.getCenter(new THREE.Vector3());
  state.preset='isometric';camera.fov=44;camera.up.set(0,1,0);
  orbit.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(instance().room_number.endsWith('A')?-12:12,12,16));
  camera.near=.025;camera.far=1100;camera.updateProjectionMatrix();orbit.update();
  frameCompletionCamera();applyNativeViewState();if(force)renderer.render(scene,camera);return;
 }
 setLegacyCamera(preset,false);
 if(completionInstalled&&(state.mode==='full'||nativeContextActive())&&completionRoomCameras.has(state.preset))frameCompletionCamera();
 if(completionInstalled)applyFixtureStudyVisibility();
 if(force)renderer.render(scene,camera);
}

function updateCompletionViewport(){
 if((state.mode==='full'||nativeContextActive())&&completionRoomCameras.has(state.preset)&&!completionManualCamera)frameCompletionCamera();
 else camera.clearViewOffset();
}

function completionEvidence(){
 const objects=renderObjects.map(o=>({category:o.userData.category,kind:o.userData.kind,
  visible:o.visible,revitId:o.userData.revit_id||null,room:o.userData.room_number||null,
  nativeInsertion:o.userData.native_insertion_ft||null,planProjection:o.userData.plan_projection_only||false}));
 const nativeWalls=renderObjects.filter(o=>o.userData.category==='ARCH_REGISTERED_WALL');
 const countertopBounds=renderObjects.filter(o=>[
  'ARCH_R068_SOURCE_COUNTER_LIGHT_REVEAL','ARCH_R069_BOUNDED_CASEWORK_LIGHT'
 ].includes(o.userData.category)).map(o=>{
  const bb=new THREE.Box3().setFromObject(o),s=o.userData.source_bounds_local_ft;
  return {id:o.userData.revit_id,category:o.userData.category,
   sourceMin:[s[0],s[2],s[4]],sourceMax:[s[1],s[3],s[5]],
   meshMin:bb.min.toArray(),meshMax:bb.max.toArray()};
 });
 const b=physicalBounds(),projected=[];
 if(b&&!b.isEmpty())for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){
  const p=new THREE.Vector3(x,y,z).project(camera);
  projected.push([(p.x+1)*stage.clientWidth/2,(1-p.y)*stage.clientHeight/2]);
 }
 return {review:sourceReview(),fixtureStudies:state.fixtureStudies,
  wcMeshes:objects.filter(o=>o.category==='PLAN_SCHEMATIC_FIXTURE'&&o.kind==='toilet'),
  wcLocators:objects.filter(o=>o.category==='SOURCE_WC_PLAN_LOCATOR'),
  nativeWallIds:[...new Set(nativeWalls.map(o=>o.userData.revit_id))],countertopBounds,
  safeViewport:completionSafeRect,projectedBounds:projected,offline:true};
}
