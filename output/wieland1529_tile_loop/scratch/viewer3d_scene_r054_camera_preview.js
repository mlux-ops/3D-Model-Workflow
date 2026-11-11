// 1529 Wieland: verifiable dual-mode bathroom viewer.
// Source-dimensional study surfaces are never represented as native Revit solids.
// Native Revit bounds render only as a separate, unassigned level-context mode.
import * as THREE from 'three';
import { OrbitControls } from 'orbit-controls';

const DATA=JSON.parse(document.getElementById('data').textContent);
const ROOMS=DATA.rooms;
const canvas=document.getElementById('render');
const stage=document.getElementById('stage');
const state={room:'PH-BATH4',instance:0,mode:'full',edges:false,walls:true,insertions:true,alt:false,surface:-1,preset:'isometric'};
const runtimeErrors=[];
window.addEventListener('error',e=>runtimeErrors.push('JS: '+e.message));
window.addEventListener('unhandledrejection',e=>runtimeErrors.push('Promise: '+String(e.reason)));
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.65));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.035;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x17222b);
const camera=new THREE.PerspectiveCamera(48,1,.025,1400);
const orbit=new OrbitControls(camera,renderer.domElement);
orbit.enableDamping=true;orbit.dampingFactor=.105;
orbit.minDistance=.65;orbit.maxDistance=260;
orbit.maxPolarAngle=Math.PI*.94;
const hemi=new THREE.HemisphereLight(0xdceafb,0x594d42,1.60);scene.add(hemi);
const ambient=new THREE.AmbientLight(0xffffff,.26);scene.add(ambient);
const main=new THREE.DirectionalLight(0xffecd6,2.95);
main.position.set(-9,14,11);main.castShadow=true;
main.shadow.mapSize.set(2048,2048);
main.shadow.camera.left=-45;main.shadow.camera.right=45;
main.shadow.camera.top=45;main.shadow.camera.bottom=-45;
main.shadow.camera.near=.3;main.shadow.camera.far=110;
main.shadow.bias=-.0002;scene.add(main);
const bounce=new THREE.DirectionalLight(0xcce3f5,1.15);
bounce.position.set(10,6,-9);scene.add(bounce);
const keyLight=new THREE.PointLight(0xfff0db,43,34,1.8);
keyLight.position.set(0,12,2);scene.add(keyLight);
// Soft studio environment. Not a claimed site-specific HDRI.
const env=new THREE.Scene();env.background=new THREE.Color(0x8d9a9f);
env.add(new THREE.HemisphereLight(0xeef5ff,0x665545,3.3));
const pmrem=new THREE.PMREMGenerator(renderer);
scene.environment=pmrem.fromScene(env,.06).texture;
const neutral={
 wall:new THREE.MeshStandardMaterial({color:0xe3dcd0,roughness:.86,side:THREE.DoubleSide}),
 missing:new THREE.MeshStandardMaterial({color:0x7d8388,roughness:.82,side:THREE.DoubleSide}),
 flooring:new THREE.MeshStandardMaterial({color:0x7c7973,roughness:.88,side:THREE.DoubleSide}),
 wood:new THREE.MeshStandardMaterial({color:0x917a63,roughness:.65,side:THREE.DoubleSide}),
 glass:new THREE.MeshPhysicalMaterial({color:0xc8e3ee,roughness:.09,metalness:0,transmission:.68,transparent:true,opacity:.35,side:THREE.DoubleSide,depthWrite:false}),
 metal:new THREE.MeshStandardMaterial({color:0x32343a,metalness:.82,roughness:.25}),
 porcelain:new THREE.MeshPhysicalMaterial({color:0xe9e7df,roughness:.23,metalness:0,clearcoat:.45,clearcoatRoughness:.22}),
 modelWall:new THREE.MeshStandardMaterial({color:0x8a9ba4,roughness:.84,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false}),
 contextFloor:new THREE.MeshStandardMaterial({color:0x7c8789,roughness:.85,transparent:true,opacity:.25,side:THREE.DoubleSide,depthWrite:false}),
 contextWindow:new THREE.MeshPhysicalMaterial({color:0x8daeba,roughness:.08,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false}),
 contextualDoor:new THREE.MeshStandardMaterial({color:0x947e6a,roughness:.62,transparent:true,opacity:.64}),
 contextualCase:new THREE.MeshStandardMaterial({color:0xb6a393,roughness:.54,transparent:true,opacity:.66})
};
const enclosureSide=new THREE.MeshPhysicalMaterial({color:0xcbd6dc,transparent:true,opacity:.14,roughness:.78,side:THREE.DoubleSide,depthWrite:false});
const enclosureBack=new THREE.MeshStandardMaterial({color:0xd5d2c9,roughness:.82,side:THREE.DoubleSide});
const insertionMaterial=new THREE.PointsMaterial({color:0xffc974,size:7.5,sizeAttenuation:false,depthTest:false,depthWrite:false,transparent:true});
const materialCache=new Map();
let modelGroup=new THREE.Group();scene.add(modelGroup);
let renderObjects=[],materialObjects=[],modeInfo='',sceneBounds=null;
let cameraEvidence=null;
let rebuildRevision=0;
const pickerRay=new THREE.Raycaster(),mouse=new THREE.Vector2();
let modal=null;

const style=document.createElement('style');
style.textContent=`
#viewer-v2-toolbar{position:absolute;z-index:5;top:158px;left:20px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;max-width:calc(100% - 145px)}
.viewer-select,.viewer-btn{background:#14212ecc;border:1px solid #5c7486;border-radius:6px;color:#edf4f7;padding:8px 10px;font:600 11px/1.35 "Segoe UI",Arial,sans-serif;letter-spacing:.01em}
.viewer-btn[aria-pressed=true]{background:#b59b79;color:#0f1b26;border-color:#dec7aa}
.viewer-btn:hover,.viewer-select:hover{border-color:#dfc3a0}
#viewer-v2-fidelity{position:absolute;z-index:2;bottom:79px;left:23px;right:24px;max-width:790px;color:#e5d2b1;font-size:11px;line-height:1.45;background:#0c1a27dc;border:1px solid #52617377;border-radius:5px;padding:8px 10px;text-shadow:0 1px 3px #071019;pointer-events:none}
#stage .stage-top>div:first-child{background:#0a1825e0;border:1px solid #536a7b77;border-radius:7px;padding:8px 12px;max-width:min(610px,73%)}
#stage .stage-top h1{color:#fff;text-shadow:0 1px 2px #060d16}
#stage .stage-top .scene-note{color:#d7e3eb}
#viewer-v2-source{font-size:11px;color:#9eb3c4;line-height:1.6;margin-top:11px}
#viewer-v2-source strong{color:#e4eaf0}
#viewer-v2-element{font-size:11px;color:#c1d8e2;line-height:1.55;margin:10px 0;padding:11px 12px;border:1px solid #597182;border-radius:7px;background:#192b36}
#viewer-v2-element strong{color:#ffda9c}
#viewer-v2-info{position:absolute;z-index:2;top:237px;left:25px;color:#c4d2de;background:#14212bca;border:1px solid #526577;border-radius:5px;padding:8px 10px;font-size:11px;line-height:1.5;pointer-events:none;max-width:330px}
.viewer-interaction-hint{font-size:10px;color:#9faeba;line-height:1.5;margin:12px 0}
@media(max-width:860px){#viewer-v2-toolbar{top:146px;left:12px;max-width:calc(100% - 20px)}#viewer-v2-info{top:222px;left:12px}#viewer-v2-fidelity{bottom:70px;left:12px}}
`;
document.head.appendChild(style);
const toolbar=document.createElement('div');toolbar.id='viewer-v2-toolbar';
toolbar.innerHTML=`<select id="viewer-instance" class="viewer-select" aria-label="Physical room instance"></select>
<button id="viewer-mode-full" class="viewer-btn" aria-pressed="true">Full bathroom</button>
<button id="viewer-mode-study" class="viewer-btn" aria-pressed="false">Wet-zone detail</button>
<button id="viewer-mode-context" class="viewer-btn" aria-pressed="false">Revit level context</button>
<button id="viewer-camera-iso" class="viewer-btn" title="Isometric view">3D</button>
<button id="viewer-camera-inside" class="viewer-btn" title="Elevated exterior architectural cutaway aligned to a source-hosted doorway; NOT a person standing in a door">Door cutaway</button>
<button id="viewer-camera-front" class="viewer-btn" title="Wall elevation">Elevation</button>
<button id="viewer-camera-top" class="viewer-btn" title="Plan view">Plan</button>
<button id="viewer-insertions" class="viewer-btn" aria-pressed="true" title="Actual native Revit fixture/casework insertion points and rotations, without room attribution">Native insertions ON</button>`;
stage.appendChild(toolbar);
const fidelity=document.createElement('div');fidelity.id='viewer-v2-fidelity';stage.appendChild(fidelity);
const modelInfo=document.createElement('div');modelInfo.id='viewer-v2-info';stage.appendChild(modelInfo);
document.getElementById('room-description').style.maxWidth='580px';
document.getElementById('error').textContent='WebGL could not initialize. This viewer requires an updated WebGL-enabled browser; no Revit files are modified.';
document.getElementById('spec-sub').textContent='Select a frozen product to inspect its maker, nominal size, historical price and rendered material study. Revit room-face attribution is not verified.';
const programLabel=document.createElement('div');programLabel.id='viewer-v2-source';document.getElementById('confidence').closest('.measure').after(programLabel);
const roomEvidence=document.createElement('details');
roomEvidence.id='viewer-v2-evidence';
roomEvidence.style.cssText='font-size:11px;color:#b5c9d6;line-height:1.6;margin:12px 0;padding:11px 12px;border:1px solid #43576a;border-radius:7px;background:#202d39';
roomEvidence.innerHTML='<summary style="color:#ecd4b4;font-weight:700;cursor:pointer">Room evidence & unresolved geometry</summary><div id="viewer-evidence-content" style="margin-top:10px"></div>';
programLabel.after(roomEvidence);
const selectedRevit=document.createElement('details');
selectedRevit.id='viewer-v2-element';selectedRevit.hidden=true;
selectedRevit.innerHTML='<summary style="cursor:pointer;font-weight:700;color:#f0d6ac">Native element details · unassigned</summary><div id="viewer-v2-element-detail"></div>';
roomEvidence.after(selectedRevit);
const cameraStatus=document.createElement('span');cameraStatus.id='viewer-camera-state';
cameraStatus.style.cssText='display:block;margin:9px 0;padding:8px 10px;border:1px solid #546d7c;border-radius:6px;background:#182c36;color:#c8dfdd;font:11px/1.5 Segoe UI,Arial,sans-serif';
cameraStatus.hidden=true;roomEvidence.after(cameraStatus);

function current(){return ROOMS.find(x=>x.id===state.room);}
function instance(){const r=current();return r?.physical_instances?.[state.instance]||null;}
function productList(){const r=current();return state.alt&&r?.alternative?r.alternative.products:r?.products||[];}
function productFor(which){const p=productList();return which==='wall'?p.find(x=>/wall|tub|wet/i.test(x.surface))
 :which==='floor'?p.find(x=>/level|floor|pan/i.test(x.surface))
 :p.find(x=>/niche/i.test(x.surface));}
function htmlEscape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','"':'&quot;',"'":'&#39;'}[c]));}
function stdNum(info){return info&&Number.isFinite(+info.value)?+info.value:null;}
function normalizeSize(s){
 const m=String(s||'').replace(/[×]/g,'x').match(/(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)/i);
 return m?[Math.max(.5,+m[1])/12,Math.max(.5,+m[2])/12]:[1,2];
}
function tileShade(p){
 const n=p?.name?.toLowerCase()||'';
 if(/indigo|sapphire|antique blue/.test(n))return [81,104,127];
 if(/emerald|hydro/.test(n))return [77,111,103];
 if(/charcoal|noir|gray/.test(n))return [122,125,127];
 if(/sandstone|terra|cortar|oat|bone/.test(n))return [180,165,145];
 if(/ivory|purity|alabaster|luxe/.test(n))return [223,219,208];
 return [202,200,193];
}
function tileAtlas(p,orientation){
 let pair=normalizeSize(p?.size);
 // Architectural design layout orientation has not been source-released.
 // Vertical field layouts show first dimension horizontally, second vertically.
 if(orientation==='floor'&&pair[0]<pair[1])pair=pair.slice().reverse();
 const id=(p?.name||'neutral')+'|'+pair.join(',')+'|'+orientation;
 if(materialCache.has(id))return materialCache.get(id);
 const [wft,hft]=pair;
 const glossy=/gloss|high gloss|sapphire|indigo|sandstone|antique/i.test(p?.name||'');
 const c=document.createElement('canvas');c.width=Math.min(1024,Math.max(256,Math.round(310*wft)));
 c.height=Math.min(1024,Math.max(256,Math.round(310*hft)));
 const ctx=c.getContext('2d'),base=tileShade(p);
 const gap=.0625/12; // ONE-SIXTEENTH INCH illustrative grout, NOT a selected joint.
 const gx=Math.max(1,c.width*gap/wft),gy=Math.max(1,c.height*gap/hft);
 ctx.fillStyle='rgb(146,142,135)';ctx.fillRect(0,0,c.width,c.height);
 ctx.fillStyle='rgb('+base.join(',')+')';ctx.fillRect(gx,gy,c.width-2*gx,c.height-2*gy);
 // Deterministic low-amplitude stone/ceramic variation, not fabricated material sample.
 for(let y=0;y<c.height;y+=7){
  const v=Math.sin(y*.049)+Math.sin(y*.113)*.5;
  ctx.fillStyle='rgba(248,244,233,'+(glossy?.015:.028)*(1+v*.3)+')';
  ctx.fillRect(gx+2,y,Math.max(0,c.width-2*gx-4),1.5);
 }
 const h=document.createElement('canvas');h.width=c.width;h.height=c.height;
 const hx=h.getContext('2d');
 const im=hx.createImageData(h.width,h.height);
 for(let y=0;y<h.height;y++)for(let x=0;x<h.width;x++){
  const px=4*(y*h.width+x),joint=(x<gx||x>h.width-gx||y<gy||y>h.height-gy);
  const q=joint?0.24:(0.50+.04*Math.sin(x*.071)*Math.cos(y*.092));
  im.data[px]=Math.round(127+q*5);im.data[px+1]=Math.round(127+q*3);
  im.data[px+2]=255;im.data[px+3]=255;
 }
 hx.putImageData(im,0,0);
 const normal=new THREE.CanvasTexture(h);normal.wrapS=normal.wrapT=THREE.RepeatWrapping;
 const image=new THREE.CanvasTexture(c);image.wrapS=image.wrapT=THREE.RepeatWrapping;
 image.colorSpace=THREE.SRGBColorSpace;image.anisotropy=8;
 const val={map:image,normal,units:pair,roughness:glossy?.21:.78,glossy,
  children:new Set(),surfaceTextures:new Map(),ready:Promise.resolve()};
 materialCache.set(id,val);
 if(p?.image){
  const img=new Image();
  val.ready=new Promise(resolve=>{
   img.onload=()=>{
   // Maker photo supplies ONLY broad color variation, never exact tile physical geometry.
   ctx.globalAlpha=.23;
   const scale=Math.max(c.width/img.width,c.height/img.height);
   const sw=img.width*scale,sh=img.height*scale;
   ctx.drawImage(img,(c.width-sw)/2,(c.height-sh)/2,sw,sh);
   ctx.globalAlpha=1;image.needsUpdate=true;
   // Re-upload each active independent per-plane texture from this updated
   // canvas. Avoid a shared GPU Source whose disposed clone could blank a
   // newer room during fast material switches.
   for(const child of val.children)child.needsUpdate=true;
   resolve();
   };
   img.onerror=()=>resolve(); // procedural fallback is still valid
  });
  img.src=p.image;
 }
 return val;
}
function tileMaterial(p,width,height,orientation){
 if(!p)return neutral.wall;
 const atlas=tileAtlas(p,orientation),[tw,th]=atlas.units;
 if(state.mode==='full'){
  // R047 Reviewer96 FIX: FULL-room physical material now uses the actual
  // available maker-product photograph blended into the local source tile
  // atlas, with grout normal map and PBR roughness. Explicit typed-array
  // DataTextures replace unstable CanvasTexture GPU sources: the latter were
  // visually near-black after rapid A/B room changes in headless Chrome.
  // Product image is visual evidence ONLY, never a certified installed tile
  // array, dye-lot sample, or selected grout/layout approval.
  const makePixels=(source)=>{
   const c=document.createElement('canvas');
   c.width=Math.min(512,source.width||512);
   c.height=Math.min(512,source.height||512);
   const ctx=c.getContext('2d',{willReadFrequently:true});
   ctx.drawImage(source,0,0,c.width,c.height);
   return {rgba:new Uint8Array(ctx.getImageData(0,0,c.width,c.height).data),
    width:c.width,height:c.height};
  };
  const makeMap=(source,srgb)=>{
   const frame=makePixels(source);
   const tex=new THREE.DataTexture(frame.rgba,frame.width,frame.height,
    THREE.RGBAFormat,THREE.UnsignedByteType);
   tex.flipY=true;tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
   tex.magFilter=THREE.LinearFilter;tex.minFilter=THREE.LinearMipmapLinearFilter;
   tex.generateMipmaps=true;tex.anisotropy=8;
   if(srgb)tex.colorSpace=THREE.SRGBColorSpace;
   tex.repeat.set(width/tw,height/th);
   tex.needsUpdate=true;
   return tex;
  };
  const map=makeMap(atlas.map.image,true);
  const normal=makeMap(atlas.normal.image,false);
  const glossy=atlas.glossy;
  const mat=new THREE.MeshPhysicalMaterial({map,normalMap:normal,
   normalScale:new THREE.Vector2(.11,.11),roughness:glossy?.28:.76,
   metalness:0,clearcoat:glossy?.45:.04,clearcoatRoughness:glossy?.23:.8,
   side:THREE.DoubleSide});
  // Every canvas-derived source pixel is copied into its own GPU-owned
  // Uint8Array. Vendor image may resolve after first frame; refresh this
  // material's DATA, not a shared or previously disposed canvas texture.
  atlas.ready.then(()=>{
   if(mat.userData.retired)return;
   const after=makePixels(atlas.map.image);
   const live=map.image;
   if(after.width===live.width&&after.height===live.height){
    live.data.set(after.rgba);map.needsUpdate=true;
   }
  });
  mat.userData={sourceStudy:'MAKER PHOTO BLENDED COLOR + SOURCE NOMINAL TILE/ILLUSTRATIVE 1/16in GROUT; installation color/layout NOT verified',
   tileSizeFt:[tw,th],pooledTile:true,atlas,sceneOwnedTextures:true,typedSourcePhoto:true,retired:false};
  return mat;
 }
 // Each material gets a scene-OWNED GPU texture pair. A previously cached
 // CanvasTexture pair survived geometry disposal but intermittently displayed
 // as near-black after room changes despite reported GPU READY. Do not reuse
 // disposed-scene GPU sources. Reuse only the CPU atlas canvas/image source.
 const map=new THREE.CanvasTexture(atlas.map.image);
 map.colorSpace=THREE.SRGBColorSpace;map.anisotropy=8;
 map.wrapS=map.wrapT=THREE.RepeatWrapping;
 map.repeat.set(width/tw,height/th);map.needsUpdate=true;
 const normal=new THREE.CanvasTexture(atlas.normal.image);
 normal.wrapS=normal.wrapT=THREE.RepeatWrapping;
 normal.repeat.copy(map.repeat);normal.needsUpdate=true;
 atlas.children.add(map);
 if(typeof renderer.initTexture==='function'){
  renderer.initTexture(map);renderer.initTexture(normal);
 }
 const mat=new THREE.MeshPhysicalMaterial({map,normalMap:normal,normalScale:new THREE.Vector2(.19,.19),
  roughness:atlas.roughness,metalness:0,clearcoat:atlas.glossy?.42:.03,
  clearcoatRoughness:atlas.glossy?.20:.75,side:THREE.DoubleSide,
  // Prevent dark manufacturer glossy finishes from becoming pure black on
  // rooms whose study planes have no verified surrounding reflected surfaces.
  emissive:new THREE.Color('rgb('+tileShade(p).join(',')+')'),
  emissiveIntensity:atlas.glossy?.18:.08});
 mat.userData={pooledTile:true,atlas,sceneOwnedTextures:true};return mat;
}
function addPlane(width,height,position,rotation,material,category,surfaceIndex=-1,source={}){
 if(!(width>0&&height>0))return null;
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(width,height),material);
 mesh.position.set(...position);mesh.rotation.set(...rotation);
 // Double-sided zero-thickness study surfaces can self-shadow to black while
 // switching material programs in WebGL. Revit-context solids retain shadows,
 // but these unlocated schematic planes must not claim castable wall solids.
 mesh.castShadow=false;mesh.receiveShadow=false;
 mesh.userData={category,surfaceIndex,source,...source};
 modelGroup.add(mesh);renderObjects.push(mesh);
 return mesh;
}
function outline(width,height,position,rotation,color=0x7f9cac){
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(width,height)),
 new THREE.LineBasicMaterial({color,transparent:true,opacity:.60}));
 edges.position.set(...position);edges.rotation.set(...rotation);
 modelGroup.add(edges);return edges;
}
function drawRegisteredArchitecture(arch,room,adjacent=false){
 // Native wall-location lines/thicknesses, drawing-INFERRED room assignment.
 // Geometry is an architectural reconstruction, not a Revit room solid.
 const poly=adjacent?arch.adjacent_zone_geometry?.floor_polygon_local_xz_ft:arch.floor_polygon_local_xz_ft;
 if(!poly?.length)return null;
 const xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
 const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
 const w=maxX-minX,d=maxZ-minZ,cx=(minX+maxX)/2,cz=(minZ+maxZ)/2;
 const signedArea2=poly.reduce((sum,p,i)=>{
  const q=poly[(i+1)%poly.length];
  return sum+p[0]*q[1]-q[0]*p[1];
 },0);
 const polygonOutwardSign=signedArea2>=0?-1:1;
 const shape=new THREE.Shape();shape.moveTo(poly[0][0],-poly[0][1]);
 for(let i=1;i<poly.length;i++)shape.lineTo(poly[i][0],-poly[i][1]);
 shape.closePath();
 const chosenFloor=!adjacent&&room.program?.dry_floor_retained!==true?productFor('floor'):null;
 const floorIdx=chosenFloor?productList().indexOf(chosenFloor):-1;
 const floorMaterial=adjacent?neutral.contextFloor:room.program?.dry_floor_retained?neutral.wood:
  chosenFloor?tileMaterial(chosenFloor,w,d,'floor'):neutral.flooring;
 const floor=new THREE.Mesh(new THREE.ShapeGeometry(shape),floorMaterial);
 floor.rotation.x=-Math.PI/2;floor.position.y=adjacent ? .011 : .018;
 floor.receiveShadow=true;floor.castShadow=false;
 floor.userData={category:adjacent?'ARCH_ADJACENT_FLOOR':'ARCH_REGISTERED_FLOOR',surfaceIndex:floorIdx,
  source:'NATIVE REVIT WALL FACE-DERIVED POLYGON; NAME drawing-inferred, NOT certified Room element',
  room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
  floor_area_not_a_purchase_quantity:true};
 modelGroup.add(floor);renderObjects.push(floor);
 // Ceiling datum is a non-solid plan outline at drawing height. The source
 // contains no reliable ROOM-specific ceiling cut profile; do not insert an
 // opaque slab that would be mistaken for verified roof geometry.
 // The neighboring 310 compartment is NOT 311. A 311-specific GWB datum
 // cannot be borrowed for 310 even when its levels happen to be similar.
 const ceilingEvidence=adjacent?arch.adjacent_zone_geometry?.native_ceiling_evidence:arch.native_ceiling_evidence;
 const ceilingY=ceilingEvidence?.underside_height_ft??9.25;
 const ceilingLoop=new THREE.LineLoop(
  new THREE.BufferGeometry().setFromPoints(poly.map(p=>new THREE.Vector3(p[0],ceilingY,p[1]))),
  new THREE.LineBasicMaterial({color:0xc1ac8b,transparent:true,opacity:adjacent?.19:.38}));
 ceilingLoop.userData={category:'ARCH_CEILING_EXTENT_DATUM',
  room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
  source:ceilingEvidence?'Actual Revit GWB AABB underside elevation independently matched to THIS compartment; outline XY drawing-inferred, NOT native ceiling trim mesh':'Footprint same as inferred floor face; height DRAWING 9.25 ft; NOT native ceiling solid or native ceiling evidence for this compartment',
  native_ceiling_id:ceilingEvidence?.id||null,
  native_ceiling_receipt:ceilingEvidence?.receipt_id||null,
  height_ft:ceilingY};
 modelGroup.add(ceilingLoop);renderObjects.push(ceilingLoop);
 // Deliberately separate the REAL Revit ceiling-element bounding rectangle
 // from the room-shaped ceiling witness (which is inferred from wall faces).
 // AABB is an exact source extent, NOT an actual ceiling panel/profile mesh.
 const cb=ceilingEvidence?.native_bounds_ft;
 const nativeOrigin=arch.origin_native_xy_ft;
 if(cb?.min&&cb?.max&&nativeOrigin?.length===2){
  const x0=cb.min[0]-nativeOrigin[0],x1=cb.max[0]-nativeOrigin[0];
  const z0=nativeOrigin[1]-cb.max[1],z1=nativeOrigin[1]-cb.min[1];
  if(x1>x0&&z1>z0){
   const witness=new THREE.LineLoop(
    new THREE.BufferGeometry().setFromPoints([[x0,z0],[x1,z0],[x1,z1],[x0,z1]].map(([x,z])=>
     new THREE.Vector3(x,ceilingY+.055,z))),
    new THREE.LineDashedMaterial({color:0x75c6bb,dashSize:.34,gapSize:.22,
     transparent:true,opacity:.53,depthTest:false}));
   witness.computeLineDistances();witness.renderOrder=12;
   witness.userData={category:'ARCH_NATIVE_GWB_AABB_WITNESS',
    room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
    native_ceiling_id:ceilingEvidence.id,native_ceiling_receipt:ceilingEvidence.receipt_id,
    source:'REAL READ-ONLY Revit GWB category AABB XY bounds at source underside; not exact ceiling surface, trim, soffit profile or proof of room membership',
    native_bounds_ft:cb,height_ft:ceilingY};
   modelGroup.add(witness);renderObjects.push(witness);
  }
 }
 // Tie the real source-wall-face floor polygon to the independently sourced
 // ceiling underside as an OPEN WIRE ENVELOPE, not as a guessed solid slab.
 // This makes recesses, returns, and 305 calibrated closures legible in 3D
 // without obscuring the selected fixtures or asserting a native Room object.
 const floorEdge=new THREE.LineLoop(
  new THREE.BufferGeometry().setFromPoints(poly.map(p=>new THREE.Vector3(p[0],.055,p[1]))),
  new THREE.LineBasicMaterial({color:0xc99c69,transparent:true,opacity:.78,depthTest:false}));
 floorEdge.renderOrder=11;
 floorEdge.userData={category:'ARCH_FLOOR_FACE_OUTLINE',
  source:'Native-wall-face polygon, NAMED ROOM membership drawing-inferred; zero-thickness visual line, not Revit slab edge',
  room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number};
 modelGroup.add(floorEdge);renderObjects.push(floorEdge);
 const cornerVectors=[];
 let lastWire=null;
 for(let i=0;i<poly.length;i++){
  const p=poly[i],prev=poly[(i+poly.length-1)%poly.length],next=poly[(i+1)%poly.length];
  const ax=p[0]-prev[0],az=p[1]-prev[1],bx=next[0]-p[0],bz=next[1]-p[1];
  const al=Math.hypot(ax,az),bl=Math.hypot(bx,bz);
  const turn=al*bl>.000001?Math.acos(Math.max(-1,Math.min(1,(ax*bx+az*bz)/(al*bl)))):0;
  // Buffer-derived rounded corners include many sub-inch tessellation points:
  // show only distinguishable planar corners, never a dense picket fence.
  if(turn<.12||(lastWire&&Math.hypot(p[0]-lastWire[0],p[1]-lastWire[1])<.42))continue;
  cornerVectors.push(new THREE.Vector3(p[0],.055,p[1]),new THREE.Vector3(p[0],ceilingY,p[1]));
  lastWire=p;
 }
 const cornerLines=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(cornerVectors),
  new THREE.LineDashedMaterial({color:0x8eaaa9,dashSize:.23,gapSize:.19,transparent:true,opacity:.32,depthTest:false}));
 cornerLines.computeLineDistances();cornerLines.renderOrder=10;
 cornerLines.userData={category:'ARCH_INFERRED_ROOM_VERTICAL_WIRES',
  room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
  source:ceilingEvidence?'Wall-face corners extended to independently matching GWB AABB underside for THIS compartment; named-room attribution and ceiling profile inferred':'Wall-face corners extended only to DRAWING 9.25ft datum; NO native GWB ceiling matched to this compartment'};
 modelGroup.add(cornerLines);renderObjects.push(cornerLines);
 const perimeter=adjacent?arch.adjacent_zone_geometry.wall_segments:arch.wall_segments;
 const openings=adjacent?arch.adjacent_zone_geometry.openings:arch.openings;
 const h=ceilingY;
 const wallMat=adjacent?new THREE.MeshPhysicalMaterial({color:0x93a6ad,roughness:.86,transparent:true,opacity:.20,
  side:THREE.DoubleSide,depthWrite:false}):
  new THREE.MeshPhysicalMaterial({color:0xd5d0c5,roughness:.8,transparent:true,opacity:.47,
  side:THREE.DoubleSide,depthWrite:false});
 const archSource={source:'Native wall centerline, bound thickness and hosted opening; named room attribution DRAWING-INFERRED',
  room_assignment:'NOT NATIVE REVIT ROOM',floor_area_display_only:arch.floor_polygon_area_ft2};
 let walls=0,doors=0;
 // Direction indicators are not hinge/swing arcs. They reflect ONLY a
 // one-sided family bounding-box extent, when the native source supports it.
 for(const opening of openings||[]){
  const side=opening.aabb_suggested_open_side;
  if(opening.kind!=='door'||!side)continue;
  const loc=opening.location_local_ft,vec=side.inward_local_xz_direction;
  const p1=new THREE.Vector3(loc[0],.073,loc[1]);
  const p2=new THREE.Vector3(loc[0]+vec[0]*.78,.073,loc[1]+vec[1]*.78);
  const ink=new THREE.LineDashedMaterial({color:0xd9b67f,dashSize:.16,gapSize:.10,transparent:true,opacity:.65,depthTest:false});
  const shapeLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([p1,p2]),ink);
  shapeLine.computeLineDistances();shapeLine.renderOrder=15;
  shapeLine.userData={category:'ARCH_DOOR_AABB_SWING_SIDE_HINT',surfaceIndex:-1,
   revit_id:opening.id,receipt_id:opening.receipt_id,host_id:opening.host_id,
   source:side.confidence,
   native_extent_evidence:'negative '+side.bbox_extent_negative_ft+'ft / positive '+side.bbox_extent_positive_ft+'ft'};
  modelGroup.add(shapeLine);renderObjects.push(shapeLine);
 }
 for(const seg of perimeter||[]){
  const a=seg.start_local_ft,b=seg.end_local_ft;
  const dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);
  if(len<.12)continue;
  const ux=dx/len,uz=dz/len,rot=Math.atan2(-uz,ux),th=seg.thickness_ft;
  // Move the wall solid outward, keeping the source-derived inner face clear.
  const nx=-uz,nz=ux,midX=(a[0]+b[0])/2,midZ=(a[1]+b[1])/2;
  // Polygon signed winding, not room centroid, defines the outward normal:
  // concave native returns can have their centroid across an edge.
  const outSign=polygonOutwardSign;
  const wallX=midX+nx*outSign*th/2,wallZ=midZ+nz*outSign*th/2;
  // Interior review cutaway: front/north-side navigation wall stops at 3 ft.
  // Original full-height source value remains in metadata and provenance.
  const cutawayFront=!adjacent&&midZ>maxZ-.18&&Math.abs(dx)>Math.abs(dz);
  const visualH=cutawayFront?3.05:(adjacent?5.2:Math.min(h,seg.height_ft));
  const hosted=(openings||[]).filter(x=>x.host_id===seg.id&&(x.kind==='door'||x.kind==='window'));
  const cuts=[];
  for(const door of hosted){
   const p=door.location_local_ft;
   const dist=(p[0]-a[0])*ux+(p[1]-a[1])*uz;
   const perpendicular=Math.abs((p[0]-a[0])*uz-(p[1]-a[1])*ux);
   if(perpendicular>.85||dist<.35||dist>len-.35)continue;
   const width=door.nominal_width_ft;
   cuts.push({start:Math.max(0,dist-width/2),end:Math.min(len,dist+width/2),opening:door});
  }
  cuts.sort((x,y)=>x.start-y.start);
  function wallBox(from,to,y0,y1){
   if(to-from<.03||y1-y0<.03)return;
   const mesh=new THREE.Mesh(new THREE.BoxGeometry(to-from,y1-y0,th),wallMat);
   const t=(from+to)/2-len/2;
   mesh.position.set(wallX+ux*t,(y0+y1)/2,wallZ+uz*t);mesh.rotation.y=rot;
   mesh.castShadow=false;mesh.receiveShadow=false;
   mesh.userData={category:'ARCH_REGISTERED_WALL',surfaceIndex:-1,revit_id:seg.id,
    receipt_id:seg.receipt_id,thickness_ft:th,height_from_native_bounds_ft:seg.height_ft,
    visual_cutaway_height_ft:visualH,type_name:seg.type_name,
    native_location:{start:seg.native_location_start_ft,end:seg.native_location_end_ft},
    ...archSource};
   modelGroup.add(mesh);renderObjects.push(mesh);walls++;
  }
  let cursor=0;
  for(const cut of cuts){
   wallBox(cursor,cut.start,0,visualH);
   const head=visualH,openingHeight=cut.opening.nominal_height_ft;
   const sill=cut.opening.kind==='window'?Math.max(0,cut.opening.sill_height_ft||0):0;
   if(sill>0)wallBox(cut.start,cut.end,0,sill);
   if(head>sill+openingHeight)wallBox(cut.start,cut.end,sill+openingHeight,head);
   const mid=(cut.start+cut.end)/2-len/2;
   const isWindow=cut.opening.kind==='window';
   const doorLeaf=new THREE.Mesh(new THREE.BoxGeometry(cut.end-cut.start,Math.max(.05,Math.min(openingHeight,head-sill)),isWindow?.05:.105),
    isWindow?neutral.glass:neutral.contextualDoor);
   doorLeaf.position.set(wallX+ux*mid,sill+Math.max(.05,Math.min(openingHeight,head-sill))/2,wallZ+uz*mid);
   doorLeaf.rotation.y=rot;doorLeaf.castShadow=false;
   doorLeaf.userData={category:isWindow?'ARCH_HOSTED_WINDOW':'ARCH_HOSTED_DOOR_LEAF',revit_id:cut.opening.id,
    receipt_id:cut.opening.receipt_id,host_id:seg.id,nominal_width_ft:cut.opening.nominal_width_ft,
    swing:isWindow?'NOT APPLICABLE':'UNKNOWN (neutral closed-plane depiction)',source:cut.opening.source};
   modelGroup.add(doorLeaf);renderObjects.push(doorLeaf);doors++;
   // Native host and nominal family width establish an opening station,
   // but NOT a construction rough opening or door handing. Trace the two
   // nominal jamb stations and visible head/sill with zero-thickness lines;
   // never fabricate a frame stock dimension or a swing arc.
   const edgeY=Math.min(head,sill+openingHeight);
   const points=[];
   const edgePosition=t=>new THREE.Vector3(wallX+ux*(t-len/2),0,wallZ+uz*(t-len/2));
   for(const t of [cut.start,cut.end]){
    const q=edgePosition(t);
    points.push(new THREE.Vector3(q.x,sill,q.z),new THREE.Vector3(q.x,edgeY,q.z));
   }
   if(edgeY<=head+.001){
    const q0=edgePosition(cut.start),q1=edgePosition(cut.end);
    points.push(new THREE.Vector3(q0.x,edgeY,q0.z),new THREE.Vector3(q1.x,edgeY,q1.z));
   }
   if(isWindow&&sill>0){
    const q0=edgePosition(cut.start),q1=edgePosition(cut.end);
    points.push(new THREE.Vector3(q0.x,sill,q0.z),new THREE.Vector3(q1.x,sill,q1.z));
   }
   const openingTrace=new THREE.LineSegments(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({color:isWindow?0x8dc5d1:0xb88e65,transparent:true,opacity:.92,depthTest:false}));
   openingTrace.renderOrder=13;
   openingTrace.userData={category:'ARCH_HOSTED_OPENING_NOMINAL_TRACE',
    revit_id:cut.opening.id,host_id:seg.id,receipt_id:cut.opening.receipt_id,
    nominal_width_ft:cut.opening.nominal_width_ft,nominal_height_ft:openingHeight,
    source:'NATIVE HOST + NOMINAL FAMILY DIMENSIONS; line-only visual trace, NOT frame, rough opening, hinge, threshold or swing'};
   modelGroup.add(openingTrace);renderObjects.push(openingTrace);
   // Reveal DEPTH study: the host wall's bounded thickness is truly native,
   // and the two nominal insertion stations are provided by the door/window
   // family type. Draw zero-thickness wire edges spanning those wall faces,
   // explicitly NOT actual rough-opening dimensions, jamb material or swing.
   const revealPts=[];
   const qAt=(t,normal,y)=>new THREE.Vector3(
    wallX+ux*(t-len/2)+nx*normal, y,
    wallZ+uz*(t-len/2)+nz*normal);
   const halves=[-th/2,th/2];
   for(const t of [cut.start,cut.end]){
    for(const sideDepth of halves){
     revealPts.push(qAt(t,sideDepth,sill),qAt(t,sideDepth,edgeY));
    }
    revealPts.push(qAt(t,-th/2,edgeY),qAt(t,th/2,edgeY));
    if(isWindow&&sill>0)revealPts.push(qAt(t,-th/2,sill),qAt(t,th/2,sill));
   }
   for(const sideDepth of halves){
    revealPts.push(qAt(cut.start,sideDepth,edgeY),qAt(cut.end,sideDepth,edgeY));
    if(isWindow&&sill>0)revealPts.push(qAt(cut.start,sideDepth,sill),qAt(cut.end,sideDepth,sill));
   }
   const reveal=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(revealPts),
    new THREE.LineBasicMaterial({color:isWindow?0x9dc8d0:0x9ab9b3,
     transparent:true,opacity:.43,depthTest:false}));
   reveal.renderOrder=12;
   reveal.userData={category:'ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS',
    room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
    revit_id:cut.opening.id,host_id:seg.id,
    receipt_id:cut.opening.receipt_id,host_wall_receipt_id:seg.receipt_id,
    native_host_thickness_ft:th,nominal_width_ft:cut.opening.nominal_width_ft,
    nominal_height_ft:openingHeight,
    source:'REAL Revit wall bounded thickness + native hosted opening point and nominal type width/height; OPENING DEPTH WIRES only, NOT actual rough opening, construction jamb, hinge, glazing, sill detail or swing'};
   modelGroup.add(reveal);renderObjects.push(reveal);
   cursor=cut.end;
  }
  wallBox(cursor,len,0,visualH);
 }
 return {w,d,cx,cz,minX,maxX,minZ,maxZ,walls,doors,area:adjacent?arch.adjacent_zone_geometry.area_display_ft2:arch.floor_polygon_area_ft2};
}
function drawNativeFixtureOffsetWitness(nativeXY,proxyXY,revitId,receiptId,roomNumber){
 if(!Array.isArray(nativeXY)||!Array.isArray(proxyXY)||nativeXY.length<2||proxyXY.length<2)return;
 // The small blue survey disk is the ACTUAL source insertion coordinate.
 // The dashed connection to a generic offset toilet is solely explanatory:
 // it is not piping, a proposed rough-in, or a placement dimension.
 const anchor=new THREE.Mesh(new THREE.CircleGeometry(.105,24),
  new THREE.MeshBasicMaterial({color:0x4cc9d6,transparent:true,opacity:.9,
   side:THREE.DoubleSide,depthTest:false}));
 anchor.rotation.x=-Math.PI/2;anchor.position.set(nativeXY[0],.145,nativeXY[1]);
 anchor.renderOrder=16;
 const meta={category:'ARCH_NATIVE_PLUMBING_INSERTION_WITNESS',revit_id:revitId,
  receipt_id:receiptId,room_number:roomNumber,
  source:'NATIVE Revit plumbing insertion point (cyan disk); dashed line to independently offset ILLUSTRATIVE toilet proxy, NOT installed location or rough-in'};
 anchor.userData=meta;modelGroup.add(anchor);renderObjects.push(anchor);
 const delta=Math.hypot(nativeXY[0]-proxyXY[0],nativeXY[1]-proxyXY[1]);
 if(delta>.035){
  const link=new THREE.Line(
   new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(nativeXY[0],.15,nativeXY[1]),
    new THREE.Vector3(proxyXY[0],.15,proxyXY[1])]),
   new THREE.LineDashedMaterial({color:0x65cad1,dashSize:.15,gapSize:.10,
    transparent:true,opacity:.72,depthTest:false}));
  link.computeLineDistances();link.renderOrder=15;
  link.userData={...meta,category:'ARCH_NATIVE_TO_VISUAL_PROXY_OFFSET',
   illustrative_offset_ft:delta};
  modelGroup.add(link);renderObjects.push(link);
 }
}
function drawNativeToiletAABBWitness(bounds,roomNumber){
 const lo=bounds?.min_local_xyz_ft,hi=bounds?.max_local_xyz_ft;
 if(!lo||!hi||lo.length!==3||hi.length!==3)return false;
 const w=hi[0]-lo[0],h=hi[1]-lo[1],d=hi[2]-lo[2];
 if(!(w>.2&&h>.2&&d>.2&&w<8&&h<8&&d<8))return false;
 // Actual Revit 270AA.101 element AABB, not actual family surface. Wire
 // edges preserve access to the room and visibly distinguish measured
 // source extents from the diagram toilet and its offset insertion marker.
 const box=new THREE.BoxGeometry(w,h,d);
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(box),
  new THREE.LineDashedMaterial({color:0x4faab0,dashSize:.17,gapSize:.11,
   transparent:true,opacity:.62,depthTest:false}));
 edges.position.set((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);
 edges.computeLineDistances();edges.renderOrder=12;
 edges.userData={category:'ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS',
  room_number:roomNumber,revit_id:bounds.revit_id,
  receipt_id:bounds.receipt_id,source:bounds.confidence,
  native_aabb_dimensions_ft:[w,h,d],
  native_bounds_ft:bounds.bounds_native_ft,
  not_family_solid:true,not_clearance_or_rough_in:true};
 modelGroup.add(edges);renderObjects.push(edges);
 return true;
}
function drawPH4AdjacentNativeFixtures(arch,side){
 const z=arch.adjacent_zone_geometry;
 const items=z?.native_fixture_evidence||[];
 const map=new Map(items.map(x=>[x.kind,x]));
 const toilet=map.get('toilet');
 if(toilet){
  const p=toilet.location_local_xz_ft;
  if(toilet.bounds_native_ft){
   const bb=toilet.bounds_native_ft,lo=bb.min,hi=bb.max;
   const ox=arch.origin_native_xy_ft[0],oy=arch.origin_native_xy_ft[1],level=arch.native_level_elevation_ft;
   drawNativeToiletAABBWitness({
    min_local_xyz_ft:[lo[0]-ox,lo[2]-level,oy-hi[1]],
    max_local_xyz_ft:[hi[0]-ox,hi[2]-level,oy-lo[1]],
    revit_id:toilet.id,receipt_id:toilet.receipt_id,
    bounds_native_ft:bb,
    confidence:'REAL native 310 Revit toilet family AABB, NOT family solid or verified rough-in; 310 attribution drawing-inferred'},'310'+side);
  }
  const sign=side==='A'?-1:1; // inward from east and west outer wall respectively
  const x=p[0]+sign*1.03;
  drawNativeFixtureOffsetWitness(p,[x,p[1]],toilet.id,toilet.receipt_id,'310'+side);
  const fixture=drawPlanFixtureSymbol('toilet',x,p[1],side==='A'?Math.PI/2:-Math.PI/2,{
   room_number:'310'+side,native_anchor_id:toilet.id,native_anchor_receipt_id:toilet.receipt_id,
   native_anchor_coordinate_ft:toilet.native_insertion_ft,illustrative_offset_from_anchor_ft:1.03});
  if(fixture)fixture.userData={context:'310'+side,confidence:'Native plumbing location; 1.03ft illustrative toilet proxy offset, not a verified family solid'};
 }
 const countertop=map.get('countertop');
 if(countertop?.bounds_native_ft){
  const bb=countertop.bounds_native_ft;
  const width=bb.max[0]-bb.min[0],depth=bb.max[1]-bb.min[1];
  const minY=Math.max(0,bb.min[2]-arch.native_level_elevation_ft),
   maxY=Math.min(9.25,bb.max[2]-arch.native_level_elevation_ft);
  if(width>.6&&depth>.6&&maxY>minY){
   const mesh=new THREE.Mesh(new THREE.BoxGeometry(width,maxY-minY,depth),
    new THREE.MeshPhysicalMaterial({color:0xaeb3b0,roughness:.57,metalness:0,
     transparent:true,opacity:.52,side:THREE.DoubleSide,depthWrite:false}));
   const x=(bb.max[0]+bb.min[0])/2-arch.origin_native_xy_ft[0],
    zz=arch.origin_native_xy_ft[1]-(bb.max[1]+bb.min[1])/2;
   mesh.position.set(x,(maxY+minY)/2,zz);
   mesh.userData={category:'ARCH_NATIVE_CASEWORK_AABB_STUDY',surfaceIndex:-1,
    revit_id:countertop.id,receipt_id:countertop.receipt_id,
    room_number:'310'+side,
    source:'Native 310 countertop AABB center / category bounds; NOT native insertion or certified cabinet solid',
    coordinate_reference_kind:countertop.coordinate_reference_kind,
    native_insertion_ft:countertop.native_insertion_ft,
    native_bounds_center_ft:countertop.native_bounds_center_ft,
    context:'310'+side};
   modelGroup.add(mesh);renderObjects.push(mesh);
   const top=new THREE.Mesh(new THREE.BoxGeometry(width,.11,depth),
    new THREE.MeshPhysicalMaterial({color:0xdbd9d1,roughness:.28,clearcoat:.18,
     transparent:true,opacity:.80}));
   top.position.set(x,maxY+.04,zz);top.userData={...mesh.userData};
   modelGroup.add(top);renderObjects.push(top);
  }
 }
 const lav=map.get('lavatory_reference');
 if(lav){
  const p=lav.location_local_xz_ft;
  const locator=new THREE.Mesh(new THREE.RingGeometry(.10,.18,28),
   new THREE.MeshBasicMaterial({color:0xb6dfec,side:THREE.DoubleSide,transparent:true,opacity:.8,depthWrite:false}));
  locator.rotation.x=-Math.PI/2;locator.position.set(p[0],3.16,p[1]);
  locator.userData={category:'ARCH_NATIVE_FIXTURE_2D_LOCATOR',surfaceIndex:-1,revit_id:lav.id,
   receipt_id:lav.receipt_id,context:'310'+side,
   source:'Actual lavatory-associated native insertion; family identification and solid NOT CERTIFIED'};
  modelGroup.add(locator);renderObjects.push(locator);
 }
}
function drawRegisteredCasework(arch,room){
 const items=arch?.native_casework_proxies||[];
 const hasSelectedBasin=!/basin UNSELECTED|sink UNSELECTED/i.test(room.program?.plumbing_truth||'');
 let drawn=0;
 for(const item of items){
  const w=item.width_x_ft,d=item.depth_z_ft;
  if(!(w>.7&&d>.7))continue;
  const z0=Math.max(0,item.min_height_ft),z1=Math.min(5,item.max_height_ft);
  if(z1<=z0)continue;
  const x=item.local_center_xz_ft[0],zz=item.local_center_xz_ft[1];
  const base=new THREE.Mesh(new THREE.BoxGeometry(w,z1-z0,d),
   new THREE.MeshPhysicalMaterial({color:0xada79d,roughness:.60,metalness:0,
    transparent:true,opacity:.68,side:THREE.DoubleSide,depthWrite:false}));
  base.position.set(x,(z0+z1)/2,zz);
  base.userData={category:'ARCH_NATIVE_CASEWORK_AABB_STUDY',surfaceIndex:-1,
   revit_id:item.id,receipt_id:item.receipt_id,
   source:'READ ONLY Revit category native AABB; not a certified physical cabinet/vanity solid',
   name:'Countertop',room_id:instance()?.room_number,bounds_ft:item.native_bounds_ft,
   room_assignment:'DRAWING INFERRED',material:'UNSELECTED NEUTRAL STUDY'};
  modelGroup.add(base);renderObjects.push(base);
  // The source AABB is not a finished stone shape; this neutral top/cabinet
  // separation improves legibility without making a source-material claim.
  const top=new THREE.Mesh(new THREE.BoxGeometry(w+.025,.095,d+.025),
   new THREE.MeshPhysicalMaterial({color:0xe0dcd2,roughness:.36,clearcoat:.18,
    transparent:true,opacity:.91,side:THREE.DoubleSide}));
  top.position.set(x,z1+.03,zz);
  top.userData={...base.userData,category:'ARCH_NATIVE_COUNTERTOP_VISUAL'};
  modelGroup.add(top);renderObjects.push(top);
  if(hasSelectedBasin&&w>.95&&d>.96&&z1>1.8){
   // Basin is a visibly generic rendering atop source countertop bounds;
   // actual basin selection, opening, rough-in and faucet point NOT certified.
   const sourceSink=item.closest_native_plumbing_insertion;
   const sinkX=sourceSink?.location_local_xz_ft?.[0]??x;
   const sinkZ=sourceSink?.location_local_xz_ft?.[1]??zz;
   const basin=new THREE.Mesh(new THREE.SphereGeometry(1,28,14,0,Math.PI*2,0,Math.PI/2),
    neutral.porcelain);
   basin.scale.set(Math.min(.52,w*.31),.10,Math.min(.38,d*.30));
   basin.rotation.x=Math.PI;
   basin.position.set(sinkX,z1+.065,sinkZ);
   basin.userData={...base.userData,category:'ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY',
    source:sourceSink?'Generic basin placed at nearby native plumbing insertion; exact fixture/basin identity UNVERIFIED':
     'Generic countertop basin diagram; native source provides countertop bounds only',
    plumbing_reference_id:sourceSink?.id||null,
    plumbing_reference_receipt:sourceSink?.receipt_id||null};
   modelGroup.add(basin);renderObjects.push(basin);
   const drain=new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,.015,20),neutral.metal);
   drain.position.set(sinkX,z1+.11,sinkZ);
   drain.userData={...basin.userData};modelGroup.add(drain);renderObjects.push(drain);
  }
  drawn++;
 }
 return drawn;
}
function buildPH4Registered(room,inst,arch){
 const main=drawRegisteredArchitecture(arch,room);
 if(!main)return;
 const wetSide=inst?.plan_shower_side,sign=wetSide==='left'?-1:1;
 const wallP=productFor('wall'),floorP=productFor('floor');
 const wallIndex=productList().indexOf(wallP),floorIndex=productList().indexOf(floorP);
 const s=room.wet_zone_schematic||{},long=Math.min(main.d,stdNum(s.width)||5),
  short=Math.min(main.w,stdNum(s.depth)||2.54),
  h=arch.native_ceiling_evidence?.underside_height_ft||9.25;
 const outerX=sign*main.w/2,wetCenter=sign*(main.w/2-short/2);
 // On source-derived inner wall faces, tile is offset 1/4 inch inward to
 // avoid coplanarity against the physically thick wall solids.
 const source={source:'Frozen Pienza Terra + source-dimensioned wet run projected onto native-derived 311 wall faces',
  revit_wall_alignment:'NATIVE FACE DERIVED, NAMED-ROOM ASSIGNMENT INFERRED',room_number:inst.room_number};
 if(wallP){
  addPlane(long,h,[outerX-sign*.021,h/2,0],[0,Math.PI/2,0],
   tileMaterial(wallP,long,h,'wall'),'FULL_ROOM_WET_WALL',wallIndex,{...source,wall:'W1',verified_hand:wetSide});
  for(const [wall,z] of [['W2',-main.d/2+.02],['W3',main.d/2-.02]]){
   // The +Z wall is also the exterior cutaway camera's near side. In the
   // general Full Bathroom review only, lower its display height to expose
   // the PH4 311 shower pan and 310 relationship. Wet Zone Study remains full
   // source height and purchase/tile geometry is never recalculated.
   const visualH=wall==='W3'?Math.min(h,2.8):h;
   addPlane(short,visualH,[wetCenter,visualH/2,z],[0,0,0],tileMaterial(wallP,short,visualH,'wall'),
    'FULL_ROOM_WET_WALL',wallIndex,{...source,wall,verified_hand:wetSide,
     full_specification_height_ft:h,rendered_cutaway_height_ft:visualH,
     cutaway_only_visualization:wall==='W3',material_quantities_unchanged:true});
  }
 }
 if(room.program?.pan_selected===true){
  addPlane(short,long,[wetCenter,.042,0],[-Math.PI/2,0,0],
   floorP?tileMaterial(floorP,short,long,'floor'):neutral.flooring,'FULL_ROOM_SELECTED_PAN_SCHEMATIC',floorIndex,
   {...source,selected_pan:true,additional_purchase_area:null,drain_location:null,slope:null});
 }
 const side=inst.room_number.endsWith('A')?'A':'B';
 if(arch.adjacent_zone_geometry){
  const adj=drawRegisteredArchitecture(arch,room,true);
  if(adj){
   addPlanLabel('310'+side+' '+(side==='A'?'WIC4':'BATH4'),adj.cx,adj.cz);
   // 310 equipment is tied to separately sourced native plumbing insertions
   // and casework bounds, never incorporated into 311 wet material quantities.
   drawPH4AdjacentNativeFixtures(arch,side);
  }
 }
 addMarker();
 modeInfo='PH-BATH4 '+inst.room_number+' / 311 source wall-face reconstruction. '+main.area.toFixed(2)+
  ' SF inferred interior polygon from native Revit wall location lines and measured bounding thickness. '+
  main.doors+' hosted door leaf(s) with nominal 28-inch type width; door swing and rough opening unverified. '+
  'Separate 310'+side+' compartment with read-only native toilet and countertop source markers, excluded from 311 purchase quantities. '+
  'Original 40.2 SF combined LEVEL/POINT PAN unchanged; drawing 27.08 versus frozen 35 SF unresolved. '+
  (arch.native_ceiling_evidence?'GWB native ceiling underside '+arch.native_ceiling_evidence.underside_height_ft.toFixed(3)+' ft; frozen 9.25ft height remains a distinct source, actual ceiling profile unverified. ':'')+
  'Front W3 Pienza wall is visually lowered only in Full Bathroom to expose shower pan; full tile height and quantities unchanged in Wet Zone Study. '+
  'No invented niche, glass partition or precise point drain.';
 modelInfo.textContent='311'+side+' NATIVE WALL-FACE STUDY · '+main.w.toFixed(3)+' × '+main.d.toFixed(3)+
  ' ft · '+main.walls+' wall parts · '+main.doors+' hosted door(s); room assignment drawing-inferred';
}
function addMarker(color=0x7c8b9a){
 const grid=new THREE.GridHelper(28,28,color,0x506270);
 grid.material.transparent=true;grid.material.opacity=.16;grid.position.y=-.05;
 modelGroup.add(grid);
}
function updateViewConstraints(mode){
 orbit.maxDistance=mode==='context'?260:80;
 camera.near=.025;camera.far=1400;camera.updateProjectionMatrix();
}
function clearGeometry(){
 const old=modelGroup;modelGroup=new THREE.Group();scene.add(modelGroup);scene.remove(old);
 old.traverse(o=>{
  if(o.geometry)o.geometry.dispose();
  if(o.material?.userData?.ownClonedMaps){
   o.material.userData.atlas?.children?.delete(o.material.map);
   o.material.map?.dispose();o.material.normalMap?.dispose();o.material.dispose();
  }
  if(o.material?.userData?.pooledTile){
   o.material.userData.retired=true;
   if(o.material.userData.sceneOwnedTextures){
    o.material.userData.atlas?.children?.delete(o.material.map);
    o.material.map?.dispose();o.material.normalMap?.dispose();
   }
   o.material.dispose();
  }
  if(o.material?.userData?.ownDiagramLabelTexture){
   o.material.map?.dispose();o.material.dispose();
  }
  if(o.material?.isLineBasicMaterial)o.material.dispose();
 });
 renderObjects=[];materialObjects=[];sceneBounds=null;
}
function addPlanLabel(text,x,z,color='#dce5df'){
 const c=document.createElement('canvas');c.width=440;c.height=88;
 const ctx=c.getContext('2d');ctx.clearRect(0,0,440,88);ctx.fillStyle='rgba(14,27,38,.82)';
 ctx.fillRect(0,0,440,88);ctx.strokeStyle='#ba9a72';ctx.lineWidth=3;ctx.strokeRect(2,2,436,84);
 ctx.font='bold 32px Segoe UI, sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=color;
 ctx.fillText(text,220,44,418);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 const mat=new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false,side:THREE.DoubleSide});
 mat.userData={ownDiagramLabelTexture:true};
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(3.65,.73),mat);
 mesh.rotation.x=-Math.PI/2;mesh.position.set(x,.16,z);
 modelGroup.add(mesh);return mesh;
}
function drawPlanFixtureSymbol(kind,x,z,rotate=0,metadata={}){
 // Schematic diagram volumes from the latest floor plan's toilet/lavatory
 // pictograms. Dimensions are NOT manufacturer family dimensions or clearances.
 const root=new THREE.Group();root.position.set(x,.12,z);root.rotation.y=rotate;
 const porcelain=new THREE.MeshStandardMaterial({color:0xe4e2d9,roughness:.23,metalness:0});
 const brass=new THREE.MeshStandardMaterial({color:0x555f63,metalness:.75,roughness:.32});
 if(kind==='toilet'){
  const tank=new THREE.Mesh(new THREE.BoxGeometry(1.18,.62,.34),porcelain);
  tank.position.set(0,.43,-.65);root.add(tank);
  const bowl=new THREE.Mesh(new THREE.SphereGeometry(1,20,12),porcelain);
  bowl.scale.set(.69,.23,.90);bowl.position.set(0,.29,.13);root.add(bowl);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.46,.048,8,28),brass);
  ring.scale.y=1.32;ring.rotation.x=-Math.PI/2;ring.position.set(0,.53,.08);root.add(ring);
 }else if(kind==='lavatory'){
  const basin=new THREE.Mesh(new THREE.BoxGeometry(1.5,.20,1.15),porcelain);
  basin.position.y=.30;root.add(basin);
  const inner=new THREE.Mesh(new THREE.SphereGeometry(1,20,12),brass);
  inner.scale.set(.52,.012,.35);inner.position.set(0,.418,0);root.add(inner);
  const tap=new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.35,10),brass);
  tap.position.set(0,.62,-.4);root.add(tap);
 }else if(kind==='vanity'){
  const base=new THREE.Mesh(new THREE.BoxGeometry(Math.max(1.4,metadata.width_ft||3.4),2.3,1.65),
   new THREE.MeshStandardMaterial({color:0xb0a293,roughness:.63}));
  base.position.set(0,1.15,0);root.add(base);
  const top=new THREE.Mesh(new THREE.BoxGeometry(Math.max(1.4,metadata.width_ft||3.4),.12,1.72),porcelain);
  top.position.set(0,2.37,0);root.add(top);
 }else if(kind==='tub'||kind==='tub-reference'){
  const width=metadata.width_ft||4.95,depth=metadata.depth_ft||2.52;
  const ref=kind==='tub-reference';
  const tubMat=new THREE.MeshPhysicalMaterial({color:ref?0xa3b9ca:0xf2f0e9,roughness:.21,
   transparent:ref,opacity:ref?.47:1,side:THREE.DoubleSide,depthWrite:!ref});
  // Four-sided hollow bathing vessel, not a filled opaque 5-ft cube. Exterior
  // overall bounds follow Duravit model dimensions ONLY for selected tub
  // programs; family solid and installation clearances are still illustrative.
  const wall=.14,height=1.46;
  const bottom=new THREE.Mesh(new THREE.BoxGeometry(width-.12,.12,depth-.12),tubMat);
  bottom.position.y=.23;root.add(bottom);
  for(const sx of [-1,1]){
   const side=new THREE.Mesh(new THREE.BoxGeometry(wall,height,depth),tubMat);
   side.position.set(sx*(width/2-wall/2),height/2+.12,0);root.add(side);
  }
  for(const sz of [-1,1]){
   const end=new THREE.Mesh(new THREE.BoxGeometry(width-2*wall,height,wall),tubMat);
   end.position.set(0,height/2+.12,sz*(depth/2-wall/2));root.add(end);
  }
  const vessel=new THREE.Mesh(new THREE.BoxGeometry(width-2*wall,.04,depth-2*wall),
   new THREE.MeshPhysicalMaterial({color:ref?0x819bac:0xdfe9e9,roughness:.22,
    transparent:ref,opacity:ref?.28:.7,depthWrite:!ref}));
  vessel.position.y=.29;root.add(vessel);
  if(!ref){
   const drain=new THREE.Mesh(new THREE.CylinderGeometry(.055,.055,.016,16),brass);
   drain.position.set(0,.328,0);root.add(drain);
   const spout=new THREE.Mesh(new THREE.CylinderGeometry(.035,.035,.23,10),brass);
   spout.position.set(0,1.65,-depth/2+.22);root.add(spout);
  }
 }else if(kind==='shower-reference'){
  const width=metadata.width_ft||3.2,depth=metadata.depth_ft||3.2;
  const mat=new THREE.MeshStandardMaterial({color:0x7e9d9d,roughness:.6,transparent:true,opacity:.35,side:THREE.DoubleSide});
  const footprint=new THREE.Mesh(new THREE.PlaneGeometry(width,depth),mat);
  footprint.rotation.x=-Math.PI/2;footprint.position.y=-.07;root.add(footprint);
  const frame=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(width,depth)),
   new THREE.LineBasicMaterial({color:0x769da5,transparent:true,opacity:.85}));
  frame.position.y=-.06;frame.rotation.x=-Math.PI/2;root.add(frame);
 }else return;
 modelGroup.add(root);
 // Raycast only the schematic volumes. Do not expose them as Revit fixtures.
 root.traverse(o=>{if(o.isMesh){
  o.userData={category:'PLAN_SCHEMATIC_FIXTURE',surfaceIndex:-1,
   source:'Latest architectural plan pictogram; appearance and size ILLUSTRATIVE',
   kind,room_number:metadata.room_number,not_native_revit_family:true,
   native_anchor_id:metadata.native_anchor_id||null,
   native_anchor_receipt_id:metadata.native_anchor_receipt_id||null,
   native_anchor_coordinate_ft:metadata.native_anchor_coordinate_ft||null,
   illustrative_offset_from_anchor_ft:metadata.illustrative_offset_from_anchor_ft??null,
   fixture_model:metadata.nominal_model_sku||null,
   source_row_id:metadata.source_row_id||null,
   drawing_calibration_delta_ft:metadata.drawing_calibration_delta_ft??null,
   fixture_dimensions:metadata.nominal_model_sku?[metadata.width_ft,metadata.depth_ft]:null,
   fixture_coordinate_certified:false};
  renderObjects.push(o);
 }});
 return root;
}
function diagramPointWithinPolygon(x,z,poly){
 let inside=false;
 for(let i=0,j=poly.length-1;i<poly.length;j=i++){
  const a=poly[i],b=poly[j];
  if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])
   inside=!inside;
 }
 return inside;
}
function diagramRectOverlapsNativeCountertop(x,z,w,d,rotation,counter){
 // Separating-axis test between an intentionally generic ORIENTED fixture
 // footprint and the actual axis-aligned native countertop BOUNDING BOX.
 // This is a VISUAL conflict veto, not an installation-clearance dimension.
 const p=[[-w/2,-d/2],[-w/2,d/2],[w/2,d/2],[w/2,-d/2]].map(([u,v])=>
  [x+u*Math.cos(rotation)+v*Math.sin(rotation),z-u*Math.sin(rotation)+v*Math.cos(rotation)]);
 const [cx,cz]=counter.local_center_xz_ft,hw=counter.width_x_ft/2,hd=counter.depth_z_ft/2;
 const q=[[cx-hw,cz-hd],[cx-hw,cz+hd],[cx+hw,cz+hd],[cx+hw,cz-hd]];
 for(const axis of [[1,0],[0,1],[Math.cos(rotation),-Math.sin(rotation)],[Math.sin(rotation),Math.cos(rotation)]]){
  const a=p.map(v=>v[0]*axis[0]+v[1]*axis[1]);
  const b=q.map(v=>v[0]*axis[0]+v[1]*axis[1]);
  if(Math.max(...a)<=Math.min(...b)+.015||Math.max(...b)<=Math.min(...a)+.015)return false;
 }
 return true;
}
function addUnlocatedFixtureMarker(type,x,z,reason,roomNumber){
 // A 2-D ring is a plan ANNOTATION, intentionally not a volumetric family
 // and not a relocated bathroom fixture.
 const mat=new THREE.MeshBasicMaterial({color:0xe2b179,transparent:true,opacity:.84,
  side:THREE.DoubleSide,depthWrite:false});
 const ring=new THREE.Mesh(new THREE.RingGeometry(.13,.225,28),mat);
 ring.rotation.x=-Math.PI/2;ring.position.set(x,.075,z);
 ring.userData={category:'PLAN_SCHEMATIC_FIXTURE',surfaceIndex:-1,
  source:'2D PLAN ANNOTATION ONLY: 3D proxy withheld '+reason,
  kind:type+' (UNLOCATED 2D)',room_number:roomNumber,not_native_revit_family:true,
  fixture_model:null,fixture_dimensions:null,fixture_coordinate_certified:false};
 modelGroup.add(ring);renderObjects.push(ring);
}
function addRoomPlanSymbols(room,inst,w,d){
 const spec=room.full_room_plan?.fixture_symbol_diagram;
 if(!spec)return {rendered:0,suppressed:0};
 const mirrored=inst?.plan_is_mirrored_B===true;
 const p=room.wet_zone_schematic||{};
 const arch=inst?.architecture,poly=arch?.floor_polygon_local_xz_ft;
 let rendered=0,suppressed=0,sourceCaseworkReplaced=0;
 for(const symbol of spec.items||[]){
  const xfrac=mirrored?1-symbol.x_fraction:symbol.x_fraction;
  let x=(xfrac-.5)*w,z=(symbol.z_fraction-.5)*d;
  const type=symbol.kind;
  if(type==='tub'&&arch?.selected_tub_unlocated_reason){
   // A selected SKU is NOT a verified installation coordinate. Source casework
   // or toilet intersection takes precedence over an attractive 3D vessel.
   addUnlocatedFixtureMarker('tub',x,z,arch.selected_tub_unlocated_reason,inst.room_number);
   suppressed++;continue;
  }
  if((type==='lavatory'||type==='vanity')&&arch?.native_casework_proxies?.length){
   // Physical countertop source bounds replace the outdated plan-relative
   // lavatory block; a second at the diagram coordinate would overlap.
   sourceCaseworkReplaced++;
   continue;
  }
  const sourceAnchor=type==='toilet'?arch?.toilet_proxy_anchor:null;
  if(sourceAnchor){
   [x,z]=sourceAnchor.illustrative_proxy_center_xz_ft;
  }
  const isTub=type==='tub'||type==='tub-reference';
  const tubFit=type==='tub'?arch?.selected_tub_proxy:null;
  if(tubFit){[x,z]=tubFit.local_center_xz_ft;}
  const vertical=tubFit?tubFit.rotation_degrees===90:isTub&&(w>6.2||room.id==='TX-BATH4');
  const long=stdNum(p.width)||5,short=stdNum(p.depth)||2.5;
  const geometryWidth=tubFit?tubFit.nominal_width_ft:isTub?Math.min(long,vertical?d*.93:w*.92):
   type==='toilet'?1.4:type==='lavatory'?1.5:type==='vanity'?Math.min(4,w*.52):2.6;
  const geometryDepth=tubFit?tubFit.nominal_depth_ft:isTub?Math.min(short,vertical?w*.92:d*.92):
   type==='toilet'?2.05:type==='lavatory'?1.15:type==='vanity'?1.72:2.6;
  const facing=sourceAnchor?.illustrative_front_vector_local_xz;
  const rotation=facing?Math.atan2(facing[0],facing[1]):vertical?Math.PI/2:0;
  let reason=null;
  if(arch&&poly?.length){
   // All sample corners must lie strictly inside native wall-face footprint.
   const corners=[[-1,-1],[-1,1],[1,-1],[1,1]];
   for(const [sx,sz] of corners){
    const ux=sx*geometryWidth*.5,uz=sz*geometryDepth*.5;
    const px=x+ux*Math.cos(rotation)+uz*Math.sin(rotation);
    const pz=z-ux*Math.sin(rotation)+uz*Math.cos(rotation);
    if(!diagramPointWithinPolygon(px,pz,poly)){reason='outside native wall-face polygon';break;}
   }
   if(!reason&&!tubFit){
    for(const counter of arch.native_casework_proxies||[]){
     if(diagramRectOverlapsNativeCountertop(x,z,geometryWidth,geometryDepth,rotation,counter)){
      reason='generic '+type+' footprint conflicts with native Countertop AABB '+counter.id;
      break;
     }
    }
   }
   // Neutral closed door plane carries no swing or hinge claim. This is a
   // conservative diagram-vs-nominal-opening clearance gate, NOT a code
   // maneuvering-clearance assessment or installation dimension.
   if(!reason){
    for(const op of arch.openings||[]){
     if(op.kind!=='door')continue;
     const q=op.location_local_ft,dist=Math.hypot(x-q[0],z-q[1]);
     const clearance=op.nominal_width_ft/2+Math.min(1.25,Math.hypot(geometryWidth,geometryDepth)/2)+.15;
     if(dist<clearance){reason='too close to hosted native door '+op.id+' (swing unknown)';break;}
    }
   }
  }
  if(reason){
   suppressed++;
   addUnlocatedFixtureMarker(type,x,z,reason,inst?.room_number);
   continue;
  }
  rendered++;
  if(type==='tub'||type==='tub-reference'){
   // Local tub long dimension is X; 90-degree rotation makes length run Z.
   drawPlanFixtureSymbol(type,x,z,rotation,{room_number:inst?.room_number,width_ft:geometryWidth,
    depth_ft:geometryDepth,nominal_model_sku:tubFit?.model_or_sku,
    drawing_calibration_delta_ft:tubFit?.calibrated_symbol_displacement_ft,
    source_row_id:tubFit?.source_row_id});
   if(type==='tub-reference')addPlanLabel('ARCH DRAWING TUB / UNSELECTED',x,z,'#d9c3a5');
  }else if(type==='shower-reference'){
   drawPlanFixtureSymbol(type,x,z,0,{room_number:inst?.room_number,width_ft:Math.min(w*.44,stdNum(p.width)||3.2),
    depth_ft:Math.min(d*.40,stdNum(p.depth)||3.2)});
  }else{
   drawPlanFixtureSymbol(type,x,z,rotation,{room_number:inst?.room_number,
    width_ft:Math.min(4,w*.52),
    native_anchor_id:sourceAnchor?.native_plumbing_id,
    native_anchor_receipt_id:sourceAnchor?.receipt_id,
    native_anchor_coordinate_ft:sourceAnchor?.native_insertion_ft,
    illustrative_offset_from_anchor_ft:sourceAnchor?.offset_from_native_insertion_ft});
  }
 }
 return {rendered,suppressed,sourceCaseworkReplaced};
}
function buildPH4FullRoom(room,inst){
 if(inst?.architecture?.floor_polygon_local_xz_ft){
  return buildPH4Registered(room,inst,inst.architecture);
 }
 // A2.2 2026-11-05: 311A and 311B are truly MIRRORED 5'-5" x 5'-0"
 // shower compartments, and the adjoining 310 spaces are not equivalent:
 // 310A is WIC4; 310B is the separate toilet/lav BATH4 zone.
 // No bath-area takeoff, construction door rough opening or fixture solid.
 const plan=room.full_room_plan,w=plan.width_ft,d=plan.depth_ft,h=9.25;
 const entry=inst?.plan_entry_side||'UNVERIFIED',adj=inst?.adjacent_zone;
 const wetSide=inst?.plan_shower_side||'UNVERIFIED';
 const wallP=productFor('wall'),floorP=productFor('floor');
 const wallIndex=productList().indexOf(wallP),floorIndex=productList().indexOf(floorP);
 const study={source:plan.plan_source,instance:inst?.room_number,
  measured_by:'DRAWING ANNOTATION, NOT NATIVE ROOM SOLID',room_number:inst?.room_number};
 const floorMat=floorP?tileMaterial(floorP,w,d,'floor'):neutral.flooring;
 addPlane(w,d,[0,.016,0],[-Math.PI/2,0,0],floorMat,'DRAWING_FULL_ROOM_FLOOR_STUDY',floorIndex,
  {...study,room_area_unverified:true,display_only_area_ft2:plan.display_area_ft2,
   purchase_area_change:false});
 outline(w,d,[0,.024,0],[-Math.PI/2,0,0],0xd8b679);
 // Schematic WINDOW-WALL at south: glazing size and actual opening are NOT
 // dimensioned, so show a translucent continuous façade, not a fake cutout.
 addPlane(w,h,[0,h/2,d/2],[0,0,0],enclosureSide,'DRAWING_FULL_ROOM_PERIMETER',-1,
  {...study,side:'south exterior',window_dimensions:null});
 // REAL distinction from the architect's drawing: an open entry on the
 // bedroom-facing side in its front half, mirrored between 311A and 311B.
 const sideMat=enclosureSide;
 const fullWallSide=entry==='left'?'right':'left';
 const xFull=fullWallSide==='left'?-w/2:w/2;
 addPlane(d,h,[xFull,h/2,0],[0,Math.PI/2,0],sideMat,'DRAWING_FULL_ROOM_PERIMETER',-1,
  {...study,side:fullWallSide,entry:false});
 const xEntry=entry==='left'?-w/2:w/2;
 const wallRun=d/2;
 addPlane(wallRun,h,[xEntry,h/2,-d/2+wallRun/2],[0,Math.PI/2,0],sideMat,
  'DRAWING_FULL_ROOM_PARTIAL_ENTRY_WALL',-1,
  {...study,side:entry,entry:true,
   'partial_wall_run_ft':wallRun,
   'dimensional_status':'APPROXIMATE WALL BREAK; opening width NOT measured'});
 const s=room.wet_zone_schematic,ww=stdNum(s?.width)||5,wd=stdNum(s?.depth)||2.54;
 // SOURCE PLAN makes the 5-ft W1 wall a LONGITUDINAL side wall; the frozen
 // 2.54-ft W2/W3 wet returns run in the transverse direction. R042's initial
 // full-width rear pan was inconsistent with the latest drawing.
 const long=Math.min(ww,d),short=Math.min(wd,w),tileH=h;
 const sign=wetSide==='left'?-1:1;
 const outerX=sign*w/2;
 const alcoveX=sign*(w/2-short/2);
 const matOuter=wallP?tileMaterial(wallP,long,tileH,'wall'):neutral.wall;
 addPlane(long,tileH,[outerX-sign*.042,tileH/2,0],[0,Math.PI/2,0],matOuter,
  'FULL_ROOM_WET_WALL',wallIndex,{...study,wall:'W1',
   placement:'DRAWING OUTER-SIDE LONG SHOWER WALL',wet_wall_only:true,verified_hand:wetSide});
 for(const [wall,z] of [['W2',-d/2+.04],['W3',d/2-.04]]){
  const mat=wallP?tileMaterial(wallP,short,tileH,'wall'):neutral.wall;
  addPlane(short,tileH,[alcoveX,tileH/2,z],[0,0,0],mat,
   'FULL_ROOM_WET_WALL',wallIndex,{...study,wall,
    placement:'DRAWING SHOWER SHORT RETURN',wet_wall_only:true,verified_hand:wetSide});
 }
 if(room.program?.pan_selected===true){
  const mat=floorP?tileMaterial(floorP,short,long,'floor'):neutral.flooring;
  addPlane(short,long,[alcoveX,.036,0],[-Math.PI/2,0,0],mat,
   'FULL_ROOM_SELECTED_PAN_SCHEMATIC',floorIndex,
   {...study,selected_pan:true,drain_center:null,slope:null,
    plan_shower_side:wetSide,
    source:'Frozen selected POINT PAN, source wet-zone rectangle; no additional SF; drain exact position UNVERIFIED'});
  outline(short,long,[alcoveX,.05,0],[-Math.PI/2,0,0],0xe9b66e);
 }
 // Drafting-derived adjacent northern compartment is INCLUDED as context
 // because 310B is also labelled BATH4, but never charged to the 311 tile pool.
 if(adj?.depth_ft>0){
  const nd=adj.depth_ft,center=-d/2-nd/2;
  const m=new THREE.MeshStandardMaterial({color:0x80919b,roughness:.9,transparent:true,opacity:.25,side:THREE.DoubleSide,depthWrite:false});
  addPlane(w,nd,[0,.006,center],[-Math.PI/2,0,0],m,
   'DRAWING_ADJACENT_UNTILED_CONTEXT',-1,
   {...study,adjacent_number:adj.number,adjacent_room_label:adj.label,tile_scope:'NOT PART OF 311 ROOM MATERIAL AREA'});
  outline(w,nd,[0,.026,center],[-Math.PI/2,0,0],0x85a0b1);
  // Reconstruct the adjoining compartment outline from the floor plan's
  // 12'-5" overall longitudinal string. Outer wall + short top wall shown
  // as subdued CONTEXT only; inner entry cutout remains unverified.
  const outerX=wetSide==='left'?-w/2:w/2;
  addPlane(nd,h,[outerX,h/2,center],[0,Math.PI/2,0],enclosureSide,
   'DRAWING_ADJACENT_BOUNDARY',-1,{...study,number:adj.number,tile_scope:'OUTSIDE 311'});
  addPlane(w,h,[0,h/2,-d/2-nd],[0,0,0],enclosureSide,
   'DRAWING_ADJACENT_BOUNDARY',-1,{...study,number:adj.number,tile_scope:'OUTSIDE 311'});
  addPlanLabel(adj.number+' '+(inst.room_number.endsWith('A')?'WIC4':'BATH4'),0,center);
  // Above plane remains unbuilt room context: no invented 310 wall/door solids.
  if(adj.drawn_fixtures?.length){
   // Both latest 310A and 310B explicitly SHOW toilet and sink despite
   // 310A's WIC4 nomenclature. Symbol coordinates scaled only from the plan,
   // never inferred as manufacturer's actual Revit family insertion points.
   const fixtureX=wetSide==='left'?-w/2+1.45:w/2-1.45;
   drawPlanFixtureSymbol('toilet',fixtureX,-d/2-nd*.65,wetSide==='left'?Math.PI/2:-Math.PI/2,
    {room_number:adj.number});
   drawPlanFixtureSymbol('lavatory',fixtureX,-d/2-nd*.88,0,{room_number:adj.number});
  }
 }
 addMarker();
 modeInfo='A2.2 LATEST OWNER-UPLOADED 2026-11-07: '+inst.room_number+' is a MIRRORED 5′-5″ × 5′-0″ shower room; open bedroom-side entry on the '+
  entry.toUpperCase()+'. Side-wall-break length approximated; actual opening dimensions unverified. '+
  'Shower along '+wetSide+' outer wall per actual plan. '+adj.number+' '+adj.label+
  ' shown in subdued plan context with schematic toilet/lav symbols, NOT part of the 311 shower material allowance. '+
  'Selected walk-in and shared Pienza LEVEL/POINT PAN original 40.2 SF pool preserved exactly once. '+
  '311 display polygon '+plan.display_area_ft2+' SF conflicts with frozen 35 SF owner figure; NO takeoff change. '+
  'No invented drain location, niche, shower glazing, slope, fixture families or wall thickness.';
 modelInfo.textContent=inst.room_number+' MIRRORED '+entry.toUpperCase()+' ENTRY, '+wetSide.toUpperCase()+' SHOWER'+
  ' · 311 '+w.toFixed(3)+'×'+d.toFixed(3)+' ft · adjacent 310 context separately';
}
function wetPlacementFromPlan(room,inst){
 // The published floor plans, NOT inferred Revit room solids, govern whether
 // the wet three-wall set is on the back, front or an outer SIDE wall.
 // For conditional baths the drawn tub is a spatial REFERENCE ONLY; the owner
 // has NOT selected either the TUB or WALK-IN program.
 const records=room.full_room_plan?.fixture_symbol_diagram?.items||[];
 const ref=records.find(x=>x.kind==='tub'||x.kind==='tub-reference'||x.kind==='shower-reference');
 if(!ref)return null;
 const xf=inst?.plan_is_mirrored_B?1-ref.x_fraction:ref.x_fraction;
 const zf=ref.z_fraction;
 let side=null;
 if(xf<=.32)side='left';
 else if(xf>=.68)side='right';
 else if(zf<=.32)side='rear';
 else if(zf>=.68)side='front';
 // A center-positioned fixture is NOT adequate evidence to assign finishes.
 return side?{side,reference_kind:ref.kind,reference_x_fraction:xf,reference_z_fraction:zf,
  source:room.full_room_plan?.plan_source,confidence:'DRAWING TRACED RELATIVE PLACEMENT; NOT NATIVE REVIT SOLID'}:null;
}
function registeredWetSupport(arch,placement,wetRun,wetDepth){
 // Only project source-selected wall finishes onto a geometrically supporting
 // native-derived wall face. A rectangular AABB alone is insufficient for
 // recessed/offset rooms. Reject a mismatched wall rather than invent tiling.
 const points=arch?.floor_polygon_local_xz_ft;
 if(!points?.length||!placement)return null;
 const side=placement.side,vertical=side==='left'||side==='right';
 const axis=vertical?0:1,along=vertical?1:0;
 const vals=points.map(p=>p[axis]),lo=Math.min(...vals),hi=Math.max(...vals);
 const face=(side==='left'||side==='rear')?lo:hi;
 let selected=null;
 for(const wall of arch.wall_segments||[]){
  const a=wall.start_local_ft,b=wall.end_local_ft;
  if(Math.abs(a[axis]-face)>.12||Math.abs(b[axis]-face)>.12)continue;
  const run=Math.abs(a[along]-b[along]);
  // A partial native wall can be a real inset/return in the source drawing.
  // Allow a modest 0.35-ft discrepancy solely to TRIM the visual tile run
  // to the actual wall face, rather than floating the extra material in space.
  // This does NOT change the source wet-wall takeoff or its recorded length.
  if(run+0.35<wetRun)continue;
  if(!selected||run>selected.run){
   const min=Math.min(a[along],b[along]),max=Math.max(a[along],b[along]);
   selected={face,run,min,max,wall_id:wall.id};
  }
 }
 if(!selected)return null;
 const range=points.map(p=>p[along]),aMin=Math.min(...range),aMax=Math.max(...range);
 const fraction=vertical?placement.reference_z_fraction:placement.reference_x_fraction;
 const target=aMin+(aMax-aMin)*fraction;
 const midpoint=Math.max(selected.min+wetRun/2,Math.min(selected.max-wetRun/2,target));
 return {...selected,center:midpoint,
  rendered_run_ft:Math.min(wetRun,selected.run),
  original_wet_run_ft:wetRun,
  run_difference_ft:Math.max(0,wetRun-selected.run),
  source:'Native wall-face run, trimmed when shorter than frozen drawing-derived wet-wall length; source quantities remain unchanged'};
}
function buildFullRoom(room){
 if(room.id==='PH-BATH4')return buildPH4FullRoom(room,instance());
 const plan=room.full_room_plan;
 if(!plan?.width_ft||!plan?.depth_ft){
  modeInfo='No dimensioned floor-plan enclosure available. Use the wet-zone detail or Revit level context.';
  addMarker();return;
 }
 const arch=instance()?.architecture;
 const reconstructed=arch?.floor_polygon_local_xz_ft?drawRegisteredArchitecture(arch,room):null;
 const w=reconstructed?.w||plan.width_ft,d=reconstructed?.d||plan.depth_ft,
  ceiling=arch?.native_ceiling_evidence?.underside_height_ft||
   stdNum(room.wet_zone_schematic?.ceiling)||9.25;
 const products=productList(),wallP=productFor('wall'),floorP=productFor('floor');
 const wallIndex=products.indexOf(wallP),floorIndex=products.indexOf(floorP);
 const isWood=room.program?.dry_floor_retained===true;
 const baseMat=isWood?neutral.wood:floorP?tileMaterial(floorP,w,d,'floor'):neutral.flooring;
 if(!reconstructed){
 addPlane(w,d,[0,.018,0],[-Math.PI/2,0,0],baseMat,
  'DRAWING_FULL_ROOM_FLOOR_STUDY',isWood?-1:floorIndex,
  {source:'SCALED ARCHITECT PLAN ENVELOPE, NOT REVIT SLAB; no purchase/takeoff computation',
   room_area_unverified:true,display_only_area_ft2:plan.display_area_ft2});
 outline(w,d,[0,.025,0],[-Math.PI/2,0,0],0xd5b68c);
 }
 const wallData={source:plan.plan_source,classification:plan.confidence,
  geometry_status:'DISTRIBUTION/RECTANGLE APPROXIMATED; NOT ROOM-SPECIFIC REVIT SOLIDS'};
 // Complete perimeter: rear and two cutaway side walls are visible.
 // Door position and rough opening have NOT been extracted; do not cut one.
 const spec=plan.fixture_symbol_diagram;
 let entry=spec?.entry_side||null;
 if(instance()?.plan_is_mirrored_B===true&&entry)entry=entry.replace('left','_').replace('right','left').replace('_','right');
 if(reconstructed){
  // Source-hosted openings are cut from the native-derived solid wall runs,
  // rather than drawing arbitrary schematic entry gaps on top of them.
 }else if(entry?.startsWith('rear-')){
  // Architectural-plan door occurs at a rear corner. The gap is illustrative
  // because the native rough opening width and wall-host profile are not read.
  const gap=Math.min(2.55,w*.44),run=w-gap;
  const cx=entry==='rear-right'?-gap/2:gap/2;
  addPlane(run,ceiling,[cx,ceiling/2,-d/2],[0,0,0],enclosureBack,'FULL_ROOM_BOUNDARY',-1,
   {...wallData,side:'rear',entry:'DRAWING INDICATED, OPENING WIDTH APPROXIMATE'});
 }else{
  addPlane(w,ceiling,[0,ceiling/2,-d/2],[0,0,0],enclosureBack,'FULL_ROOM_BOUNDARY',-1,{...wallData,side:'rear'});
 }
 if(!reconstructed){
 addPlane(d,ceiling,[-w/2,ceiling/2,0],[0,Math.PI/2,0],enclosureSide,'FULL_ROOM_BOUNDARY',-1,{...wallData,side:'left'});
 addPlane(d,ceiling,[w/2,ceiling/2,0],[0,-Math.PI/2,0],enclosureSide,'FULL_ROOM_BOUNDARY',-1,{...wallData,side:'right'});
 // Entry wall traced as a visual outline only: it remains uncut because
 // the door's offset, swing, jamb and native host wall are not certified.
 outline(w,ceiling,[0,ceiling/2,d/2],[0,0,0],0x9bafbc);
 }
 // Frozen wet-wall specification shown over the SOURCE wet-zone dimensions,
 // without claiming its ORIENTATION or placement was established on the plan.
 const s=room.wet_zone_schematic||{},wetW=stdNum(s.width)||stdNum(s.wall_segments?.[0]?.length),
  wetD=stdNum(s.depth)||stdNum(s.wall_segments?.[1]?.length),wetH=stdNum(s.wall_segments?.[0]?.tiled_height)||ceiling;
 const placement=wetPlacementFromPlan(room,instance());
 const isSide=placement?.side==='left'||placement?.side==='right';
 const nativeSupport=reconstructed&&placement&&wetW>0?registeredWetSupport(arch,placement,wetW,wetD):null;
 const showWet=Boolean(placement&&wetW>0&&wetD>0&&
  (isSide?wetW<=d+.5&&wetD<=w+.5:wetW<=w+.5&&wetD<=d+.5)&&
  (!reconstructed||nativeSupport));
 const ph2FrontReview=room.id==='PH-BATH2'&&placement?.side==='front'&&Boolean(arch?.selected_tub_proxy);
 if(showWet){
  const tw=Math.min(wetW,isSide?d:w,nativeSupport?.rendered_run_ft??Infinity),
   td=Math.min(wetD,isSide?w:d),th=Math.min(wetH,ceiling);
  // 305A/B: the Nov-07 plan places the selected tub immediately behind
  // SOUTH/front W1. A full opaque 9-ft W1 conceals that tub from the default
  // 3D camera despite a source-compatible fixture fit. In Full Bathroom ONLY,
  // present the front W1 and its returns as a LOW CUTAWAY section. Preserve
  // the source full height in metadata and in the separate Wet Zone Study.
  const reviewHeight=ph2FrontReview?Math.min(th,.72):th;
  const wetSource={source:'LATEST PLAN-TRACED TUB/SHOWER REFERENCE + ORIGINAL SOURCE WET WALL RUN; exact opening offsets UNKNOWN',
   plan_placement:placement.side,plan_fixture_kind:placement.reference_kind,
   classification:placement.confidence,
   native_host_face_id:nativeSupport?.wall_id||null,
   visual_run_trim_ft:nativeSupport?.run_difference_ft||0,
   original_source_run_ft:wetW,
   visible_model_run_ft:tw,
   full_specification_height_ft:th,
   rendered_cutaway_height_ft:reviewHeight,
   cutaway_only_visualization:ph2FrontReview,
   material_quantities_unchanged:true,
   revit_spatial_match:Boolean(nativeSupport),
   source_host_classification:nativeSupport?'WALL FACE NATIVE-DERIVED; wall specification association drawing-inferred':'DRAWING RELATIVE ONLY'};
  let panW,panD,panX,panZ;
  if(isSide){
   const sign=placement.side==='left'?-1:1;
   const edgeX=nativeSupport?nativeSupport.face:sign*w/2,
    zMid=nativeSupport?nativeSupport.center:0,
    x=edgeX-sign*td/2;
   const mat=wallP?tileMaterial(wallP,tw,th,'wall'):neutral.wall;
   addPlane(tw,th,[edgeX-sign*.042,th/2,zMid],[0,Math.PI/2,0],mat,
    'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W1'});
   for(const [idx,z] of [[1,zMid-tw/2],[2,zMid+tw/2]]){
    if(!s.wall_segments?.[idx])continue;
    const run=stdNum(s.wall_segments[idx]?.length);
    if(!(run>0))continue;
    const length=Math.min(td,run);
    const m=wallP?tileMaterial(wallP,length,th,'wall'):neutral.wall;
    addPlane(length,th,[edgeX-sign*length/2,th/2,z],[0,0,0],m,
     'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W'+(idx+1)});
   }
   [panW,panD,panX,panZ]=[td,tw,x,zMid];
  }else{
   const sign=placement.side==='front'?1:-1,
    edgeZ=nativeSupport?nativeSupport.face:sign*d/2,
    xMid=nativeSupport?nativeSupport.center:0;
   const m=wallP?tileMaterial(wallP,tw,reviewHeight,'wall'):neutral.wall;
   addPlane(tw,reviewHeight,[xMid,reviewHeight/2,edgeZ-sign*.042],[0,0,0],m,
    'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W1'});
   for(const [idx,x,rotation] of [[1,xMid-tw/2,Math.PI/2],[2,xMid+tw/2,-Math.PI/2]]){
    if(!s.wall_segments?.[idx])continue;
    const run=stdNum(s.wall_segments[idx]?.length);
    if(!(run>0))continue;
    const length=Math.min(td,run);
    const m=wallP?tileMaterial(wallP,length,reviewHeight,'wall'):neutral.wall;
    addPlane(length,reviewHeight,[x,reviewHeight/2,edgeZ-sign*length/2],[0,rotation,0],m,
     'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W'+(idx+1)});
   }
   [panW,panD,panX,panZ]=[tw,td,xMid,edgeZ-sign*td/2];
  }
  const doPan=room.program?.pan_selected===true;
  if(doPan){
   const panMat=floorP?tileMaterial(floorP,panW,panD,'floor'):neutral.flooring;
   addPlane(panW,panD,[panX,.033,panZ],[-Math.PI/2,0,0],panMat,
    'FULL_ROOM_SELECTED_PAN_SCHEMATIC',floorIndex,
    {...wetSource,selected_pan:true,drain_center:null,slope:null,additional_purchase_area:null});
  }
  const wetEdge=new THREE.LineSegments(
   new THREE.EdgesGeometry(new THREE.PlaneGeometry(panW,panD)),
   new THREE.LineBasicMaterial({color:0xe5ba7e,transparent:true,opacity:.8}));
  wetEdge.position.set(panX,.041,panZ);wetEdge.rotation.x=-Math.PI/2;modelGroup.add(wetEdge);
 }
 if(!showWet&&wallP&&!reconstructed){
  const run=stdNum(s.wall_segments?.[0]?.length);
  if(run>0){
   const width=Math.min(w,run),m=tileMaterial(wallP,width,ceiling,'wall');
   addPlane(width,ceiling,[0,ceiling/2,-d/2+.025],[0,0,0],m,
    'FULL_ROOM_WALL_MATERIAL_STUDY',wallIndex,{source:'Source-selected dry vanity wall finish; position/extent are UNVERIFIED'});
  }
 }
 const sourceCasework=reconstructed?drawRegisteredCasework(arch,room):0;
 if(reconstructed&&arch?.toilet_proxy_anchor){
  const t=arch.toilet_proxy_anchor;
  drawNativeToiletAABBWitness(t.native_family_aabb,instance()?.room_number);
  drawNativeFixtureOffsetWitness(t.local_native_insertion_xz_ft,
   t.illustrative_proxy_center_xz_ft,t.native_plumbing_id,t.receipt_id,
   instance()?.room_number);
 }
 const symbolGate=addRoomPlanSymbols(room,instance(),w,d);
 addMarker();
 const areaConflict=Math.abs((plan.source_floor_area_ft2??plan.display_area_ft2)-plan.display_area_ft2)>.2;
 modeInfo=(reconstructed?
  'REGISTERED REVIT WALL-FACE ARCHITECTURE — '+reconstructed.area.toFixed(2)+
   ' SF visual polygon; wall location/host openings source-native, ROOM NUMBER still drawing-inferred. '+reconstructed.doors+
   ' nominal hosted door leaves, swing/rough opening unknown. ':
  'FULL BATHROOM FLOOR-PLAN ENCLOSURE — '+plan.confidence+'. '+plan.evidence+
   '. Actual wall thickness, door/window opening geometry and Revit room polygon UNVERIFIED.')+
  (showWet?' Frozen wet tiles displayed alongside the '+placement.side.toUpperCase()+
   (ph2FrontReview?' PH-BATH2 south W1/returns LOWERED TO 0.72 FT FOR VISUAL CUTAWAY ONLY; actual full wet-wall height and frozen quantities unchanged.':'')+
   (nativeSupport?' native-derived host wall face (membership drawing-inferred).'+
    (nativeSupport.run_difference_ft>.015?' W1 visual run trimmed '+nativeSupport.run_difference_ft.toFixed(3)+' ft to actual native wall-face segment; FROZEN source W1 dimensions and material pool are unchanged.':'') :
    ' plan-traced tub/shower reference; native spatial location NOT VERIFIED.'):
   (wallP?' Wet wall plane remains UNLOCATED material study pending room-to-fixture source evidence.':''))+
  (areaConflict?' DISPLAY AREA '+plan.display_area_ft2+' SF versus legacy/owner '+plan.source_floor_area_ft2+' SF: RECONCILIATION OPEN.':'')+
  (spec?' Fixture diagrams follow plan pictograms with illustrative model dimensions; exact native family geometry/positions NOT established.':'')+
  ' No unverified niche, shower drain position or glazing fabricated.'+
  (sourceCasework?' '+sourceCasework+' native bounded countertop/vanity proxy(s) replace generic plan-lavatory positions; countertop geometry and basin are schematic, not certified.':'')+
  (symbolGate.suppressed?' '+symbolGate.suppressed+' diagram fixture(s) rendered as 2D UNLOCATED source markers because native boundary/hosted-door overlap made a 3D placement misleading.':'');
 modelInfo.textContent=(reconstructed?'Registered wall-face geometry ':'Drawing-only envelope ')+
  w.toFixed(2)+' × '+d.toFixed(2)+' ft · ceiling '+ceiling.toFixed(2)+
  ' ft · '+(reconstructed?reconstructed.walls+' wall segments / '+reconstructed.doors+' native openings':'entry wall outlined')+
  (arch?.area_conflict_flag?' · DRAWING AREA CONFLICT '+arch.drawing_vs_wall_face_difference_percent.toFixed(1)+'%':'');
}
function buildStudy(room){
 const s=room.wet_zone_schematic,ws=s?.wall_segments||[],width=stdNum(s?.width)||stdNum(ws[0]?.length);
 const depth=stdNum(s?.depth)||stdNum(ws[1]?.length)||null;
 const height=stdNum(s?.ceiling)||stdNum(ws[0]?.height);
 const kind=room.program?.kind;
 const wallP=productFor('wall'),floorP=productFor('floor');
 const wallIndex=productList().indexOf(wallP),floorIndex=productList().indexOf(floorP);
 const actualWidth=width||0;
 if(!height||!actualWidth){
  modeInfo='No source-supported wall dimensions or room footprint. Nothing architectural is synthesized.';
  addMarker();return;
 }
 const d=(depth&&depth>0)?depth:0;
 const makeWalls=(length,height)=>{
  const mat=wallP?tileMaterial(wallP,length,height,'wall'):neutral.missing;
  const pos=[0,height/2,-d/2];
  addPlane(length,height,pos,[0,0,0],mat,'sourceWall',wallIndex,{wall:'W1',dimension_class:ws[0]?.length?.classification||'drawing-derived'});
  outline(length,height,[0,height/2,-d/2+.002],[0,0,0]);
 };
 makeWalls(actualWidth,height);
 if(d>0 && ws.length>1){
  const w2=stdNum(ws[1]?.length)||d;
  const mat=wallP?tileMaterial(wallP,w2,height,'wall'):neutral.missing;
  addPlane(w2,height,[-actualWidth/2,height/2,0],[0,Math.PI/2,0],mat,'sourceWall',wallIndex,{wall:'W2',dimension_class:ws[1].length?.classification});
  outline(w2,height,[-actualWidth/2-.003,height/2,0],[0,Math.PI/2,0]);
 }
 if(d>0 && ws.length>2){
  const w3=stdNum(ws[2]?.length)||d;
  const mat=wallP?tileMaterial(wallP,w3,height,'wall'):neutral.missing;
  addPlane(w3,height,[actualWidth/2,height/2,0],[0,-Math.PI/2,0],mat,'sourceWall',wallIndex,{wall:'W3',dimension_class:ws[2].length?.classification});
  outline(w3,height,[actualWidth/2+.003,height/2,0],[0,-Math.PI/2,0]);
 }
 if(d>0){
  // This is the WET ZONE SOURCE FOOTPRINT, not the complete bathroom floor.
  const doPan=room.program?.pan_selected===true;
  const panelMaterial=doPan&&floorP?tileMaterial(floorP,actualWidth,d,'floor'):neutral.flooring;
  addPlane(actualWidth,d,[0,.006,0],[-Math.PI/2,0,0],panelMaterial,doPan?'dimensionedPan':'sourceFootprint',doPan?floorIndex:-1,
   {width_ft:actualWidth,depth_ft:d,classification:'drawing-derived / assumed; not native Revit polygon',
    selected_pan:doPan,not_full_room_floor:true});
  outline(actualWidth,d,[0,.011,0],[-Math.PI/2,0,0]);
 }
 // The entire bathroom LEVEL slab polygon was NOT returned by the native bridge.
 // A freestanding 2x2-ft sample outside the drawing-derived wet alcove makes
 // every frozen LEVEL choice inspectable without fabricating a room footprint.
 // For PH4 this is the SAME Pienza tile as the one combined LEVEL/PAN pool:
 // a material swatch, NEVER a second area takeoff or purchase.
 if(floorP){
  const sw=2.0,sd=2.0;
  const sx=actualWidth/2+1.75;
  const sz=d>0?d*.12:0;
  addPlane(sw,sd,[sx,.016,sz],[-Math.PI/2,0,0],
   tileMaterial(floorP,sw,sd,'floor'),'UNLOCATED_LEVEL_MATERIAL_SAMPLE',floorIndex,
   {source:'NON_ARCHITECTURAL MATERIAL SAMPLE; not a bathroom slab, takeoff or second PAN',
    area_ft2_for_display_only:4,
    actual_room_floor_outline:null,
    original_material_pool_preserved:true});
  outline(sw,sd,[sx,.022,sz],[-Math.PI/2,0,0],0xe5bb84);
 }
 // TUB bedrooms and undecided bath branches get NO constructed tiled PAN.
 // No niche, glass enclosure, point/linear drain or fixture is placed without an actual BIM location.
 addMarker();
 const desc=kind==='WALK_IN_SELECTED'?'Selected WALK-IN; footprint is 5.0 × 2.54 ft drawing-derived. Drain location / four-plane slope NOT modeled.':
 kind==='DURAVIT_TUB_SELECTED'?'Selected Duravit TUB; dimensions indicate alcove only. Tub family and pan are NOT modeled.':
 kind==='TUB_OR_WALK_IN_UNSELECTED'?'TUB/WALK-IN unselected. No pan or tub geometry invented; floor shown as neutral source footprint.':
 kind==='PRIMARY_WALK_IN_LINEAR'?'Primary wet walls remain neutral; 48-inch factory-solid linear drain location and wet overhead not mapped.':
 kind==='DRY_WOOD'?'Dry vanity WALL only. Existing WOOD floor retained; no room slab dimensions available.':
 'Source wall segment only; no guessed room floor or plumbing fixtures.';
 modeInfo='SOURCE-DIMENSIONED DRAWING STUDY — not a Revit room reconstruction. '+desc+
 (floorP?' The separate bordered 2×2-ft LEVEL tile swatch is UNLOCATED MATERIAL-ONLY, not a second floor/PAN area or purchase.':'');
 modelInfo.textContent='W1 '+actualWidth.toFixed(2)+' ft'+(d>0?' · wet-zone depth '+d.toFixed(2)+' ft':'')+
  ' · '+height.toFixed(2)+' ft height · floor outline unverified';
}
function contextAnchor(inst){
 const side=inst?.unit_side?.value==='B'?'B':'A';
 return [side==='A'?-521:-545,228,inst?.level?.elevation_ft||0];
}
function renderAABB(item,anchor,mat,cat){
 const b=item.bounds;if(!b?.min||!b?.max)return null;
 const raw=[b.max[0]-b.min[0],b.max[2]-b.min[2],b.max[1]-b.min[1]];
 if(raw.some(x=>!Number.isFinite(x))||raw.some(x=>x<0)||Math.max(...raw)>80)return null;
 const dim=raw.map(x=>Math.max(.017,x));
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(...dim),mat);
 mesh.position.set((b.max[0]+b.min[0])/2-anchor[0],(b.max[2]+b.min[2])/2-anchor[2],(b.max[1]+b.min[1])/2-anchor[1]);
 mesh.userData={category:'revit_'+cat,surfaceIndex:-1,revit_id:item.id,receipt_id:item.receipt_id,
  room_association:'NOT_VERIFIED',family_name:item.name,host_id:item.host_id,
  bounds_ft:b,location:item.location,
  dimensions_ft:raw.map(x=>+x.toFixed(4)),
  source:'real native Revit axis-aligned bounds, not solid'};
 // Native AABBs are analytical proxies, not modeled opaque wall/fixture solids.
 mesh.receiveShadow=false;mesh.castShadow=false;
 modelGroup.add(mesh);renderObjects.push(mesh);
 if(state.edges){
  const e=new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry),
    new THREE.LineBasicMaterial({color:0x829dad,transparent:true,opacity:.65}));
  mesh.add(e);
 }
 return mesh;
}
function renderNativeInsertion(item,anchor,cat){
 // Geometry here is an ACTUAL read-only Revit LocationPoint (and rotation);
 // the small arrow is a locator symbol, emphatically NOT the fixture family.
 const p=item.location?.point,b=item.bounds,theta=item.location?.rotation_radians;
 if(!Array.isArray(p)||p.length!==3||!p.every(Number.isFinite)||!b?.min||!b?.max)return null;
 // Revit returns a meaningless [0,0,0] location for some non-point elements.
 // Only advertise an insertion when it lies at/near that element's real bounds.
 if(p.some((v,i)=>v<b.min[i]-.65||v>b.max[i]+.65))return null;
 const pos=new THREE.Vector3(p[0]-anchor[0],p[2]-anchor[2]+.15,p[1]-anchor[1]);
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0],3));
 const marker=new THREE.Points(g,insertionMaterial);
 marker.position.copy(pos);marker.renderOrder=12;marker.visible=state.insertions;
 marker.userData={category:'REVIT_INSERTION_POINT',surfaceIndex:-1,
  revit_id:item.id,receipt_id:item.receipt_id,host_id:item.host_id,
  family_name:item.name,location:item.location,bounds_ft:b,
  room_association:'UNVERIFIED',symbol:'DISPLAY-ONLY, 0.15 ft elevation offset, NOT A FIXTURE SOLID'};
 if(Number.isFinite(theta)){
  const dx=Math.cos(theta),dz=Math.sin(theta),len=.68,tip=.18,wing=.12;
  const v=[
   0,0,0, len*dx,0,len*dz,
   len*dx,0,len*dz, len*dx-tip*dx+wing*(-dz),0,len*dz-tip*dz+wing*dx,
   len*dx,0,len*dz, len*dx-tip*dx-wing*(-dz),0,len*dz-tip*dz-wing*dx
  ];
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(v,3));
  const line=new THREE.LineSegments(geo,new THREE.LineBasicMaterial({color:0xf1c477,depthTest:false}));
  marker.add(line);
 }
 modelGroup.add(marker);renderObjects.push(marker);
 return marker;
}
function buildContext(room,inst){
 const ctx=inst?.unit_context;
 if(!ctx){modeInfo='No native model evidence for the selected physical instance.';return;}
 const anchor=contextAnchor(inst),counts={},insertions={};
 const choices={
  walls:neutral.modelWall,doors:neutral.contextualDoor,
  windows:neutral.contextWindow,plumbing:neutral.porcelain,
  casework:neutral.contextualCase,floors:neutral.contextFloor,
  ceilings:neutral.contextFloor
 };
 for(const cat of ['floors','walls','doors','windows','casework','plumbing']){
  let count=0,points=0;for(const o of ctx[cat]||[]){
   const m=renderAABB(o,anchor,choices[cat],cat);
   if(m){m.visible=cat!=='walls'||state.walls;count++;}
   if(['plumbing','casework'].includes(cat)&&renderNativeInsertion(o,anchor,cat))points++;
  }counts[cat]=count;
  insertions[cat]=points;
 }
 addMarker(0x425e74);
 modeInfo='READ-ONLY REVIT LEVEL CONTEXT: actual native element bounds ('+
 Object.entries(counts).map(([k,n])=>k+' '+n).join(' · ')+
 '). Native fixture/casework insertion markers: '+Object.values(insertions).reduce((a,b)=>a+b,0)+
 ' actual source points/rotations where valid. Room assignment unverified; markers are not fixture solids and NO tile is painted on unidentified Revit walls.';
 modelInfo.textContent=(inst?.room_number||room.id)+' · '+(inst?.level?.name||'UNKNOWN LEVEL')+
 ' · elevation '+Number(inst?.level?.elevation_ft).toFixed(2)+' ft · Level receipt '+(inst?.level?.receipt_id||'N/A');
}
function physicalBounds(){
 const b=new THREE.Box3();let hit=0;
 for(const o of renderObjects){if(!o.visible)continue;b.expandByObject(o);hit++;}
 return hit?b:null;
}
function sourceHostedDoorSightline(inst){
 // Door INSERTION and host wall-face line are read-only Revit evidence.
 // The viewer lens/eye-height, inward offset and look target are chosen for
 // visual study ONLY: never an architectural clear width, safety/ADA or swing.
 const arch=inst?.architecture,poly=arch?.floor_polygon_local_xz_ft;
 if(!poly?.length||!arch?.wall_segments?.length)return null;
 const signed=poly.reduce((sum,p,i)=>{
  const q=poly[(i+1)%poly.length];return sum+p[0]*q[1]-q[0]*p[1];
 },0);
 const outward=signed>=0?-1:1;
 const doorUsage=new Map();
 for(const r of ROOMS)for(const physical of r.physical_instances||[]){
  for(const o of physical.architecture?.openings||[]){
   if(o.kind==='door')doorUsage.set(o.id,(doorUsage.get(o.id)||0)+1);
  }
 }
 const candidates=[];
 for(const door of arch.openings||[]){
  if(door.kind!=='door'||!Array.isArray(door.location_local_ft)||!(door.nominal_width_ft>1.5))continue;
  const wall=arch.wall_segments.find(s=>s.id===door.host_id);
  if(!wall)continue;
  const a=wall.start_local_ft,b=wall.end_local_ft;
  const dx=b[0]-a[0],dz=b[1]-a[1],len=Math.hypot(dx,dz);
  if(len<.3)continue;
  const nx=dz/len*outward,nz=-dx/len*outward;
  const p=door.location_local_ft;
  for(const offset of [.9,1.15]){
   const eyeX=p[0]+nx*offset,eyeZ=p[1]+nz*offset;
   if(!diagramPointWithinPolygon(eyeX,eyeZ,poly))continue;
   const lookDistance=[4,3.5,2.8,2.1,1.4].find(distance=>
    distance>offset+.45&&diagramPointWithinPolygon(p[0]+nx*distance,p[1]+nz*distance,poly));
   if(!lookDistance)continue;
   candidates.push({door,wall,offset,eyeX,eyeZ,
    targetX:p[0]+nx*lookDistance,targetZ:p[1]+nz*lookDistance,
    lookDistance,sharedCompartmentDoor:(doorUsage.get(door.id)||0)>1});
   break;
  }
 }
 // Prefer an unshared hosted opening rather than an adjoining WC connector
 // when the same native door occurs in two inferred room envelopes.
 candidates.sort((a,b)=>Number(a.sharedCompartmentDoor)-Number(b.sharedCompartmentDoor)||
  b.lookDistance-a.lookDistance);
 return candidates[0]||null;
}
function setCamera(preset,force=true){
 state.preset=preset;
 cameraEvidence=null;cameraStatus.hidden=true;
 const b=physicalBounds(),center=b?b.getCenter(new THREE.Vector3()):new THREE.Vector3(0,4,0);
 const ext=b?b.getSize(new THREE.Vector3()):new THREE.Vector3(8,8,8);
 // PH4 includes a distinct 310 context compartment behind 311. Frame the
 // selected 311 bathroom from its actual inner-side entrance, not from the
 // outside of its shower wall; keep the separate 310 visible on orbit.
 const ph4Focus=state.mode==='full'&&state.room==='PH-BATH4';
 if(ph4Focus){center.set(0,3.4,-.55);ext.set(6.2,9.25,6.2);}
 if(preset==='interior'&&state.mode==='full'){
  const sourceView=sourceHostedDoorSightline(instance());
  if(sourceView){
   const {door,wall,eyeX,eyeZ,offset,sharedCompartmentDoor}=sourceView;
   // Camera stays OUTSIDE the inferred envelope, elevated to reveal complete
   // bathrooms. Door/host provide a source orientation, not an actual user's
   // eye position, walk path or accessible/installation clearance.
   const doorX=door.location_local_ft[0],doorZ=door.location_local_ft[1];
   const inwardX=(eyeX-doorX)/offset,inwardZ=(eyeZ-doorZ)/offset;
   const distance=Math.max(9.5,Math.min(17,ext.length()*1.13));
   const eyeXOutside=doorX-inwardX*distance,eyeZOutside=doorZ-inwardZ*distance;
   const poly=instance()?.architecture?.floor_polygon_local_xz_ft||[];
   const centerX=poly.length?poly.reduce((v,p)=>v+p[0],0)/poly.length:0;
   const centerZ=poly.length?poly.reduce((v,p)=>v+p[1],0)/poly.length:0;
   const eyeHeight=Math.max(12.0,ext.y*1.42),targetHeight=2.8;
   cameraEvidence={category:'CAMERA_HOSTED_DOOR_ALIGNED_EXTERIOR_CUTAWAY',
    revit_id:door.id,host_id:wall.id,receipt_id:door.receipt_id,
    host_wall_receipt_id:wall.receipt_id,
    nominal_width_ft:door.nominal_width_ft,
    native_door_insertion_local_xz_ft:door.location_local_ft,
    source_inward_probe_ft:offset,visual_eye_height_ft:eyeHeight,
    eye_local_xyz_ft:[eyeXOutside,eyeHeight,eyeZ],
    target_local_xyz_ft:[centerX,targetHeight,centerZ],
    shared_compartment_connector:sharedCompartmentDoor,
    not_verified_main_entry:true,not_construction_clearance:true,
    not_an_interior_eye:true,visual_cutaway_only:true,
    room_assignment:'DRAWING-INFERRED; NOT NATIVE OST_Rooms',
    source:'REAL source-hosted door insertion and wall normal orient a VISUAL elevated EXTERIOR cutaway; camera distance/elevation and look center are chosen by viewer, NOT native person eye, entrance certification or construction data'};
   cameraStatus.textContent='Hosted door #'+door.id+' / wall #'+wall.id+
    (sharedCompartmentDoor?' · shared WC/primary connector, NOT verified main entry':' · main entry role NOT verified')+
    ' · elevated EXTERIOR cutaway aligned to door host; NOT an actual entry/standing viewpoint. Room association drawing-inferred.';
   cameraStatus.hidden=false;
   camera.fov=52;
   orbit.target.set(centerX,targetHeight,centerZ);
   camera.position.set(eyeXOutside,eyeHeight,eyeZOutside);camera.up.set(0,1,0);
   camera.near=.018;camera.far=1100;camera.updateProjectionMatrix();
   orbit.update();if(force)renderer.render(scene,camera);
   return;
  }
  const arch=instance()?.architecture;
  const footprint=arch?.floor_polygon_local_xz_ft;
  const pts=footprint?.length?footprint:null;
  let focus=new THREE.Vector3(0,3.05,0);
  if(pts){
   focus.set(pts.reduce((s,p)=>s+p[0],0)/pts.length,3.05,
    pts.reduce((s,p)=>s+p[1],0)/pts.length);
  }
  // Reviewer96 FIX: a true 1st-person viewpoint immersed in a zero-thickness
  // wet tile plane produced an opaque wall and unreadable overlay. This preset
  // intentionally uses a CLOSE EXTERIOR CUTAWAY, not a certified standing/
  // doorway camera point. Real wall cutaway is already in native geometry.
  const wetHand=instance()?.plan_shower_side;
  const side=ph4Focus&&wetHand==='left'?-1:1;
  // Back the cutaway camera outside the whole envelope far enough that its
  // near wall does not fill/bleach the full interactive canvas.
  const eye=new THREE.Vector3(focus.x+side*Math.max(10.8,ext.x*1.65),
   Math.max(14.5,ext.y*1.52),focus.z+Math.max(11.8,ext.z*1.65));
  cameraEvidence={category:'CAMERA_EXTERIOR_CUTAWAY_FALLBACK',
   source:'No defensible native hosted door eye/location inside drawing-inferred room face. External cutaway is DISPLAY ONLY, not a source view'};
  cameraStatus.textContent='Exterior cutaway fallback — no source-compatible interior doorway sightline, eye/location not certified.';
  cameraStatus.hidden=false;
  camera.fov=55;
  orbit.target.copy(focus);
  camera.position.copy(eye);camera.up.set(0,1,0);
  camera.near=.023;camera.far=1100;camera.updateProjectionMatrix();
  orbit.update();if(force)renderer.render(scene,camera);
  return;
 }
 camera.fov=48;
 // Fit the entire tall 9'-3" wall set BELOW the scene overlays, rather than
 // filling and clipping the upper viewport like the original contextual preview.
 // Source context spans a whole building wing; the old 85-ft distance cap
 // clipped its outer actual bounds. Fit the full source AABB diagonal to the
 // camera's real vertical FOV, without changing a single Revit coordinate.
 const R=state.mode!=='context'
  ?Math.max(7.8,Math.min(45,ext.length()*(state.mode==='full'?1.56:1.48)))
  :Math.max(75,Math.min(350,ext.length()/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2)))*1.25));
 const entrySide=instance()?.plan_entry_side;
 const innerX=(ph4Focus&&entrySide==='left')?-1:1;
 const u=(preset==='front')?new THREE.Vector3(.1,.10,1):
  (preset==='top')?new THREE.Vector3(.01,1,.012):
  (preset==='side')?new THREE.Vector3(1,.13,.1):
  state.mode==='full'?new THREE.Vector3(innerX*.74,1.14,1.0):new THREE.Vector3(.80,.55,1.0);
 u.normalize().multiplyScalar(R);
 orbit.target.copy(center);
 camera.position.copy(center).add(u);
 camera.up.set(0,1,0);
 camera.near=Math.max(.015,R/1000);camera.far=1100;camera.updateProjectionMatrix();
 orbit.update();
 if(force)renderer.render(scene,camera);
}
function updateRoomList(){
 const list=document.getElementById('room-list');list.innerHTML='';
 for(const room of ROOMS){
  const b=document.createElement('button');b.type='button';b.className='room-btn'+(room.id===state.room?' active':'');
  b.setAttribute('aria-pressed',String(room.id===state.room));
  const d=document.createElement('span');d.className='room-dot'+(room.has_pick?'':' empty');
  const text=document.createElement('span');text.className='room-text';
  const a=document.createElement('div');a.className='room-code';a.textContent=room.id;
  const meta=document.createElement('div');meta.className='room-meta';
  meta.textContent=room.has_pick?'Frozen provisional tiles':'No tile pick yet';
  text.append(a,meta);b.append(d,text);b.onclick=()=>selectRoom(room.id);
  list.append(b);
 }
}
function updateMaterials(){
 const list=document.getElementById('surfaces');list.innerHTML='';
 const p=productList(),r=current();
 if(!p.length){const t=document.createElement('div');t.className='muted';t.style.cssText='padding:14px;margin-top:10px;border:1px solid #596879;background:#26333e;border-radius:6px';t.textContent='NO PICK YET. Selected surfaces remain neutral. No owner tile approval.';list.append(t);}
 else p.forEach((prod,index)=>{
  const b=document.createElement('button');b.className='surface';b.type='button';b.dataset.index=String(index);
  const row=document.createElement('div');row.className='surface-row';
  const image=document.createElement('img');image.className='swatch';image.loading='lazy';
  if(prod.image)image.src=prod.image;else image.alt='No maker photo';
  const t=document.createElement('div');
  const h=document.createElement('div');h.className='surface-name';h.textContent=prod.surface;
  const s=document.createElement('div');s.className='surface-sub';
  s.textContent=prod.name+(/niche/i.test(prod.surface)?' · location unknown':'');
  t.append(h,s);row.append(image,t);b.append(row);b.onclick=()=>selectMaterial(index);
  list.append(b);
 });
 const alt=document.getElementById('alternative');alt.disabled=!r.alternative;alt.checked=state.alt&&!!r.alternative;
 document.getElementById('alternative-label').textContent=r.alternative?(state.alt?'Unselected preview':'Compare unselected'):'Not available';
 document.getElementById('spec-title').textContent=r.id+' · '+(state.alt?'Historic unselected alternative':r.has_pick?'Frozen current picks':'No pick yet');
 document.getElementById('material-info').hidden=true;
 if(state.surface>=p.length)state.surface=-1;
 if(state.surface>=0)selectMaterial(state.surface);
}
function productVendor(p){
 let domain='';try{domain=new URL(p?.url||'').hostname.toLowerCase().replace(/^www\./,'');}catch(e){}
 return ({'flooranddecor.com':'Floor & Decor','elmsurfaces.com':'Elm Surfaces','msisurfaces.com':'MSI Surfaces','porcelanosa-usa.com':'Porcelanosa'})[domain]||domain||'Not stated';
}
function selectMaterial(index){
 state.surface=index;
 const p=productList()[index],node=document.getElementById('material-info');
 document.querySelectorAll('.surface').forEach((x,i)=>x.classList.toggle('selected',i===index));
 for(const o of renderObjects){
  if(o.material?.emissive){o.material.emissive.set((o.userData.surfaceIndex===index)?0x3a2717:0x000000);o.material.emissiveIntensity=.25;}
 }
 if(!p){node.hidden=true;return}
 node.hidden=false;
 node.innerHTML='<b>'+htmlEscape(p.name)+'</b><div>'+htmlEscape(p.surface)+'</div>'+
  '<div>Vendor: '+htmlEscape(productVendor(p))+'</div>'+
  '<div>Size: '+htmlEscape(p.size)+'</div><div>Source price: '+htmlEscape(p.price)+'</div>'+
  '<div>Selection status: '+(state.alt?'HISTORIC UNSELECTED PREVIEW':'FROZEN PROVISIONAL, NOT OWNER-APPROVED')+'</div>'+
  '<div>Source: '+htmlEscape(p.source||current()?.alternative?.provenance||'Archived frozen owner review')+'</div>'+
  '<div>'+(/niche/i.test(p.surface)?'Niche dimension/location NOT in Revit read result; no niche mesh or cutout fabricated.':'Rendered material is a nominal-sized study, not a verified per-face BIM material.')+'</div>'+
  (p.image?.includes('sandstone')?'<div><b>Image caveat:</b> Sandstone/Copper mixed maker installation, not exact Sandstone-only appearance.</div>':'')+
  '<div>Grout shown as unselected illustrative 1/16-inch, vertical wall layout default. Vendor images are not physical samples.</div>'+
  '<a href="'+htmlEscape(p.url)+'" target="_blank" rel="noopener noreferrer">Official product page ↗</a>';
}
function showNativeElement(x){
 selectedRevit.hidden=false;selectedRevit.open=true;
 const p=x.location?.point,b=x.bounds_ft;
 const point=Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)?
  p.map(v=>v.toFixed(3)).join(', ')+' ft (native X,Y,Z)':'not returned';
 const rotation=Number.isFinite(x.location?.rotation_radians)?
  (x.location.rotation_radians*180/Math.PI).toFixed(2)+'°':'not returned';
 const range=b?.min&&b?.max?
  b.min.map(v=>Number(v).toFixed(3)).join(', ')+' → '+b.max.map(v=>Number(v).toFixed(3)).join(', ')+' ft':'not returned';
 const wallEnds=x.native_location?.start&&x.native_location?.end?
  x.native_location.start.map(v=>Number(v).toFixed(4)).join(', ')+' → '+
  x.native_location.end.map(v=>Number(v).toFixed(4)).join(', ')+' ft':'not available';
 document.getElementById('viewer-v2-element-detail').innerHTML=
  '<div><strong>ID:</strong> '+htmlEscape(x.revit_id)+' · '+htmlEscape(x.family_name||x.category)+'</div>'+
  '<div><strong>Revit native bounds:</strong> '+htmlEscape(range)+'</div>'+
  '<div><strong>Revit wall centerline endpoints:</strong> '+htmlEscape(wallEnds)+'</div>'+
  '<div><strong>Derived wall thickness:</strong> '+htmlEscape(x.thickness_ft??'not available')+' ft</div>'+
  '<div><strong>Insertion location:</strong> '+htmlEscape(point)+'</div>'+
  '<div><strong>Native rotation:</strong> '+htmlEscape(rotation)+'</div>'+
  '<div><strong>Host element:</strong> '+htmlEscape(x.host_id??'not returned')+'</div>'+
  '<div><strong>Read-only receipt:</strong> '+htmlEscape(x.receipt_id||'missing')+'</div>'+
  '<div><strong>Spatial room association:</strong> UNVERIFIED. Bounding boxes and native location markers are not family solids or room boundaries.</div>';
 modelInfo.textContent='Revit '+x.revit_id+' · '+(x.family_name||x.category)+' · room match UNVERIFIED';
}
const wallCats=new Set(['sourceWall','revit_walls','FULL_ROOM_BOUNDARY','FULL_ROOM_WET_WALL',
 'FULL_ROOM_WALL_MATERIAL_STUDY','DRAWING_FULL_ROOM_PERIMETER',
 'DRAWING_FULL_ROOM_PARTIAL_ENTRY_WALL','DRAWING_ADJACENT_BOUNDARY','ARCH_REGISTERED_WALL',
 'ARCH_HOSTED_DOOR_LEAF','ARCH_HOSTED_WINDOW']);
function applyWallVisibility(){
 for(const o of renderObjects){
  if(wallCats.has(o.userData.category))o.visible=state.walls;
 }
 document.getElementById('toggle-walls').textContent=state.walls?'Hide walls':'Show walls';
 document.getElementById('toggle-walls').setAttribute('aria-pressed',String(state.walls));
}
function showPlanSymbol(x){
 selectedRevit.hidden=false;selectedRevit.open=true;
 document.getElementById('viewer-v2-element-detail').innerHTML=
  '<div><strong>Architectural plan fixture:</strong> '+htmlEscape(x.kind)+'</div>'+
  '<div><strong>Room label:</strong> '+htmlEscape(x.room_number||instance()?.room_number||'unverified')+'</div>'+
  '<div><strong>Reference:</strong> A2.1 / A2.2, owner-uploaded November 7, 2026 floor-plan export</div>'+
  '<div><strong>Spatial basis:</strong> drawing-traced fixture diagram. Relative position is approximate.</div>'+
  (x.fixture_model?'<div><strong>Frozen selected nominal model:</strong> '+htmlEscape(x.fixture_model)+
   '; source row '+htmlEscape(x.source_row_id)+
   '; overall rendering footprint '+htmlEscape(x.fixture_dimensions)+' ft (NOT verified installation solid or tolerances)</div>'+
   '<div><strong>Native wall-face calibration displacement:</strong> '+
   htmlEscape(x.drawing_calibration_delta_ft)+' ft from drawing symbol, no native tub insertion established.</div>':'')+
  (x.native_anchor_id?'<div><strong>Native plumbing source ID:</strong> '+htmlEscape(x.native_anchor_id)+
   ' · read-only receipt '+htmlEscape(x.native_anchor_receipt_id)+
   '</div><div><strong>Native insertion ft:</strong> '+htmlEscape(x.native_anchor_coordinate_ft)+
   '</div><div><strong>3D proxy projected:</strong> '+htmlEscape(x.illustrative_offset_from_anchor_ft)+
   ' ft inward, illustrative ONLY, not actual fixture center or rough-in.</div>':'')+
  '<div><strong>Fixture identification:</strong> NOT a native Revit family; NO confirmed SKU, exact dimensions, rough-in, clearance or installation coordinate.</div>'+
  (/reference/.test(x.kind)?'<div><strong>Program:</strong> The drawing pictogram DOES NOT select the undecided tub/walk-in branch.</div>':'');
 modelInfo.textContent='Architectural drawing '+x.kind+' diagram · source-relative placement only';
}
function rebuild(){
 const room=current(),inst=instance();
 if(!room)return;
 const revision=++rebuildRevision;
 document.body.dataset.viewerMaterials='LOADING';
 clearGeometry();updateViewConstraints(state.mode);selectedRevit.hidden=true;selectedRevit.open=false;
 modelInfo.textContent='';
 if(state.mode==='full')buildFullRoom(room);
 else if(state.mode==='study')buildStudy(room);
 else buildContext(room,inst);
 document.getElementById('room-title').textContent=room.id+' · '+(room.title||room.id);
 const nr=inst?.room_number||room.id;
 document.body.dataset.viewerRoom=room.id;
 document.body.dataset.viewerInstance=nr;
 document.body.dataset.viewerMode=state.mode;
 const registered=inst?.architecture;
 document.getElementById('room-description').textContent=
  nr+' / '+(inst?.level?.name||'level unknown')+' (native elevation; room-number mapping inferred). '+
  (state.mode==='full'?(registered?'Architecture from read-only native wall curves and hosted openings; room ID drawing-inferred, not certified Revit room.':
    'Entire bathroom envelope reconstructed from floor-plan study, approximate and NOT a measured Revit room.'):
   state.mode==='study'?'Dimensioned wet-zone-only surface study, not BIM-native room solids.':
   'Read-only level-context bounding geometry, not bathroom-specific walls.');
 document.getElementById('confidence').textContent=state.mode==='full'?(registered?'Native wall lines / inferred room':'Full room / drawing study'):
  state.mode==='study'?'Wet-zone / unlocated':'Revit bounds / unassigned';
 document.getElementById('model-count').textContent=renderObjects.length+
  ' physical study/model objects · '+nr+' · '+(room.program?.kind||'program unverified');
 const alert=document.querySelector('.alert');
 alert.textContent=state.mode==='full'?(registered?'FULL BATHROOM · NATIVE WALL-FACE STUDY':'FULL BATHROOM · PLAN-STUDY GEOMETRY'):
  state.mode==='study'?'WET-ZONE DETAIL · NOT VERIFIED':'REVIT BOUNDS · ROOM UNVERIFIED';
 const programs=room.program||{};
 programLabel.innerHTML='<strong>Selected program:</strong> '+htmlEscape(programs.plumbing_truth||'Not mapped')+
  '<div><strong>Scope:</strong> '+htmlEscape(programs.scope_truth||'Unknown')+'</div>'+
  '<div>Two physical rooms represented separately. No native fixture-to-room mapping verified. Owner approvals: ZERO.</div>';
 const s=room.wet_zone_schematic||{};
 const w=s.wall_segments||[];
 const claims=w.map(x=>htmlEscape(x.id)+' '+htmlEscape(x.length?.value??'unknown')+' ft ('+
      htmlEscape(x.length?.classification||'unclassified')+')').join('; ')||'None';
 const missing=inst?.missing||['Room geometry not mapped'];
 document.getElementById('viewer-evidence-content').innerHTML=
  '<div><strong>Instance:</strong> '+htmlEscape(inst?.room_number||'unknown')+'</div>'+
  '<div><strong>Native Revit level:</strong> '+htmlEscape(inst?.level?.name||'unknown')+
  ', '+htmlEscape(inst?.level?.elevation_ft?.toFixed(3)||'unknown')+
  ' ft; source receipt '+htmlEscape(inst?.level?.receipt_id||'missing')+'</div>'+
  '<div><strong>Spatial match:</strong> '+(registered?'DRAWING-REGISTERED to native wall-face polygon; room membership not a native Room ID':'UNVERIFIED (room number inferred)')+'</div>'+
  (registered?'<div><strong>Native wall receipt:</strong> '+htmlEscape(registered.wall_receipt_id)+
   '</div><div><strong>Native wall IDs:</strong> '+htmlEscape(registered.native_wall_ids?.join(', '))+
   '</div><div><strong>Visual face area:</strong> '+htmlEscape(registered.floor_polygon_area_ft2)+
   ' SF (NOT quantity or owner-approved room measurement)</div>'+
   (registered.area_conflict_flag?'<div><strong>AREA CONFLICT:</strong> Drawing '+htmlEscape(registered.drawing_display_area_ft2)+
    ' SF versus wall-face '+htmlEscape(registered.floor_polygon_area_ft2)+' SF ('+
    htmlEscape(registered.drawing_vs_wall_face_difference_percent)+'%). UNRESOLVED; no procurement adjustment.</div>':'')+
   '<div><strong>Hosted opening IDs:</strong> '+htmlEscape((registered.openings||[]).map(x=>x.id+' host '+x.host_id).join(', ')||'None on documented wall faces')+'</div>':'')+
  (registered?.toilet_proxy_anchor?'<div><strong>WC plumbing insertion anchor:</strong> '+htmlEscape(registered.toilet_proxy_anchor.native_plumbing_id)+
   '; proxy projection '+htmlEscape(registered.toilet_proxy_anchor.offset_from_native_insertion_ft)+
   ' ft is illustrative, not certified plumbing placement.</div>':'')+
  (registered?.native_ceiling_evidence?'<div><strong>Native GWB ceiling underside:</strong> '+htmlEscape(registered.native_ceiling_evidence.underside_height_ft)+
   ' ft above level · element '+htmlEscape(registered.native_ceiling_evidence.id)+
   ' · receipt '+htmlEscape(registered.native_ceiling_evidence.receipt_id)+
   '; room ceiling outline still drawing-inferred and 9.25ft drawn height not overwritten.</div>':'')+
  '<div><strong>Source drawing walls:</strong> '+claims+'</div>'+
  '<div><strong>Missing:</strong><ul style="padding-left:16px;margin:4px 0">'+
  missing.map(x=>'<li>'+htmlEscape(x)+'</li>').join('')+'</ul></div>';
 fidelity.textContent=modeInfo;
 document.getElementById('viewer-mode-full').setAttribute('aria-pressed',String(state.mode==='full'));
 document.getElementById('viewer-mode-study').setAttribute('aria-pressed',String(state.mode==='study'));
 document.getElementById('viewer-mode-context').setAttribute('aria-pressed',String(state.mode==='context'));
 const inserts=document.getElementById('viewer-insertions');
 inserts.hidden=state.mode!=='context';
 inserts.setAttribute('aria-pressed',String(state.insertions));
 inserts.textContent='Native insertions '+(state.insertions?'ON':'OFF');
 applyWallVisibility();updateMaterials();setCamera(state.preset);
 history.replaceState(null,'','#'+encodeURIComponent(room.id)+'/'+encodeURIComponent(inst?.room_number||'A'));
 // GPU material stabilization for rapid 26-instance navigation: maker-image
 // blends are asynchronous. The procedural tile map must remain usable
 // immediately, and after maker assets arrive every active map is explicitly
 // uploaded/rendered before the browser marks the scene capture-ready.
 const tiled=renderObjects.filter(o=>o.material?.userData?.atlas);
 const atlases=[...new Set(tiled.map(o=>o.material.userData.atlas))];
 Promise.all(atlases.map(a=>a.ready)).then(async()=>{
  if(revision!==rebuildRevision)return;
  try{
   for(const o of tiled){
    if(!o.parent||!o.material)return;
    const map=o.material.map,normal=o.material.normalMap;
    if(map){map.needsUpdate=true;renderer.initTexture?.(map);}
    if(normal){normal.needsUpdate=true;renderer.initTexture?.(normal);}
   }
   renderer.compile(scene,camera);
   renderer.render(scene,camera);
   renderer.getContext().finish();
   // A synchronous GPU upload is not sufficient on all SwiftShader/Chrome
   // builds: the texture program settles over subsequent rendered frames.
   // Explicitly gate READY on a second render after a short real browser hold.
   await new Promise(resolve=>setTimeout(resolve,560));
   if(revision!==rebuildRevision)return;
   renderer.render(scene,camera);
   renderer.getContext().finish();
   if(revision===rebuildRevision)document.body.dataset.viewerMaterials='READY';
  }catch(error){
   runtimeErrors.push('MATERIAL_REFRESH: '+String(error));
   if(revision===rebuildRevision)document.body.dataset.viewerMaterials='ERROR';
  }
 });
}
function parseInstanceAddress(hash){
 let parts;try{parts=decodeURIComponent(String(hash||'').replace(/^#/, '')).split('/');}catch(e){return null;}
 const r=ROOMS.find(x=>x.id===parts[0]);if(!r)return null;
 const index=r.physical_instances?.findIndex(x=>String(x.room_number).toUpperCase()===String(parts[1]||'').toUpperCase())??-1;
 return {room:r.id,instance:index>=0?index:0};
}
function loadInstanceAddress(hash){
 const address=parseInstanceAddress(hash);if(!address)return false;
 state.room=address.room;state.instance=address.instance;state.surface=-1;state.alt=false;
 state.mode='full';state.preset='isometric';
 updateRoomList();updateInstanceSelect();rebuild();
 return true;
}
function selectRoom(id){
 const r=ROOMS.find(x=>x.id===id);if(!r)return;
 state.room=id;state.instance=0;state.alt=false;state.surface=-1;
 state.mode='full';
 state.preset='isometric';
 updateRoomList();updateInstanceSelect();rebuild();
}
function updateInstanceSelect(){
 const e=document.getElementById('viewer-instance');e.innerHTML='';
 current()?.physical_instances?.forEach((inst,i)=>{
  const o=document.createElement('option');o.value=String(i);
  o.textContent='Instance '+inst.room_number+' ('+(inst.unit_side?.value||'?')+')';
  e.append(o);
 });e.value=String(state.instance);
}
function setMode(mode){
 if(mode!=='study'&&mode!=='context'&&mode!=='full')return;
 state.mode=mode;state.surface=-1;state.preset='isometric';rebuild();
}
function resize(){
 const w=Math.max(200,stage.clientWidth),h=Math.max(200,stage.clientHeight);
 renderer.setSize(w,h,false);
 camera.aspect=w/h;camera.updateProjectionMatrix();
}
const ro=new ResizeObserver(resize);ro.observe(stage);resize();
document.getElementById('viewer-instance').addEventListener('change',e=>{
 state.instance=Math.max(0,Math.min(1,+e.target.value||0));state.surface=-1;rebuild();
});
document.getElementById('viewer-mode-study').onclick=()=>setMode('study');
document.getElementById('viewer-mode-full').onclick=()=>setMode('full');
document.getElementById('viewer-mode-context').onclick=()=>setMode('context');
document.getElementById('viewer-insertions').onclick=()=>{
 state.insertions=!state.insertions;
 for(const o of renderObjects)if(o.userData.category==='REVIT_INSERTION_POINT')o.visible=state.insertions;
 const e=document.getElementById('viewer-insertions');
 e.textContent='Native insertions '+(state.insertions?'ON':'OFF');
 e.setAttribute('aria-pressed',String(state.insertions));
};
document.getElementById('viewer-camera-iso').onclick=()=>setCamera('isometric');
document.getElementById('viewer-camera-inside').onclick=()=>setCamera('interior');
document.getElementById('viewer-camera-front').onclick=()=>setCamera('front');
document.getElementById('viewer-camera-top').onclick=()=>setCamera('top');
document.getElementById('reset').onclick=()=>setCamera('isometric');
document.getElementById('toggle-walls').onclick=()=>{
 state.walls=!state.walls;
 applyWallVisibility();
};
document.getElementById('toggle-bounds').onclick=()=>{
 state.edges=!state.edges;document.getElementById('toggle-bounds').textContent=state.edges?'Hide edges':'Show edges';rebuild();
};
document.getElementById('alternative').onchange=e=>{
 if(!current().alternative){e.target.checked=false;return}
 state.alt=!!e.target.checked;state.surface=-1;rebuild();
};
document.getElementById('open-accuracy').onclick=()=>window.open('ACCURACY.md','_blank');
document.getElementById('copy-room').onclick=()=>navigator.clipboard?.writeText(current()?.physical_instances?.[state.instance]?.room_number||state.room);
const copyInstance=document.createElement('button');
copyInstance.type='button';copyInstance.id='viewer-copy-instance';copyInstance.textContent='Copy instance link';
document.getElementById('copy-room').after(copyInstance);
copyInstance.onclick=async()=>{
 try{if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');await navigator.clipboard.writeText(location.href);copyInstance.textContent='Link copied';}
 catch(e){copyInstance.textContent='Use address bar to copy';}
};
canvas.addEventListener('dblclick',()=>setCamera('isometric'));
function pickableObjects(){return renderObjects.filter(o=>o.visible&&o.parent?.visible!==false);}
canvas.addEventListener('click',e=>{
 const rect=canvas.getBoundingClientRect();
 mouse.x=2*(e.clientX-rect.left)/rect.width-1;
 mouse.y=-2*(e.clientY-rect.top)/rect.height+1;
 pickerRay.setFromCamera(mouse,camera);
 // Three.js raycasting does not automatically exclude invisible meshes.
 // Hidden native insertion symbols or hidden context walls must never be
 // selectable, even when their geometry remains in the scene for toggling.
 const hits=pickerRay.intersectObjects(pickableObjects(),false);
 if(hits.length){
  const obj=hits[0].object;
  if(obj.userData.surfaceIndex>=0){selectMaterial(obj.userData.surfaceIndex);}
  else if(obj.userData.revit_id)showNativeElement(obj.userData);
  else if(obj.userData.category==='PLAN_SCHEMATIC_FIXTURE')showPlanSymbol(obj.userData);
 }
});
document.addEventListener('keydown',e=>{
 if(e.target?.matches('input,textarea,select'))return;
 if(e.key==='1')setMode('full');if(e.key==='2')setMode('study');if(e.key==='3')setMode('context');
 if(e.key.toLowerCase()==='f')setCamera('isometric');
 if(e.key.toLowerCase()==='i')setCamera('interior');
 if(e.key.toLowerCase()==='p')setCamera('top');
 if(e.key.toLowerCase()==='a'&&state.instance!==0){state.instance=0;updateInstanceSelect();rebuild();}
 if(e.key.toLowerCase()==='b'&&state.instance!==1){state.instance=1;updateInstanceSelect();rebuild();}
});
function animate(){requestAnimationFrame(animate);orbit.update();renderer.render(scene,camera)}
let started=false;function start(){if(started)return;started=true;animate();}
function qatest(){
 const passed=[],fail=[];
 let addresses=0;
 document.body.dataset.viewerQa='RUNNING';
 try{
  for(const r of ROOMS){
   // Test the SAME rebuild path as the UI while avoiding three redundant
   // GPU renders per instance that previously obscured headless QA completion.
   state.room=r.id;state.alt=false;state.surface=-1;state.preset='isometric';
   updateRoomList();
   for(let i=0;i<2;i++){
    state.instance=i;updateInstanceSelect();
    for(const mode of ['full','study','context']){
     state.mode=mode;rebuild();
     // rebuild() renders once via setCamera(); do not re-render the full
     // Revit level context for a second, redundant GPU verification pass.
     const count=renderObjects.length;
     const good=renderObjects.every(o=>o.position.toArray().every(Number.isFinite));
     const key=r.id+'/'+instance().room_number+'/'+mode;
     if(!good)fail.push(key+':nonfinite coords');
     else passed.push(key+':'+count);
     if(mode==='full'){
      const registered=Boolean(instance()?.architecture);
      const floorCategory=registered?'ARCH_REGISTERED_FLOOR':'DRAWING_FULL_ROOM_FLOOR_STUDY';
      const floors=renderObjects.filter(o=>o.userData.category===floorCategory);
      if(floors.length!==1)fail.push(key+': no complete plan-derived bathroom floor');
      if(registered){
       if(floors.some(o=>o.userData.floor_area_not_a_purchase_quantity!==true))
        fail.push(key+': native-wall-face area incorrectly treated as purchase quantity');
      }else if(floors.some(o=>o.userData.room_area_unverified!==true))
       fail.push(key+': drawing-derived floor incorrectly verified');
      const pan=renderObjects.filter(o=>o.userData.category==='FULL_ROOM_SELECTED_PAN_SCHEMATIC');
      if(r.program?.pan_selected===true&&pan.length!==1)fail.push(key+': full room selected PAN missing');
      if(r.program?.pan_selected!==true&&pan.length)fail.push(key+': unselected/tub PAN fabricated');
      if(r.program?.tub_selected&&instance()?.architecture?.selected_tub_proxy){
       if(!renderObjects.some(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'&&o.userData.kind==='tub'&&o.userData.fixture_model==='700332000000090'))
        fail.push(key+': source-calibrated selected Duravit tub not recognizable as nominal 3D model');
      }
      if(r.program?.tub_selected&&instance()?.architecture?.selected_tub_unlocated_reason){
       if(!renderObjects.some(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'&&o.userData.kind==='tub (UNLOCATED 2D)'))
        fail.push(key+': source-conflicting selected tub not clearly marked UNLOCATED');
      }
      if(instance()?.architecture?.toilet_proxy_anchor?.proxy_polygon_door_gate_passed&&r.id!=='PH-BATH4'){
       if(!renderObjects.some(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'&&o.userData.kind==='toilet'))
        fail.push(key+': native-anchored toilet proxy suppressed despite registered source-footprint gate');
      }
      if(r.program?.dry_floor_retained&&floors.some(o=>o.userData.surfaceIndex>=0))fail.push(key+': dry wood floor incorrectly tiled');
      const visibleWalls=renderObjects.filter(o=>wallCats.has(o.userData.category)&&o.visible);
      for(const wall of visibleWalls)wall.visible=false;
      if(pickableObjects().some(o=>visibleWalls.includes(o)))
       fail.push(key+': hidden full-room wall still intercepts pointer');
      for(const wall of visibleWalls)wall.visible=true;
      if(r.full_room_plan?.fixture_symbol_diagram?.items?.length&&!renderObjects.some(o=>o.userData.category==='PLAN_SCHEMATIC_FIXTURE'))
       fail.push(key+': drawing fixture diagrams missing');
      if(r.id!=='PH-BATH4'){
       const location=wetPlacementFromPlan(r,instance());
       const wall=renderObjects.find(o=>o.userData.category==='FULL_ROOM_WET_WALL'&&o.userData.wall==='W1');
       const arch=instance()?.architecture;
       const canHost=!arch||registeredWetSupport(arch,location,stdNum(r.wet_zone_schematic?.width)||0,
        stdNum(r.wet_zone_schematic?.depth)||0);
       if(location&&productFor('wall')&&canHost){
        if(!wall||wall.userData.plan_placement!==location.side)
         fail.push(key+': frozen wet wall mismatched to drawing fixture side '+location.side);
        else{
         const w=r.full_room_plan.width_ft,d=r.full_room_plan.depth_ft;
         const support=arch?registeredWetSupport(arch,location,stdNum(r.wet_zone_schematic?.width)||0,
          stdNum(r.wet_zone_schematic?.depth)||0):null;
         const edgeDistance=support?
          (location.side==='left'||location.side==='right'?Math.abs(wall.position.x-support.face):Math.abs(wall.position.z-support.face)):
          location.side==='left'?Math.abs(wall.position.x+w/2):
          location.side==='right'?Math.abs(wall.position.x-w/2):
          location.side==='front'?Math.abs(wall.position.z-d/2):
          Math.abs(wall.position.z+d/2);
         if(edgeDistance>.20)fail.push(key+': wet W1 physically remote from '+location.side+' tub/shower edge');
        }
       }
      }
     }
     if(mode==='study'){
      const levelProduct=productFor('floor');
      const samples=renderObjects.filter(o=>o.userData.category==='UNLOCATED_LEVEL_MATERIAL_SAMPLE');
      if(levelProduct&&samples.length!==1)fail.push(key+': selected LEVEL product missing labeled material swatch');
      if(!levelProduct&&samples.length!==0)fail.push(key+': unexpected material swatch');
      const pans=renderObjects.filter(o=>o.userData.category==='dimensionedPan');
      if((r.program?.tub_selected||r.program?.kind==='TUB_OR_WALK_IN_UNSELECTED')&&pans.length)fail.push(key+': conditional/tub PAN fabricated');
      if(r.program?.pan_selected===true&&pans.length!==1)fail.push(key+': selected PAN missing');
      if(renderObjects.some(o=>o.userData.category==='REVIT_INSERTION_POINT'))
       fail.push(key+': native insertion markers leaked into unlocated study');
     }else{
      const marks=renderObjects.filter(o=>o.userData.category==='REVIT_INSERTION_POINT');
      for(const o of marks){
       const p=o.userData.location?.point,bb=o.userData.bounds_ft;
       if(!o.userData.revit_id||!o.userData.receipt_id||!p?.every?.(Number.isFinite)||
          p.some((v,j)=>v<bb.min[j]-.65||v>bb.max[j]+.65))
        fail.push(key+': invalid native insertion evidence '+o.userData.revit_id);
      }
      // Reviewer94 FIX regression: disabled insertions cannot intercept clicks,
      // and toggled-off walls cannot be hit-tested either.
      const testMarkers=marks.filter(o=>o.visible);
      const testWalls=renderObjects.filter(o=>o.userData.category==='revit_walls'&&o.visible);
      for(const o of [...testMarkers,...testWalls])o.visible=false;
      if(pickableObjects().some(o=>testMarkers.includes(o)||testWalls.includes(o)))
       fail.push(key+': hidden native marker/wall still pickable');
      for(const o of [...testMarkers,...testWalls])o.visible=true;
     }
    }
   }
   document.body.dataset.viewerQaStep=String(passed.length);
  }
  // The historic alternative is inspected as frozen data; three additional
  // expensive WebGL rebuilds are not a useful test of a selected bathroom.
  const ph4=ROOMS.find(x=>x.id==='PH-BATH4');
  if(ph4?.alternative&&!ph4.alternative.products?.length)fail.push('PH4 historic alt missing');
  if(ROOMS.length!==13)fail.push('room count !=13');
  if(ROOMS.reduce((a,r)=>a+(r.physical_instances?.length||0),0)!==26)fail.push('instance count !=26');
  for(const r of ROOMS)for(const inst of r.physical_instances){
   const got=parseInstanceAddress('#'+r.id+'/'+inst.room_number);
   if(!got||got.room!==r.id||r.physical_instances[got.instance]?.room_number!==inst.room_number)
    fail.push('deep-link broken '+r.id+'/'+inst.room_number);
   else addresses++;
  }
  if(addresses!==26)fail.push('not all 26 physical instance deep links resolve');
  if(ROOMS.some(r=>r.program?.kind==='DURAVIT_TUB_SELECTED'&&r.program.pan_selected))fail.push('TUB has selected PAN');
  if(ROOMS.some(r=>r.program?.kind==='DRY_WOOD'&&r.program.pan_selected))fail.push('DRY has selected PAN');
 }catch(e){fail.push('QA_EXCEPTION:'+e.stack)}
 fail.push(...runtimeErrors);
 const text=JSON.stringify({status:fail.length?'FIX':'PASS',tested:passed.length,physical_instance_links:addresses,probes:passed,fail});
 document.body.dataset.viewerQa=fail.length?'FIX':'PASS';
 const t=document.createElement('div');t.id='viewer-qa-result';t.textContent=text;t.style.display='none';document.body.append(t);
 console.info('VIEWER_QA_RESULT '+text);
 // Restore the owner-facing room only AFTER the machine-readable QA receipt.
 selectRoom('PH-BATH4');
 return {passed,fail};
}
async function gallery(){
 const display=document.createElement('div');display.id='viewer-gallery';
 display.dataset.status='COLLECTING';
 display.style.cssText='position:fixed;inset:0;z-index:99999;background:#0b1118;color:#e8eff4;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:repeat(4,minmax(0,1fr));gap:7px;padding:10px;overflow:hidden';
 const status=document.createElement('div');status.id='viewer-gallery-status';
 status.textContent='Collecting source-dimensional views... 0/13';
 status.style.cssText='position:absolute;bottom:12px;right:12px;background:#162537;padding:7px 12px;font:600 12px Segoe UI;border:1px solid #688ba6;z-index:2';
 display.append(status);document.body.append(display);
 const cards=[];
 for(const r of ROOMS){
  // Do not treat this capture diagnostic as architectural BIM verification.
  selectRoom(r.id);setCamera('isometric');
  const active=[...materialCache.values()].map(x=>x.ready);
  await Promise.race([Promise.all(active),new Promise(resolve=>setTimeout(resolve,2500))]);
  // The synchronous path is reliable in local headless Chrome; some
  // SwiftShader builds never resolve compileAsync during virtual-time capture.
  renderer.compile(scene,camera);
  renderer.render(scene,camera);
  renderer.getContext().finish();
  // Virtual-time headless Chrome can stall awaiting RAF, so use a bounded
  // deterministic browser timer and an explicit second GPU render.
  await new Promise(resolve=>setTimeout(resolve,800));
  renderer.render(scene,camera);renderer.getContext().finish();
  const src=canvas.toDataURL('image/png');
  if(!src.startsWith('data:image/png;base64,'))throw new Error('Canvas capture did not return PNG: '+r.id);
  cards.push({id:r.id,src,program:r.program?.kind||''});
  status.textContent='Collecting source-dimensional views... '+cards.length+'/13';
 }
 selectRoom('PH-BATH4');
 for(const card of cards){
  const box=document.createElement('div');
  box.style.cssText='border:1px solid #334c5c;overflow:hidden;background:#18242f;position:relative;min-height:0';
  const img=document.createElement('img');img.src=card.src;img.style.cssText='height:100%;width:100%;object-fit:cover';
  const label=document.createElement('div');label.textContent=card.id+' — '+card.program;
  label.style.cssText='position:absolute;top:2px;left:2px;background:#0d1724d9;padding:5px;font:600 11px Segoe UI;color:white';
  box.append(img,label);display.append(box);
 }
 status.textContent='13 / 13 captures complete. Source-registered wall faces where evidenced; room IDs and family solids not certified.';
 display.dataset.status='COMPLETE';document.body.dataset.viewerGallery='COMPLETE';
}
window.__viewerDebug={rooms:ROOMS.length,instanceTotal:ROOMS.reduce((a,r)=>a+r.physical_instances.length,0),
 selectRoom,setMode,setCamera,parseInstanceAddress,loadInstanceAddress,
 getState:()=>({...state,objectCount:renderObjects.length}),
 getCameraEvidence:()=>cameraEvidence?{...cameraEvidence}:null,
 getSceneEvidence:()=>renderObjects.map(o=>({category:o.userData?.category,
  kind:o.userData?.kind||null,source:o.userData?.source||null,
  room_number:o.userData?.room_number||null,
  native_ceiling_id:o.userData?.native_ceiling_id||null,
  native_ceiling_receipt:o.userData?.native_ceiling_receipt||null,
  height_ft:o.userData?.height_ft??null,
  coordinate_reference_kind:o.userData?.coordinate_reference_kind||null,
  native_insertion_ft:o.userData?.native_insertion_ft??null,
  native_bounds_center_ft:o.userData?.native_bounds_center_ft??null,
  native_aabb_dimensions_ft:o.userData?.native_aabb_dimensions_ft??null,
  not_family_solid:o.userData?.not_family_solid??null,
  host_id:o.userData?.host_id??null,
  native_host_thickness_ft:o.userData?.native_host_thickness_ft??null,
  nominal_width_ft:o.userData?.nominal_width_ft??null,
  revit_id:o.userData?.revit_id||null,position:o.getWorldPosition(new THREE.Vector3()).toArray()})),
 qa:qatest,errors:runtimeErrors};
try{
 if(!loadInstanceAddress(location.hash)){
  updateRoomList();updateInstanceSelect();rebuild();
 }
}catch(err){
 runtimeErrors.push('INITIAL ROOM RENDER: '+(err.stack||err.message));
 document.body.dataset.viewerFatal=String(err.message||err);
 const fatal=document.createElement('pre');fatal.id='viewer-fatal-result';
 fatal.style.cssText='position:absolute;z-index:700;left:24%;top:35%;white-space:pre-wrap;max-width:65%;background:#381b25;color:#fff;padding:15px';
 fatal.textContent='FULL ROOM RENDER ERROR: '+(err.stack||err.message);
 document.body.append(fatal);
}
const requestedMode=new URLSearchParams(location.search).get('mode');
if(['context','study','full'].includes(requestedMode))setMode(requestedMode);
window.addEventListener('hashchange',()=>loadInstanceAddress(location.hash));
start();
if(location.search.includes('qa=1'))setTimeout(qatest,180);
if(location.search.includes('gallery=1'))setTimeout(()=>gallery().catch(e=>{
 runtimeErrors.push('GALLERY: '+e.message);
 const status=document.getElementById('viewer-gallery-status');
 if(status)status.textContent='GALLERY FIX: '+e.message;
 const d=document.getElementById('viewer-gallery');if(d)d.dataset.status='FIX';
 document.body.dataset.viewerGallery='FIX';
}),480);
