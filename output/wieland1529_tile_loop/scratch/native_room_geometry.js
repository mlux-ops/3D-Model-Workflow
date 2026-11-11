// Geometry is a read-only snapshot of actual Revit instances. Frozen product
// selections are kept separate; source-family geometry is not product approval.
async function loadNativeAudit(){
 const node=document.getElementById('native-geometry');if(!node)return null;
 document.body.dataset.nativeGeometry='LOADING';
 const bytes=Uint8Array.from(atob(node.textContent.trim()),c=>c.charCodeAt(0));
 const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
 const audit=await new Response(stream).json();
 document.body.dataset.nativeGeometry='READY';return audit;
}

function buildAuditedRooms(frozen,audit){
 const rooms=JSON.parse(JSON.stringify(frozen));if(!audit)return rooms;
 for(const room of rooms)for(const inst of room.physical_instances){
  if(room.id==='PH-BATH4'){
   inst.historical_viewer_room_number=inst.room_number;
   inst.room_number='310'+inst.room_number.slice(-1);
   room.numbers=['310A','310B'];
  }
  const source=audit.cases[room.id+'/'+inst.room_number];if(!source)continue;
  const arch=inst.architecture;
  arch.live_native_audit=source;
  if(room.id==='PH-BATH4'){
   delete arch.adjacent_zone_geometry;
   arch.wall_segments=[];arch.openings=[];
   delete arch.toilet_proxy_anchor;delete arch.native_casework_proxies;
   room.full_room_plan={...room.full_room_plan,width_ft:5,depth_ft:source.area_sf/5,
    display_area_ft2:source.area_sf,plan_source:'Owner floor plan A2.2: 310A/B BATH 4; 311A/B WIC 4'};
  }
  arch.floor_polygon_local_xz_ft=source.rings_local_xz_ft[0];
  arch.floor_polygon_area_ft2=source.area_sf;
  arch.native_room_element_id=source.native_room_id;
  arch.native_room_number=source.native_room_number;
  arch.room_assignment=source.membership_verified?'VERIFIED NATIVE ROOM BOUNDARY':'NATIVE WALL-FACE COMPARTMENT; ROOM RECORD INVALID';
  arch.face_confidence=source.boundary_basis;
  arch.wall_receipt_id=audit.source_operation;
  arch.native_wall_ids=source.native_walls;
  arch.drawing_vs_wall_face_difference_ft2=source.area_sf-arch.drawing_display_area_ft2;
  arch.drawing_vs_wall_face_difference_percent=100*(source.area_sf-arch.drawing_display_area_ft2)/arch.drawing_display_area_ft2;
  arch.area_conflict_flag=Math.abs(arch.drawing_vs_wall_face_difference_percent)>5;
  if(source.ceiling)arch.native_ceiling_evidence={...arch.native_ceiling_evidence,
   ...source.ceiling,receipt_id:audit.source_operation,native_surface_geometry:true};
  else delete arch.native_ceiling_evidence;
  if(source.adjacent&&arch.adjacent_zone_geometry){
   const adjacent=arch.adjacent_zone_geometry;
   adjacent.floor_polygon_local_xz_ft=source.adjacent.rings_local_xz_ft[0];
   adjacent.area_display_ft2=source.adjacent.area_sf;
   adjacent.native_room_element_id=source.adjacent.native_room_id;
  }
  inst.live_native_room_id=source.native_room_id;
  inst.live_native_room_number=source.native_room_number;
 }
 return rooms;
}

const nativeMaterialCache=new Map();
const nativeAuditMaterials=new Map((NATIVE_AUDIT?.materials||[]).map(x=>[x.id,x]));
let nativeRendered=[];
const nativeFinishHolds=new Map();
function nativeCase(room=current(),inst=instance()){
 return NATIVE_AUDIT?.cases[room?.id+'/'+inst?.room_number]||null;
}
function nativeContextActive(){return Boolean(NATIVE_AUDIT&&state.mode==='context'&&!state.levelContext);}
function nativeGeometryActive(){return Boolean(nativeCase()&&(state.mode==='full'||nativeContextActive()));}

function nativeMaterial(id){
 if(nativeMaterialCache.has(id))return nativeMaterialCache.get(id);
 const s=nativeAuditMaterials.get(id)||{color:[220,218,210],name:'Unassigned',transparency:0};
 const [r,g,b]=s.color,name=s.name.toLowerCase();
 const metal=/metal|chrome|nickel|brass|steel|gold|onyx/.test(name);
 const glass=s.transparency>50||/glass|glazing/.test(name);
 const ceramic=/vitreous|porcelain|china/.test(name);
 const m=new THREE.MeshPhysicalMaterial({color:(r<<16)|(g<<8)|b,
  roughness:glass?.12:metal?.25:ceramic?.18:/countertop|stone|marble/.test(name)?.30:.78,
  metalness:metal?.88:0,clearcoat:ceramic?.38:0,clearcoatRoughness:.18,
  transparent:glass,opacity:glass?.23:1,depthWrite:!glass,side:THREE.DoubleSide,
  envMapIntensity:metal?1.1:.85});
 m.userData={native_source_material_id:id,native_source_material_name:s.name,
  display_rgb_from_model:true,physical_finish_certified:false};
 nativeMaterialCache.set(id,m);return m;
}

function removeLegacyNativeProxies(){
 const remove=new Set();
 for(const object of renderObjects){
  const u=object.userData||{},c=u.category||'';
  const replacement=c==='ARCH_REGISTERED_WALL'||c==='ARCH_HOSTED_DOOR_LEAF'||c==='ARCH_HOSTED_WINDOW'||
   c==='ARCH_VISUAL_CUTAWAY_UPPER_REMNANT'||c==='ARCH_NATIVE_COUNTERTOP_VISUAL'||
   c==='ARCH_NATIVE_CASEWORK_AABB_STUDY'||c==='ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL'||
   c==='ARCH_CEILING_EXTENT_DATUM'||c==='ARCH_INFERRED_ROOM_VERTICAL_WIRES'||
   c==='ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR'||c==='SOURCE_WC_PLAN_LOCATOR'||
   c==='ARCH_R059_DERIVED_GWB_CEILING_CANOPY'||
   /^ARCH_R0(62|63|66|67|68|69|70)_.*(COUNTER|VANITY|CASEWORK|POWDER_FACET|PLASTER|CORNER_DEPTH|NATIVE_WALL_DEPTH|NATIVE_HOST_REVEAL|BOUNDED_LID)/.test(c)||
   c==='PLAN_SCHEMATIC_FIXTURE'&&['toilet','vanity','lavatory'].includes(u.kind);
  if(replacement){object.traverse(o=>remove.add(o));}
 }
 for(const object of remove){object.removeFromParent();object.geometry?.dispose();}
 renderObjects=renderObjects.filter(o=>!remove.has(o));
 materialObjects=materialObjects.filter(o=>!remove.has(o));
}

function addNativeGeometry(source,mode){
 nativeRendered=[];
 for(const e of source.elements){
  const contextHold=Boolean(e.source_attribution_hold);
  const include=mode==='context'||e.full_room_default||['ceiling','overhead_structure'].includes(e.geometry_role);
  if(!include||contextHold&&mode!=='context')continue;
  for(const p of e.primitives){
   const geo=new THREE.BufferGeometry();
   geo.setAttribute('position',new THREE.Float32BufferAttribute(p.positions,3));
   geo.setIndex(p.indices);geo.computeVertexNormals();geo.computeBoundingBox();
   const material=nativeMaterial(p.material_id).clone();
   if(e.geometry_role==='ceiling'||e.geometry_role==='overhead_structure'){
    material.transparent=true;material.opacity=.16;material.depthWrite=false;
   }
   const mesh=new THREE.Mesh(geo,material);
   mesh.castShadow=!material.transparent;mesh.receiveShadow=true;
   mesh.userData={category:'LIVE_NATIVE_'+e.category.toUpperCase().replace(/\s+/g,'_'),
    source_category:e.category,native_geometry:true,live_native_geometry:true,
    revit_id:e.id,unique_id:e.unique_id,version_guid:e.version_guid,
    family_name:e.family_name||e.name,source_name:e.name,host_id:e.host_id,
    room_number:source.number,native_room_id:source.native_room_id,
    native_room_number:source.native_room_number,room_membership_verified:source.membership_verified,
    document_session_id:NATIVE_AUDIT.document.session_id,receipt_id:e.geometry_source_operation||NATIVE_AUDIT.source_operation,
    source:'Read-only native Revit instance geometry, fine face triangulation. Source-family shape is not frozen product selection or installation approval.',
    native_geometry_role:e.geometry_role||null,fixture_kind:e.fixture_kind||null,
    display_clip_only:e.display_clip_only,context_room:e.context_room,
    source_attribution_hold:e.source_attribution_hold||null,
    outward_faces:e.outward_faces||[],native_material_id:p.material_id,
    surfaceIndex:-1,triangle_count:p.indices.length/3};
   mesh.raycast=function(raycaster,hits){
    const candidates=[];THREE.Mesh.prototype.raycast.call(this,raycaster,candidates);
    for(const hit of candidates)if((this.material.clippingPlanes||[]).every(p=>p.distanceToPoint(hit.point)>=-1e-6))hits.push(hit);
   };
   modelGroup.add(mesh);renderObjects.push(mesh);nativeRendered.push(mesh);
   if(state.edges){
    const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geo,35),new THREE.LineBasicMaterial({color:0x69716c,transparent:true,opacity:.4}));
    edges.raycast=()=>{};mesh.add(edges);
   }
  }
 }
 renderer.localClippingEnabled=true;
}

function buildFullRoom(room){
 if(room.id==='PH-BATH4'&&nativeCase(room,instance()))return buildCorrectedPH4(room,nativeCase(room,instance()));
 buildLegacyFullRoom(room);
 const source=nativeCase(room,instance());if(!source)return;
 removeLegacyNativeProxies();addNativeGeometry(source,'full');alignFinishStudiesToNativeFaces(source);
 for(const object of renderObjects)if(object.userData?.category==='ARCH_REGISTERED_FLOOR'){
  Object.assign(object.userData,{native_room_id:source.native_room_id,
   native_room_number:source.native_room_number,room_membership_verified:source.membership_verified,
   source:source.boundary_basis+'; display floor uses this exact source footprint, not a changed quantity.'});
 }
}

function buildCorrectedPH4(room,source){
 addNativeGeometry(source,'full');
 const poly=source.rings_local_xz_ft[0],xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
 const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
 const shape=new THREE.Shape();shape.moveTo(poly[0][0],-poly[0][1]);
 poly.slice(1).forEach(p=>shape.lineTo(p[0],-p[1]));shape.closePath();
 const fp=productFor('floor'),wp=productFor('wall'),height=source.ceiling?.underside_height_ft||9.25;
 const floor=new THREE.Mesh(new THREE.ShapeGeometry(shape),fp?registeredFloorMaterial(fp):neutral.flooring);
 floor.rotation.x=-Math.PI/2;floor.position.y=.018;floor.receiveShadow=true;
 floor.userData={category:'ARCH_REGISTERED_FLOOR',surfaceIndex:productList().indexOf(fp),native_room_id:source.native_room_id,
  room_number:source.number,room_membership_verified:true,source:'A2.2 bathroom 310; exact native Room footprint. 311 closet excluded. Finish study; historical quantity unchanged.'};
 modelGroup.add(floor);renderObjects.push(floor);
 const south=source.elements.find(e=>e.category==='Walls'&&e.outward_faces?.some(f=>Math.abs(f.mid_xz[1]-maxZ)<.02&&f.normal_xz[1]>.9));
 if(south&&wp){
  addPlane(maxX-minX,height,[(minX+maxX)/2,height/2,maxZ-.006],[0,Math.PI,0],
   tileMaterial(wp,maxX-minX,height,'wall'),'FULL_ROOM_WET_WALL',productList().indexOf(wp),
   {native_host_face_id:south.id,source:'Frozen Pienza finish study on actual south shower-side wall of 310, as oriented on owner A2.2. No closet finish or quantity added.',plan_corrected_ph4:true});
 }
 alignFinishStudiesToNativeFaces(source);
 modeInfo='PH Bath 4 '+source.number+' · native 5 ft × 7 ft 1/4 in bathroom · 311 is the separate closet';
 modelInfo.textContent=source.number+' · '+source.area_sf.toFixed(2)+' SF · actual bathroom footprint';
}

function alignFinishStudiesToNativeFaces(source){
 const withheld=new Set(),holds=[];
 for(const object of renderObjects){
  const u=object.userData||{};
  if(object.parent!==modelGroup||!object.isMesh||!u.native_host_face_id||
   !['FULL_ROOM_WET_WALL','ARCH_R067_SOURCE_HOSTED_DRY_FINISH_PREVIEW','ARCH_R059_FULL_HEIGHT_FINISH_REVIEW'].includes(u.category))continue;
  let wall=source.elements.find(e=>e.id===u.native_host_face_id&&e.category==='Walls');
  // Historical PH2 return metadata sometimes assigned a perpendicular wall.
  // Resolve against the original plane normal and actual native boundary face.
  if(source.key.startsWith('PH-BATH2/')&&['FULL_ROOM_WET_WALL','ARCH_R059_FULL_HEIGHT_FINISH_REVIEW'].includes(u.category)){
   const n=new THREE.Vector3(0,0,1).applyQuaternion(object.quaternion),p=object.position;
   const candidates=source.elements.filter(e=>e.category==='Walls').flatMap(e=>(e.outward_faces||[]).map(f=>({e,f,
    d:Math.abs((p.x-f.mid_xz[0])*f.normal_xz[0]+(p.z-f.mid_xz[1])*f.normal_xz[1])})))
    .filter(c=>Math.abs(n.x*c.f.normal_xz[0]+n.z*c.f.normal_xz[1])>.99&&c.d<.06).sort((a,b)=>a.d-b.d);
   if(candidates.length){wall=candidates[0].e;u.native_host_face_id=wall.id;}
  }
  if(!wall?.outward_faces?.length)continue;
  const p=object.position;
  const nearest=wall.outward_faces.reduce((a,b)=>{
   const distance=f=>Math.abs((p.x-f.mid_xz[0])*f.normal_xz[0]+(p.z-f.mid_xz[1])*f.normal_xz[1]);
   return distance(a)<=distance(b)?a:b;
  });
  const [nx,nz]=nearest.normal_xz,[mx,mz]=nearest.mid_xz;
  const d=(p.x-mx)*nx+(p.z-mz)*nz;
  p.x-=nx*(d+.006);p.z-=nz*(d+.006);
  object.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(-nx,0,-nz));
  u.native_finish_face_aligned=true;u.native_finish_preview_offset_ft=.006;
  clipFinishToNativeFace(object,wall);
  if(u.native_finish_face_clip===false){
   holds.push({category:u.category,wall:u.wall,returnMid:u.review_return_face_midpoint_xz_ft,returnNormal:u.review_return_outward_xz,host:u.native_host_face_id,width:object.geometry.parameters?.width,height:object.geometry.parameters?.height,position:object.position.toArray(),normal:new THREE.Vector3(0,0,1).applyQuaternion(object.quaternion).toArray()});
   object.traverse(o=>withheld.add(o));
  }
 }
 for(const object of withheld){object.removeFromParent();object.geometry?.dispose();}
 renderObjects=renderObjects.filter(o=>!withheld.has(o));materialObjects=materialObjects.filter(o=>!withheld.has(o));
 nativeFinishHolds.set(source.key,holds);
}

function clipFinishToNativeFace(object,wall){
 const width=object.geometry.parameters?.width,height=object.geometry.parameters?.height;
 if(!(width>0&&height>0))return;
 object.updateMatrixWorld(true);
 const inverse=object.matrixWorld.clone().invert(),positions=[],uv=[];
 const clip=(polygon,axis,limit,sign)=>{
  const result=[];if(!polygon.length)return result;
  let a=polygon.at(-1),sa=(a[axis]-limit)*sign,insideA=sa>=-1e-7;
  for(const b of polygon){const sb=(b[axis]-limit)*sign,insideB=sb>=-1e-7;
   if(insideA!==insideB){const t=sa/(sa-sb);result.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t]);}
   if(insideB)result.push(b);a=b;sa=sb;insideA=insideB;
  }return result;
 };
 for(const primitive of wall.primitives){
  const p=primitive.positions,ix=primitive.indices;
  for(let n=0;n<ix.length;n+=3){
   const triangle=ix.slice(n,n+3).map(i=>new THREE.Vector3(p[i*3],p[i*3+1],p[i*3+2]).applyMatrix4(inverse).toArray());
   if(triangle.some(v=>Math.abs(v[2]+.006)>.003))continue;
   let polygon=triangle;
   for(const [axis,limit,sign] of [[0,-width/2,1],[0,width/2,-1],[1,-height/2,1],[1,height/2,-1]])polygon=clip(polygon,axis,limit,sign);
   for(let j=1;j<polygon.length-1;j++){
    const tri=[polygon[0],polygon[j],polygon[j+1]];
    const area=Math.abs((tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[2][0]-tri[0][0])*(tri[1][1]-tri[0][1]));
    if(area<1e-10)continue;
    for(const v of tri){positions.push(v[0],v[1],0);uv.push(v[0]/width+.5,v[1]/height+.5);}
   }
  }
 }
 if(!positions.length){object.userData.native_finish_face_clip=false;return;}
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
 geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geometry.computeVertexNormals();
 geometry.parameters={width,height};object.geometry.dispose();object.geometry=geometry;
 object.userData.native_finish_face_clip=true;
 object.userData.native_finish_source_triangles=positions.length/9;
}

function buildContext(room,inst){
 if(!NATIVE_AUDIT||state.levelContext){nativeRendered=[];return buildLegacyContext(room,inst);}
 const source=nativeCase(room,inst);if(!source)return buildLegacyContext(room,inst);
 addNativeGeometry(source,'context');
 modeInfo='NATIVE REVIT ROOM SNAPSHOT — actual wall, opening, fixture and casework geometry. Source-family products remain distinct from frozen selections.';
 modelInfo.textContent=source.number+' / native '+(source.native_room_number||'room record unresolved')+' / '+source.area_sf.toFixed(2)+' SF';
}

function applyNativeViewState(){
 if(!nativeAuditInstalled)return;
 const active=nativeGeometryActive();
 const cuts=new Set();let count=0;
 for(const mesh of nativeRendered){
  if(!mesh.parent)continue;
  const u=mesh.userData;
  if(u.source_category!=='Walls')continue;
  const facing=u.outward_faces.some(f=>{
   const dx=camera.position.x-f.mid_xz[0],dz=camera.position.z-f.mid_xz[1];
   return (dx*f.normal_xz[0]+dz*f.normal_xz[1])/Math.max(.001,Math.hypot(dx,dz))>.26;
  });
  const cut=active&&state.interiorReveal&&facing;
  mesh.visible=state.walls;
  mesh.material.clippingPlanes=cut?[new THREE.Plane(new THREE.Vector3(0,-1,0),2.35)]:[];
  mesh.material.clipShadows=true;
  if(u.last_native_cutaway!==cut){mesh.material.needsUpdate=true;u.last_native_cutaway=cut;}
  for(const child of mesh.children)if(child.material)child.material.clippingPlanes=mesh.material.clippingPlanes;
  u.reversible_view_cutaway=cut;
  if(cut){cuts.add(u.revit_id);count++;}
 }
 for(const mesh of nativeRendered){
  const u=mesh.userData;if(!mesh.parent)continue;
  if(['Doors','Windows'].includes(u.source_category))mesh.visible=state.walls&&!(state.interiorReveal&&cuts.has(u.host_id));
  if(u.native_geometry_role==='ceiling'||u.native_geometry_role==='overhead_structure')mesh.visible=Boolean(state.ceilingPreview&&state.walls);
  if(u.source_attribution_hold)mesh.visible=Boolean(nativeContextActive()&&state.sourceTraces);
 }
 for(const o of renderObjects)if(o.userData?.category==='SOURCE_WC_PLAN_LOCATOR')o.visible=state.sourceTraces;
 for(const o of renderObjects)if(o.userData?.plan_corrected_ph4&&o.material){
  const cut=state.interiorReveal&&cuts.has(o.userData.native_host_face_id);
  o.material.clippingPlanes=cut?[new THREE.Plane(new THREE.Vector3(0,-1,0),2.35)]:[];
  o.material.needsUpdate=true;o.visible=state.walls;
 }
 document.body.dataset.nativeMeshCount=String(nativeRendered.filter(o=>o.parent).length);
 document.body.dataset.nativeWallCuts=String(count);
}

function nativeSourceReview(room=current(),inst=instance()){
 const s=nativeCase(room,inst);if(!s)return null;
 const holds=[];const kind=room.program?.kind;
 if(!s.membership_verified)holds.push('Native '+s.number+' room record is unplaced or identifies another space. This WC enclosure is verified against current wall faces.');
 if(s.native_room_number&&s.native_room_number!==s.number)holds.push('Drawing/viewer '+s.number+' maps spatially to native '+s.native_room_number+' TOILET. Both identifiers are retained.');
 if(kind==='PRIMARY_WALK_IN_LINEAR')holds.push('Selected walk-in and linear-drain installation remain unverified. Native room shows existing project fixture geometry separately.');
 if(kind==='TUB_OR_WALK_IN_UNSELECTED')holds.push('Tub versus walk-in remains UNSELECTED. Native room is a source-model reference, not a program choice.');
 if(room.id==='TX-BATH4')holds.push('Selected Duravit tub remains UNLOCATED; no selected tub installation is invented.');
 if(room.id==='PH-POWDER')holds.push('Prior basin locator referenced a wall faucet. Native faucet/cabinet geometry is available; no independent selected basin is located.');
 if(room.id==='TX-POWDER')holds.push('Wall finish remains NO PICK. Native fixture geometry does not select a product.');
 if(room.id==='TX-POWDER2')holds.push('Basin remains UNSELECTED; existing native basin is a reference. Selected faucet installation is not certified.');
 if(room.id==='PH-BATH4')holds.push('A2.2 identifies 310A/B as Bath 4 and 311A/B as WIC 4. The native names and viewer mapping are corrected; the closet is excluded from this bathroom footprint.');
 if(!s.ceiling)holds.push('No finish-ceiling element matched this room in the native model. Available overhead structure is a separate reference.');
 if(nativeFinishHolds.get(s.key)?.length)holds.push('A selected-wall preview has no supporting native face in its study rectangle and is withheld. Wet-zone detail retains the material sample.');
 const sourceHolds=s.elements.filter(e=>e.source_attribution_hold);
 if(sourceHolds.length)holds.push(sourceHolds.length+' conflicting or nonphysical source objects are hidden by default; inspect them using Native room + Source lines.');
 const conflicts=s.elements.filter(e=>e.room_property_conflict);
 if(conflicts.length)holds.push(conflicts.length+' source element Room-property conflict(s); geometry is associated by position and level.');
 const actualWC=s.elements.some(e=>e.fixture_kind==='toilet'&&!e.source_attribution_hold);
 const delta=100*(s.area_sf-s.drawing_area_sf)/s.drawing_area_sf;
 return {room:room.id,instance:s.number,
  area:{wallFaceSF:s.area_sf,drawingStudySF:s.drawing_area_sf,
   historicalSF:room.full_room_plan?.source_floor_area_ft2,differencePercent:delta,
   unresolved:Math.abs(delta)>5,nativeRoomVerified:s.membership_verified},holds,
  roomMembershipCertified:s.membership_verified,
  geometryBasis:s.boundary_basis,nativeRoomId:s.native_room_id,nativeRoomNumber:s.native_room_number,
  nativeWallIds:s.native_walls,wallReceipt:NATIVE_AUDIT.source_operation,
  fixtureStudies:state.fixtureStudies,hasWC:actualWC,liveRevitVerified:true,
  selectionDataChanged:false,sourceModelFixtureLayer:true};
}

function updateNativeAuditUI(){
 if(!nativeAuditInstalled)return;
 const s=nativeCase();if(!s)return;
 const nativeMode=nativeContextActive(),full=state.mode==='full',archived=state.mode==='context'&&state.levelContext;
 for(const id of ['viewer-ph4-focus-311','viewer-ph4-focus-310'])document.getElementById(id).hidden=true;
 document.getElementById('viewer-mode-context').textContent='Native room';
 document.getElementById('confidence').textContent=archived?'Archived level bounds':s.membership_verified?'Native Room / actual solids':'Native walls / derived WC';
 document.getElementById('room-description').textContent=s.number+' / '+(s.native_room_number&&s.native_room_number!==s.number?'native '+s.native_room_number+' / ':'')+
  (archived?'Archived level bounding boxes. Use Native room for the current geometry snapshot.':nativeMode?'Current-model geometry; source fixtures are separate from frozen product selections.':full?'Frozen finish study on audited native architecture. Native room shows the current-model fixtures.':'Dimensioned material study; native room audit remains available.');
 const alert=document.querySelector('.alert');
 alert.textContent=archived?'ARCHIVED LEVEL BOUNDS':nativeMode?'NATIVE MODEL SNAPSHOT':full?'AUDITED GEOMETRY · FROZEN FINISH STUDY':'WET FINISH STUDY';
 const review=sourceReview(),area=review.area;
 const card=document.getElementById('viewer-source-review');
 card.innerHTML='<strong>'+htmlEscape(s.number)+' · '+(s.membership_verified?'Native Room verified':'Wall-face enclosure')+'</strong>'+
  '<div class="source-area"><div><span>'+(s.membership_verified?'Native Room area':'Wall-face area')+'</span><b>'+s.area_sf.toFixed(2)+' SF</b></div><div><span>Historical drawing study</span><b>'+s.drawing_area_sf.toFixed(2)+' SF</b></div></div>'+
  '<p>'+(s.membership_verified?'Revit Room '+htmlEscape(s.native_room_number)+' · ID '+s.native_room_id+'.':'Native room tag/record requires correction; physical wall geometry retained.')+
  (area.unresolved?' Historical area differs; frozen quantities remain unchanged.':'')+'</p>'+
  '<button type="button" id="viewer-native-evidence-open">'+review.holds.length+' source / placement notes →</button>';
 document.getElementById('viewer-native-evidence-open').onclick=()=>{roomEvidence.open=true;roomEvidence.scrollIntoView({block:'nearest'});};
 const evidence=document.getElementById('viewer-evidence-content');
 evidence.innerHTML='<strong>Native geometry audit</strong><div>Document: '+htmlEscape(NATIVE_AUDIT.document.title)+
  '</div><div>Session: '+htmlEscape(NATIVE_AUDIT.document.session_id)+'</div><div>Read-only source operation: '+htmlEscape(NATIVE_AUDIT.source_operation)+
  '</div><div>Boundary basis: '+htmlEscape(s.boundary_basis)+'</div><div>Native room ID: '+htmlEscape(s.native_room_id||'Not assigned to this physical WC')+
  '</div><div>Wall IDs: '+htmlEscape(s.native_walls.join(', '))+'</div><div>Native geometry: '+s.elements.length+' source elements; exact instance positions, native face materials and hosted openings. Wall/floor geometry is clipped only for this room view.</div>'+
  (s.excluded_out_of_room_elements?.length?'<div>'+s.excluded_out_of_room_elements.length+' adjacent-storey object(s) wholly above the native finish ceiling excluded from this room view.</div>':'')+
  '<ul style="padding-left:16px">'+review.holds.map(t=>'<li>'+htmlEscape(t)+'</li>').join('')+'</ul>'+
  '<details><summary>Native elements and source classifications</summary>'+s.elements.map(e=>'<div style="margin:7px 0"><b>'+e.id+'</b> · '+htmlEscape(e.category)+' · '+htmlEscape(e.family_name||e.name)+
   (e.context_room?' · separate '+htmlEscape(e.context_room):'')+(e.source_attribution_hold?' · ATTRIBUTION HOLD':'')+'</div>').join('')+'</details>'+
  '<p>Native Room records repaired against owner plans: TX WC placement and PH Bath 4 / closet names. Geometry captured after those repairs. Product selections and quantities retained; no save or synchronization. Source family geometry is not manufacturer installation approval.</p>';
 const note=(s.membership_verified?'Native Room '+s.native_room_number:'Wall-derived WC')+' · '+s.area_sf.toFixed(2)+' SF · '+
  (archived?'Archived level bounds; current native room audit is separate.':nativeMode?'Source-model fixture geometry; frozen program unchanged.':'Frozen finish study; source-model geometry available in Native room.');
 fidelity.textContent=note;fidelity.title=note;
 focusCaption.textContent=note;
 document.getElementById('viewer-focus-level').textContent=nativeMode?'NATIVE SOURCE MODEL · SELECTIONS UNCHANGED':full?'NATIVE ARCHITECTURE · FROZEN FINISH STUDY':'WET MATERIAL STUDY';
 const section=document.getElementById('viewer-focus-cutaway');section.hidden=!(full||nativeMode);
 document.getElementById('viewer-reveal-interior').hidden=!(full||nativeMode);
 const hasCeiling=s.elements.some(e=>e.geometry_role==='ceiling');
 const hasOverhead=s.elements.some(e=>['ceiling','overhead_structure'].includes(e.geometry_role));
 document.getElementById('viewer-focus-gwb').hidden=!(full||nativeMode)||!hasOverhead;
 document.getElementById('viewer-ceiling-preview').hidden=!(full||nativeMode)||!hasOverhead;
 document.getElementById('viewer-focus-gwb').textContent=(hasCeiling?'Native ceiling ':'Overhead model ')+(state.ceilingPreview?'ON':'OFF');
 document.getElementById('viewer-fixture-legend').hidden=true;
 for(const id of ['viewer-fixture-studies','viewer-focus-fixture-studies'])document.getElementById(id).hidden=true;
 if(state.compareAB){
  const first=document.getElementById('viewer-ab-drawer').firstElementChild;
  if(first)first.textContent='A/B source geometry is independent for each physical room. Native Room boundaries are used where valid; TX WC enclosures remain wall-derived. 310 context is separate.';
 }
 applyNativeViewState();
}

function updateFocusViewControls(){
 updateLegacyFocusControls();
 if(nativeAuditInstalled)updateNativeAuditUI();
}

function showNativeElement(data){
 if(!data.live_native_geometry)return showLegacyNativeElement(data);
 selectedRevit.hidden=false;selectedRevit.open=true;
 document.getElementById('viewer-v2-element-detail').innerHTML='<strong>Actual native instance geometry</strong>'+
  '<div>Element '+data.revit_id+' · '+htmlEscape(data.family_name)+'</div><div>Unique ID: '+htmlEscape(data.unique_id)+'</div><div>Source category: '+htmlEscape(data.source_category)+
  '</div><div>Native room: '+htmlEscape(data.native_room_number||'Wall-derived compartment')+'</div><div>Document session: '+htmlEscape(data.document_session_id)+
  '</div><div>Read-only operation: '+htmlEscape(data.receipt_id)+'</div><div>Displayed triangles: '+data.triangle_count+
  (data.display_clip_only?' · source geometry clipped for room view only':'')+'</div><div>Source family geometry and frozen product selection are separate. No manufactured installation certification.</div>';
}

function installNativeAudit(){
 if(!NATIVE_AUDIT)return;
 state.levelContext=false;nativeAuditInstalled=true;
 const options=document.querySelector('#viewer-view-options .viewer-secondary-controls');
 const level=document.createElement('button');level.type='button';level.className='viewer-btn';
 level.id='viewer-level-context';level.textContent='Archived level bounds';level.onclick=()=>{state.levelContext=true;setMode('context');};options.append(level);
 const nativeButton=document.getElementById('viewer-mode-context');
 nativeButton.onclick=()=>{state.levelContext=false;setMode('context');};
 const toggleSection=()=>{state.interiorReveal=!state.interiorReveal;applyWallVisibility();applyInteriorReveal();updateFocusViewControls();renderer.render(scene,camera);};
 document.getElementById('viewer-focus-cutaway').onclick=toggleSection;
 document.getElementById('viewer-reveal-interior').onclick=toggleSection;
 const toggleCeiling=()=>{state.ceilingPreview=!state.ceilingPreview;applyCeilingPreview();updateFocusViewControls();renderer.render(scene,camera);};
 document.getElementById('viewer-focus-gwb').onclick=toggleCeiling;
 document.getElementById('viewer-ceiling-preview').onclick=toggleCeiling;
 const focusButton=document.createElement('button');focusButton.type='button';focusButton.className='viewer-btn';focusButton.id='viewer-focus-native';focusButton.textContent='Native room';
 focusButton.onclick=()=>{state.levelContext=false;setMode('context');};document.getElementById('viewer-focus-full').after(focusButton);
 const foot=document.querySelector('.foot');foot.textContent='Floor-plan reconciliation: 26 verified native bathroom Room boundaries. TX WC records repaired; PH Bath 4 correctly mapped to 310A/B, with 311 closets excluded. Frozen products and quantities retained.';
 document.querySelector('.side-note').textContent='13 bathroom types · 26 physical A/B instances verified against native Room boundaries and the owner’s floor plans. PH Bath 4 is 310A/B; TX WC records are repaired.';
 Object.assign(window.__viewerDebug,{getNativeAudit:()=>{
  const s=nativeCase();return {key:s.key,nativeRoomId:s.native_room_id,nativeRoomNumber:s.native_room_number,
   membershipVerified:s.membership_verified,areaSF:s.area_sf,boundary:s.rings_local_xz_ft,
   mode:state.mode,nativeContext:nativeContextActive(),sourceElements:s.elements.map(e=>({id:e.id,category:e.category,kind:e.fixture_kind,
    role:e.geometry_role,triangles:e.primitives.reduce((n,p)=>n+p.indices.length/3,0),fullDefault:e.full_room_default})),
   rendered:nativeRendered.filter(m=>m.parent).map(m=>({id:m.userData.revit_id,category:m.userData.source_category,role:m.userData.native_geometry_role,
    visible:m.visible,triangles:m.userData.triangle_count,cutaway:Boolean(m.userData.reversible_view_cutaway),
    bounds:(()=>{const b=new THREE.Box3().setFromObject(m);return [b.min.toArray(),b.max.toArray()];})()})),
   finishStudies:renderObjects.filter(o=>o.userData?.native_finish_face_aligned).map(o=>({host:o.userData.native_host_face_id,
    clipped:o.userData.native_finish_face_clip,sourceTriangles:o.userData.native_finish_source_triangles||0})),
   finishHolds:nativeFinishHolds.get(s.key)||[],selectionChanged:false,modelWrites:Boolean(NATIVE_AUDIT.room_record_repairs)};}});
}
