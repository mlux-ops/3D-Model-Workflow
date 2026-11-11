// 1529 Wieland: verifiable dual-mode bathroom viewer.
// Source-dimensional study surfaces are never represented as native Revit solids.
// Native Revit bounds render only as a separate, unassigned level-context mode.
import * as THREE from 'three';
import { OrbitControls } from 'orbit-controls';

const DATA=JSON.parse(document.getElementById('data').textContent);
const ROOMS=DATA.rooms;
// R068 separate FROZEN source-row display: plumbing-sheet tubs have NO
// installed native tub position; do not change primary WALK-IN program or
// invent a second installed fixture by drawing them from a product listing.
const R068_PRIMARY_BATH_SHEET=JSON.parse(
 document.getElementById('r068-primary-plumbing')?.textContent||'{}');
const R068_WET_FOCUS=new Set(['PH-PRIMARY','TX-PRIMARY','PH-BATH2','TX-BATH2']);
// R069 second coordinated architectural depth group. Both BATH3 branches
// remain unselected and TX-BATH4's nominated Duravit remains 3D UNLOCATED.
const R069_FOCUS=new Set(['PH-BATH3','TX-BATH3','PH-BATH4','TX-BATH4']);
// R070 dry-room coordinated interior depth. PH-WC and TX-WC share the same
// inherited-neutral construction path; no selected WC floor or fixture claim.
const R070_DRY_FOCUS=new Set(['PH-POWDER','TX-POWDER','TX-POWDER2','PH-WC','TX-WC']);
const R063_FOCUS_BATHS=new Set(['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3']);
const R067_COMPACT_FOCUS=new Set(['PH-POWDER','PH-WC','TX-POWDER','TX-POWDER2','TX-WC']);
const canvas=document.getElementById('render');
const stage=document.getElementById('stage');
const state={room:'PH-BATH4',instance:0,mode:'full',edges:false,walls:true,sourceTraces:false,
 interiorReveal:true,ceilingPreview:false,compareAB:false,insertions:true,alt:false,surface:-1,
 preset:'isometric',focusView:false};
const runtimeErrors=[];
let completionInstalled=false;
let nativeAuditInstalled=false;
window.addEventListener('error',e=>runtimeErrors.push('JS: '+e.message));
window.addEventListener('unhandledrejection',e=>runtimeErrors.push('Promise: '+String(e.reason)));
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.65));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
// R065: neutral photographic studio exposure. Lower broad wash, retaining
// actual selected material-color atlases, their normal/grout and polished
// ceramic response. These are VIEWER lights, never source Revit luminaires.
renderer.toneMappingExposure=.895;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x17222b);
const camera=new THREE.PerspectiveCamera(48,1,.025,1400);
const orbit=new OrbitControls(camera,renderer.domElement);
orbit.enableDamping=true;orbit.dampingFactor=.105;
orbit.minDistance=.65;orbit.maxDistance=260;
orbit.maxPolarAngle=Math.PI*.94;
const hemi=new THREE.HemisphereLight(0xe8eef3,0x635c53,1.02);scene.add(hemi);
const ambient=new THREE.AmbientLight(0xffffff,.14);scene.add(ambient);
const main=new THREE.DirectionalLight(0xfff0df,2.03);
main.position.set(-9,14,11);main.castShadow=true;
main.shadow.mapSize.set(2048,2048);
main.shadow.camera.left=-45;main.shadow.camera.right=45;
main.shadow.camera.top=45;main.shadow.camera.bottom=-45;
main.shadow.camera.near=.3;main.shadow.camera.far=110;
main.shadow.bias=-.0002;scene.add(main);
const bounce=new THREE.DirectionalLight(0xd5e4ed,.78);
bounce.position.set(10,6,-9);scene.add(bounce);
const keyLight=new THREE.PointLight(0xfff0e2,18,35,2);
keyLight.position.set(0,12,2);scene.add(keyLight);
// Soft studio environment. Not a claimed site-specific HDRI.
const env=new THREE.Scene();env.background=new THREE.Color(0x8d9a9f);
env.add(new THREE.HemisphereLight(0xeef5ff,0x665545,3.3));
const pmrem=new THREE.PMREMGenerator(renderer);
scene.environment=pmrem.fromScene(env,.06).texture;
const neutral={
 wall:new THREE.MeshStandardMaterial({color:0xe3dcd0,roughness:.86,side:THREE.DoubleSide}),
 missing:new THREE.MeshStandardMaterial({color:0x7d8388,roughness:.82,side:THREE.DoubleSide}),
 // R062 no-pick LEVEL is a neutral architectural surface, never a selected
 // tile/stone SKU. A lighter mineral tone separates it from source wall faces
 // without adding artificial grout, purchasing, pan slope or a maker claim.
 flooring:new THREE.MeshPhysicalMaterial({color:0xb5aea4,roughness:.87,
  metalness:0,clearcoat:.035,side:THREE.DoubleSide}),
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
// R065: a restrained matte-plaster NORMAL-ONLY studio study on actual
// native-bound wall boxes (not a selected paint SKU, gypsum profile,
// waterproofing product or Revit material parameter). Single GPU DataTexture
// with source-foot planar wall UVs; original wall thicknesses/openings/IDs
// remain wholly untouched. Neutral is deliberately non-directional.
function makeNeutralWallPlasterNormal(){
 const W=256,H=256,pixels=new Uint8Array(W*H*4);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const p=(y*W+x)*4;
  const waveX=Math.sin(x*.38+y*.14)*.54+Math.sin(x*.89-y*.24)*.24;
  const waveY=Math.cos(y*.42-x*.16)*.53+Math.sin(y*.78+x*.33)*.26;
  pixels[p]=Math.round(128+waveX*9);
  pixels[p+1]=Math.round(128+waveY*9);
  pixels[p+2]=254;pixels[p+3]=255;
 }
 const t=new THREE.DataTexture(pixels,W,H,THREE.RGBAFormat,THREE.UnsignedByteType);
 t.wrapS=t.wrapT=THREE.RepeatWrapping;
 t.magFilter=THREE.LinearFilter;t.minFilter=THREE.LinearMipmapLinearFilter;
 t.generateMipmaps=true;t.anisotropy=8;t.needsUpdate=true;
 return t;
}
const neutralWallPlasterNormal=makeNeutralWallPlasterNormal();
// R060: retained, UNSELECTED wood is not a gray-tan tile or a claimed maker
// material. Give the three DRAWING-INFERRED dry powder footprints a quiet,
// deterministic plank/grain study. Its widths, seams and orientation are
// illustrative, not an actual existing-floor SKU, installation or takeoff.
function makeRetainedWoodStudy(){
 const c=document.createElement('canvas');c.width=512;c.height=1024;
 const g=c.getContext('2d');
 g.fillStyle='#b69a78';g.fillRect(0,0,512,1024);
 const board=64;
 for(let col=0;col<8;col++){
  const left=col*board,phase=(col*173+79)%1024;
  const shade=col%3===0?'#b49a7d':col%3===1?'#bea58a':'#b8a082';
  g.fillStyle=shade;g.fillRect(left+2,0,board-3,1024);
  for(let k=0;k<44;k++){
   const x=left+4+((k*37+col*19)%55),wave=Math.sin(k*.84+col)*1.8;
   g.strokeStyle=k%4===0?'rgba(91,66,44,.095)':'rgba(247,222,187,.12)';
   g.lineWidth=k%5===0?1.6:.65;g.beginPath();
   g.moveTo(x,0);
   g.bezierCurveTo(x+wave,380,x-wave,700,x+Math.sin(k+col)*2,1024);
   g.stroke();
  }
  for(const y of [phase,(phase+590)%1024]){
   g.fillStyle='rgba(83,68,53,.22)';g.fillRect(left+2,y,board-3,2);
   g.fillStyle='rgba(246,226,201,.18)';g.fillRect(left+2,y+2,board-3,1);
  }
  g.fillStyle='rgba(77,61,48,.25)';g.fillRect(left,0,2,1024);
 }
 const t=new THREE.CanvasTexture(c);
 t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;
 // ShapeGeometry's planar UVs are native DRAWING-REGISTERED feet. Two-by-four
 // foot texture period; the rectangular plank pattern is display-only.
 t.repeat.set(.5,.25);t.anisotropy=8;
 // R070 tactile plank-grain NORMAL follows exactly the same illustrative
 // 2x4ft material repeat. It is an optical retained-wood preview, NOT an
 // inferred manufacturer, thickness, board layout, species or restoration.
 const n=document.createElement('canvas');n.width=512;n.height=1024;
 const ng=n.getContext('2d'),ni=ng.createImageData(512,1024);
 for(let y=0;y<1024;y++)for(let x=0;x<512;x++){
  const j=(y*512+x)*4;
  const seam=x%64<3||x%64>61;
  const grain=Math.sin(x*.52+Math.sin(y*.025)*2.4)*.58+
   Math.sin(x*.21+y*.017)*.40;
  ni.data[j]=Math.max(0,Math.min(255,Math.round(128+grain*(seam?8:18))));
  ni.data[j+1]=Math.max(0,Math.min(255,Math.round(128+
   (Math.sin(y*.043+x*.016)*.36+(seam?.20:0))*14)));
  ni.data[j+2]=seam?239:252;ni.data[j+3]=255;
 }
 ng.putImageData(ni,0,0);
 const normal=new THREE.CanvasTexture(n);
 normal.wrapS=normal.wrapT=THREE.RepeatWrapping;
 normal.repeat.copy(t.repeat);normal.anisotropy=8;
 return new THREE.MeshPhysicalMaterial({map:t,normalMap:normal,
  normalScale:new THREE.Vector2(.27,.19),
  color:0xffffff,roughness:.69,
  metalness:0,clearcoat:.15,clearcoatRoughness:.52,
  envMapIntensity:.79,side:THREE.DoubleSide,
  userData:{r070_wood_preview_only:true,
   r070_nominal_plank_layout_selected:false,
   retained_original_floor_material_unknown:true}});
}
neutral.wood=makeRetainedWoodStudy();
const enclosureSide=new THREE.MeshPhysicalMaterial({color:0xcbd6dc,transparent:true,opacity:.14,roughness:.78,side:THREE.DoubleSide,depthWrite:false});
const enclosureBack=new THREE.MeshStandardMaterial({color:0xd5d2c9,roughness:.82,side:THREE.DoubleSide});
const insertionMaterial=new THREE.PointsMaterial({color:0xffc974,size:7.5,sizeAttenuation:false,depthTest:false,depthWrite:false,transparent:true});
const materialCache=new Map();
let modelGroup=new THREE.Group();scene.add(modelGroup);
let renderObjects=[],materialObjects=[],modeInfo='',sceneBounds=null;
let rebuildRevision=0;
const pickerRay=new THREE.Raycaster(),mouse=new THREE.Vector2();
let modal=null;

const style=document.createElement('style');
style.textContent=`
#viewer-v2-toolbar{position:absolute;z-index:5;top:158px;left:20px;display:flex;gap:6px;align-items:center;flex-wrap:wrap;max-width:calc(100% - 136px)}
.viewer-select,.viewer-btn{background:#14212ee6;border:1px solid #5c7486;border-radius:5px;color:#edf4f7;padding:7px 8px;font:600 10.5px/1.32 "Segoe UI",Arial,sans-serif;letter-spacing:0}
.viewer-btn[aria-pressed=true]{background:#b59b79;color:#0f1b26;border-color:#dec7aa}
.viewer-btn:hover,.viewer-select:hover{border-color:#dfc3a0}
#viewer-v2-fidelity{position:absolute;z-index:2;bottom:79px;left:23px;right:24px;max-width:790px;max-height:63px;overflow:hidden;color:#e5d2b1;font-size:11px;line-height:1.45;background:#0c1a27dc;border:1px solid #52617377;border-radius:5px;padding:8px 10px;text-shadow:0 1px 3px #071019;pointer-events:none}
#stage .stage-top>div:first-child{background:#0a1825e0;border:1px solid #536a7b77;border-radius:7px;padding:8px 12px;max-width:min(610px,73%)}
#stage .stage-top h1{color:#fff;text-shadow:0 1px 2px #060d16}
#stage .stage-top .scene-note{color:#d7e3eb}
#viewer-v2-source{font-size:11px;color:#9eb3c4;line-height:1.6;margin-top:11px}
#viewer-v2-source strong{color:#e4eaf0}
#viewer-v2-element{font-size:11px;color:#c1d8e2;line-height:1.55;margin:10px 0;padding:11px 12px;border:1px solid #597182;border-radius:7px;background:#192b36}
#viewer-v2-element strong{color:#ffda9c}
#viewer-v2-info{position:absolute;z-index:2;top:310px;left:25px;color:#c4d2de;background:#14212bca;border:1px solid #526577;border-radius:5px;padding:8px 10px;font-size:11px;line-height:1.5;pointer-events:none;max-width:330px}
.viewer-ab-drawer{position:absolute;z-index:7;top:305px;right:18px;width:min(570px,calc(100% - 36px));max-height:calc(100% - 415px);min-height:240px;overflow:auto;color:#e6e7e5;background:#111e29f5;border:1px solid #b89c7a;border-radius:8px;box-shadow:0 12px 36px #07121ec9;padding:12px}
.viewer-ab-drawer[hidden]{display:none}
.viewer-ab-card{flex:1;min-width:190px;background:#1b2b35;border:1px solid #52687b;border-radius:6px;padding:9px}
.viewer-ab-card svg{width:100%;height:200px;display:block;background:#0d202b;border-radius:4px}
.viewer-ab-card strong{color:#f2d0a4;font-size:12px}
.viewer-ab-card small{display:block;color:#b4c5ce;margin-top:5px;line-height:1.4}
.viewer-interaction-hint{font-size:10px;color:#9faeba;line-height:1.5;margin:12px 0}
#viewer-focus-enter{background:#c7a985;color:#0e202b;border-color:#e2cbac;font-weight:700}
/* R064: an immersive, entirely reversible presentation layer.  It changes
   viewport/UI composition, NOT the source geometry, room attribution or picks.
   Fullscreen is intentionally CSS-only so offline file:// Chrome works. */
#stage.viewer-focus-active{position:fixed!important;inset:0!important;z-index:60!important;
 width:100vw!important;height:100vh!important;height:100dvh!important;min-height:0!important;
 background:radial-gradient(ellipse at 55% 34%,#2b3a48 0%,#0f1720 76%)}
#stage.viewer-focus-active>.stage-top,#stage.viewer-focus-active>.tools,
#stage.viewer-focus-active>#viewer-v2-toolbar,#stage.viewer-focus-active>#viewer-v2-fidelity,
#stage.viewer-focus-active>#viewer-v2-info{display:none!important}
#stage.viewer-focus-active .stage-bottom{bottom:14px;left:16px;right:16px;opacity:.64;
 transition:opacity .2s;pointer-events:none}
#stage.viewer-focus-active .stage-bottom:hover{opacity:1}
#viewer-focus-bar{display:none;position:absolute;left:16px;right:16px;top:13px;z-index:25;
 align-items:center;gap:9px;flex-wrap:wrap;padding:11px 13px;border:1px solid #82919a91;
 border-radius:10px;background:#0d1c29e8;box-shadow:0 10px 30px #07101985;
 backdrop-filter:blur(10px)}
#stage.viewer-focus-active #viewer-focus-bar{display:flex}
#viewer-focus-bar .viewer-btn,#viewer-focus-bar .viewer-select{font-size:12px;min-height:35px;
 padding:7px 10px;border-radius:6px}
#viewer-focus-bar #viewer-focus-exit{color:#ffdfb8;border-color:#bd9a6d;background:#352a25}
#viewer-focus-room-label{display:flex;flex-direction:column;min-width:156px;max-width:210px;
 margin:0 8px 0 1px;line-height:1.3}
#viewer-focus-room-label strong{font-size:13px;color:#fff;letter-spacing:.015em}
#viewer-focus-room-label span{font-size:10px;color:#9cb0be;letter-spacing:.02em}
#viewer-focus-bar select{max-width:178px;cursor:pointer}
#viewer-focus-bar button[aria-pressed=true]{border-color:#ddc4a2;background:#b59b79;color:#12212e}
#viewer-focus-evidence{margin-left:auto}
#viewer-focus-caption{display:none;position:absolute;left:18px;bottom:54px;z-index:8;
 background:#0b1a27d9;border:1px solid #71829065;border-radius:5px;padding:7px 11px;
 font-size:10px;letter-spacing:.05em;color:#c4d0d8;pointer-events:none;max-width:65%}
#stage.viewer-focus-active #viewer-focus-caption{display:block}
#stage.viewer-focus-active .viewer-ab-drawer{top:82px;right:16px;
 max-height:calc(100% - 145px);z-index:30}
@media(max-width:860px){#viewer-focus-bar{left:8px;right:8px;top:7px;padding:7px;gap:5px}
 #viewer-focus-room-label{min-width:100px}#viewer-focus-bar .viewer-btn,
 #viewer-focus-bar .viewer-select{font-size:10px;padding:6px;min-height:30px}
 #viewer-focus-caption{max-width:90%;bottom:45px}}
@media(max-width:860px){#viewer-v2-toolbar{top:146px;left:12px;max-width:calc(100% - 20px)}#viewer-v2-info{top:328px;left:12px}#viewer-v2-fidelity{bottom:70px;left:12px}}
`;
document.head.appendChild(style);
const toolbar=document.createElement('div');toolbar.id='viewer-v2-toolbar';
toolbar.innerHTML=`<select id="viewer-instance" class="viewer-select" aria-label="Physical room instance"></select>
<button id="viewer-mode-full" class="viewer-btn" aria-pressed="true">Full bathroom</button>
<button id="viewer-mode-study" class="viewer-btn" aria-pressed="false">Wet-zone detail</button>
<button id="viewer-mode-context" class="viewer-btn" aria-pressed="false">Revit level context</button>
<button id="viewer-camera-iso" class="viewer-btn" title="Isometric view">3D</button>
<button id="viewer-camera-inside" class="viewer-btn" title="Close architectural cutaway camera (no unsupported first-person location)">Cutaway</button>
<button id="viewer-camera-fixture" class="viewer-btn" title="R058 exterior focus target follows selected source-bounded tub or original native countertop AABB; never a source-certified standing position">Fixture focus</button>
<button id="viewer-r060-counter-focus" class="viewer-btn" title="R060 source AABB countertop review: exterior close camera. No sink, faucet or cabinetry location inferred">Countertop</button>
<button id="viewer-r062-primary-vanity" class="viewer-btn" title="R062 primary source-bounded 9ft Countertop-category long-axis envelope; exterior review camera, not a Revit standing point or selected sink">Primary vanity</button>
<button id="viewer-r062-primary-shell" class="viewer-btn" title="R062 primary L-plan native wall returns and source-hosted openings in 3D, with explicit unlocated walk-in/drain position">Primary enclosure</button>
<button id="viewer-r063-bath-finish" class="viewer-btn" title="R063 four-bath exterior finished-wall/nominal tub view follows registered source wall and drawing wet-side, not a physical doorway or installed fixture camera">Bath finish</button>
<button id="viewer-r060-wc-focus" class="viewer-btn" title="R060 physical instance's native toilet anchor and source-gated generic porcelain proxy, from an exterior camera">WC focus</button>
<button id="viewer-camera-wet" class="viewer-btn" title="R059 opposite-side EXTERIOR wet-wall review; selected tile surfaces and drawing-derived orientation preserved, no invented doorway point">Wet wall</button>
<button id="viewer-camera-front" class="viewer-btn" title="Wall elevation">Elevation</button>
<button id="viewer-camera-top" class="viewer-btn" title="Plan view">Plan</button>
<button id="viewer-ceiling-preview" class="viewer-btn" aria-pressed="false" title="Reversible translucent GWB underside witness bounded by inferred room wall faces; NOT a native ceiling trim/solid">Ceiling OFF</button>
<button id="viewer-ph4-focus-311" class="viewer-btn" title="PH4: source-wall-face focused 311 wet compartment; 310 remains an independent contextual volume">311 shower</button>
<button id="viewer-ph4-focus-310" class="viewer-btn" title="PH4: exterior architectural focus on source-registered adjoining 310A WIC4 / 310B Bath4, never part of 311 material pool">310 context</button>
<button id="viewer-reveal-interior" class="viewer-btn" aria-pressed="true" title="Reversible camera-facing visual wall and wet-tile cutaway. Original source heights, openings and material quantities stay unchanged.">Interior reveal ON</button>
<button id="viewer-toggle-source-traces" class="viewer-btn" aria-pressed="false" title="Show/hide native source bounding wires; actual geometry, source data and material picks unchanged">Source traces OFF</button>
<button id="viewer-compare-ab" class="viewer-btn" aria-pressed="false" title="Compare both actual source-wall-face polygons, openings and fixture anchors in plan">Compare A/B</button>
<button id="viewer-focus-enter" class="viewer-btn" title="R064: expand the actual 3D scene to the full offline viewport and temporarily collapse analytical overlays; original source/evidence still available">Focus view</button>
<button id="viewer-insertions" class="viewer-btn" aria-pressed="true" title="Actual native Revit fixture/casework insertion points and rotations, without room attribution">Native insertions ON</button>`;
stage.appendChild(toolbar);
const focusBar=document.createElement('nav');focusBar.id='viewer-focus-bar';
focusBar.setAttribute('aria-label','Immersive source-faithful bathroom view controls');
focusBar.innerHTML=`<button type="button" id="viewer-focus-exit" class="viewer-btn" title="Exit focus view and show all source evidence (Esc)">Exit focus</button>
<div id="viewer-focus-room-label"><strong id="viewer-focus-title">Bathroom</strong><span id="viewer-focus-level">Drawing-registered study</span></div>
<select id="viewer-focus-room" class="viewer-select" aria-label="Bathroom type"></select>
<select id="viewer-focus-instance" class="viewer-select" aria-label="Physical A/B instance"></select>
<button type="button" id="viewer-focus-full" class="viewer-btn" title="Full bathroom room volume">Full</button>
<button type="button" id="viewer-focus-wet" class="viewer-btn" title="Look at the frozen wet wall from a source-aware exterior camera">Wet wall</button>
<button type="button" id="viewer-focus-finish" class="viewer-btn" title="Source-aware exterior selected-finish camera for PH/TX Bath2 and Bath3 A/B">Bath finish</button>
<button type="button" id="viewer-focus-architectural" class="viewer-btn" title="Source-native PH/TX primary Countertop AABB, PH4 311 selected shower or TX4 short countertop from exterior; not occupied standing position">Assembly</button>
<button type="button" id="viewer-focus-plan" class="viewer-btn" title="Plan camera; no new source geometry">Plan</button>
<button type="button" id="viewer-focus-iso" class="viewer-btn" title="Isometric camera">3D</button>
<button type="button" id="viewer-focus-cutaway" class="viewer-btn" aria-pressed="true" title="Reversible camera-facing section of source wall meshes; no construction or fixture change">Section ON</button>
<button type="button" id="viewer-focus-gwb" class="viewer-btn" aria-pressed="false" title="Optional translucent reference at the independently matched Revit GWB underside; XY remains inferred, not a native ceiling panel">GWB ghost OFF</button>
<button type="button" id="viewer-focus-ab" class="viewer-btn" aria-pressed="false" title="Compare separately registered A/B plans">A/B</button>
<button type="button" id="viewer-focus-traces" class="viewer-btn" aria-pressed="false" title="Show native source wires without new room/fixture geometry">Source lines</button>
<button type="button" id="viewer-focus-evidence" class="viewer-btn" title="Return to inspector and open original evidence">Evidence</button>`;
stage.appendChild(focusBar);
const focusCaption=document.createElement('div');focusCaption.id='viewer-focus-caption';
focusCaption.textContent='VIEWER-ONLY Â· Drawing-registered room faces; no certified Revit Room solids, source fixture families or owner approvals';
stage.appendChild(focusCaption);
const abDrawer=document.createElement('section');
abDrawer.id='viewer-ab-drawer';abDrawer.className='viewer-ab-drawer';abDrawer.hidden=true;
abDrawer.setAttribute('aria-label','A and B source-derived room-plan comparison');
stage.appendChild(abDrawer);
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
selectedRevit.innerHTML='<summary style="cursor:pointer;font-weight:700;color:#f0d6ac">Native element details Â· unassigned</summary><div id="viewer-v2-element-detail"></div>';
roomEvidence.after(selectedRevit);
const cameraStatus=document.createElement('span');cameraStatus.id='viewer-camera-state';

function current(){return ROOMS.find(x=>x.id===state.room);}
function instance(){const r=current();return r?.physical_instances?.[state.instance]||null;}
function productList(){const r=current();return state.alt&&r?.alternative?r.alternative.products:r?.products||[];}
function productFor(which){const p=productList();return which==='wall'?p.find(x=>/wall|tub|wet/i.test(x.surface))
 :which==='floor'?p.find(x=>/level|floor|pan/i.test(x.surface))
 :p.find(x=>/niche/i.test(x.surface));}
function htmlEscape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','"':'&quot;',"'":'&#39;'}[c]));}
function stdNum(info){return info&&Number.isFinite(+info.value)?+info.value:null;}
function normalizeSize(s){
 // Original frozen Smartsheet/handoff rows contain U+FFFD in place of a
 // multiplication sign (e.g. "24ï¿½24, actual 23.50ï¿½23.50"). Recover ONLY
 // dimension separator encoding for the display atlas, never edit a source
 // product, selected size or SKU. The earlier regex silently fell back to
 // generic 1Ã—2ft for every corrupted tile size; both wall and floor scale
 // were visually wrong. First pair is NOMINAL product size, not "actual".
 const m=String(s||'').match(/(\d+(?:\.\d+)?)\s*[xÃ—\uFFFD]\s*(\d+(?:\.\d+)?)/i);
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
 // R061: the earlier atlas inset a FULL nominal joint on EACH edge, doubling
 // the visible seam at neighboring tiles. Half-joint per side restores the
 // 1/16in illustrative joint. Grout is NOT an owner-selected color/width.
 const gap=(.0625/12)/2;
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
  // PBR relief illustrates a slight ceramic arris at the tile/grout border,
  // NOT an extracted manufacturer thickness or a chosen joint profile.
  const bevelX=Math.max(1,Math.min(5,Math.round(gx*.8))),
   bevelY=Math.max(1,Math.min(5,Math.round(gy*.8)));
  const left=x-gx,right=(c.width-gx)-x,top=y-gy,bottom=(c.height-gy)-y;
  const nx=joint?0:left>=0&&left<bevelX?-.27*(1-left/bevelX):
   right>=0&&right<bevelX?.27*(1-right/bevelX):0;
  const ny=joint?0:top>=0&&top<bevelY?-.27*(1-top/bevelY):
   bottom>=0&&bottom<bevelY?.27*(1-bottom/bevelY):0;
  const grain=joint?0:.014*Math.sin(x*.057)*Math.cos(y*.033);
  im.data[px]=Math.round(127+(nx+grain)*128);
  im.data[px+1]=Math.round(127+(ny+grain*.65)*128);
  im.data[px+2]=Math.round(joint?247:253);
  im.data[px+3]=255;
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
   // R068 photographic-depth pass for the two retained selected Bath2
   // glossy wall programs. Vendor photo remains a color/relief STAND-IN,
   // not an approved shade, wet-area finish sample or chosen grout layout.
   const r068Bath2Glazed=R068_WET_FOCUS.has(state.room)&&
    current()?.program?.kind==='DURAVIT_TUB_SELECTED'&&
    orientation==='wall';
   const r069Selected=R069_FOCUS.has(state.room)&&orientation==='wall';
   ctx.globalAlpha=r069Selected?(glossy?.37:.32):r068Bath2Glazed?.30:.23;
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
 const r068Bath2Glazed=R068_WET_FOCUS.has(state.room)&&
  current()?.program?.kind==='DURAVIT_TUB_SELECTED'&&
  orientation==='wall'&&atlas.glossy;
 const r069Selected=R069_FOCUS.has(state.room)&&orientation==='wall';
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
   normalScale:r069Selected?new THREE.Vector2(.34,.30):
    r068Bath2Glazed?new THREE.Vector2(.27,.25):new THREE.Vector2(.19,.19),
   roughness:glossy?(r069Selected?.20:r068Bath2Glazed?.22:.26):r069Selected?.66:.73,
   metalness:0,clearcoat:glossy?(r069Selected?.58:r068Bath2Glazed?.55:.45):.04,
   clearcoatRoughness:glossy?(r069Selected?.15:r068Bath2Glazed?.17:.23):.8,
    envMapIntensity:glossy?(r069Selected?1.08:r068Bath2Glazed?1.02:.88):.57,
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
   tileSizeFt:[tw,th],pooledTile:true,atlas,sceneOwnedTextures:true,typedSourcePhoto:true,retired:false,
   r068_selected_bath2_glazed_optical_relief:!!r068Bath2Glazed,
   r068_nominal_tile_ft:[tw,th],r068_grout_not_selected:true,
   r069_selected_ceramic_relief:r069Selected,
   r069_nominal_tile_ft:[tw,th],r069_maker_photo_not_sample:true,
   r069_grout_joint_illustrative_only:true};
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
 const mat=new THREE.MeshPhysicalMaterial({map,normalMap:normal,
  normalScale:r069Selected?new THREE.Vector2(.33,.29):
   r068Bath2Glazed?new THREE.Vector2(.26,.24):new THREE.Vector2(.19,.19),
  roughness:r069Selected?(atlas.glossy?.20:.68):
   r068Bath2Glazed?.22:atlas.roughness,
  metalness:0,clearcoat:atlas.glossy?(r069Selected?.57:r068Bath2Glazed?.54:.42):.03,
  clearcoatRoughness:atlas.glossy?(r069Selected?.15:r068Bath2Glazed?.17:.20):.75,
  side:THREE.DoubleSide,
  // Prevent dark manufacturer glossy finishes from becoming pure black on
  // rooms whose study planes have no verified surrounding reflected surfaces.
  emissive:new THREE.Color('rgb('+tileShade(p).join(',')+')'),
  emissiveIntensity:atlas.glossy?.18:.08});
 mat.userData={pooledTile:true,atlas,sceneOwnedTextures:true,
  r068_selected_bath2_glazed_optical_relief:!!r068Bath2Glazed,
  r068_nominal_tile_ft:[tw,th],r068_grout_not_selected:true,
  r069_selected_ceramic_relief:r069Selected,
  r069_nominal_tile_ft:[tw,th],r069_maker_photo_not_sample:true,
  r069_grout_joint_illustrative_only:true};return mat;
}
// R063: ShapeGeometry assigns UV in the original XY FEET, unlike PlaneGeometry
// (normalized [0,1]). The old room floor passed room span (5-14ft) into
// tileMaterial, which tiled its ShapeGeometry UV *again* by the whole span.
// In a 7ft room, nominal 2ft tile became ~3.4in graphical repeat. This
// source-native geometry uses ONE texture cycle per actual NOMINAL tile feet;
// it is a VISUAL layout, not a chosen starting point or shop drawing.
function registeredFloorMaterial(p){
 const m=tileMaterial(p,1,1,'floor');
 const s=m.userData?.tileSizeFt||[1,2];
 m.userData={...m.userData,registered_floor_feet_based_uv:true,
  repeat_per_source_ft:[1/s[0],1/s[1]],
  tile_layout_selected:false,grout_selected:false,
  source:'Source wall-face polygon UV are unnormalized Revit-origin feet; nominal dimensions remain source SKU only'};
 return m;
}
// R068 neutral corner/footfall falloff is baked ONLY to actual wall BOX
// faces, not a new wall, selected paint, baseboard, shower assembly or panel.
// Child-of-source-wall construction inherits every R057 camera cutaway and
// R065 wall-hide/Focus operation, preventing floating optical ghost planes.
let r068NativeWallLightMat=null;
function r068SourceWallLightMaterial(){
 if(r068NativeWallLightMat)return r068NativeWallLightMat;
 const c=document.createElement('canvas');c.width=256;c.height=256;
 const g=c.getContext('2d'),img=g.createImageData(256,256);
 for(let y=0;y<256;y++)for(let x=0;x<256;x++){
  const edge=Math.pow(1-Math.min(x,255-x)/127.5,4.2);
  const foot=Math.pow(y/255,4.3);
  const corner=.54*edge+.38*foot+.16*edge*foot;
  const j=(y*256+x)*4;
  img.data[j]=33;img.data[j+1]=35;img.data[j+2]=40;
  img.data[j+3]=Math.round(Math.min(1,corner)*95);
 }
 g.putImageData(img,0,0);
 const map=new THREE.CanvasTexture(c);map.colorSpace=THREE.SRGBColorSpace;
 map.anisotropy=8;
 r068NativeWallLightMat=new THREE.MeshBasicMaterial({map,
  transparent:true,depthWrite:false,side:THREE.DoubleSide,
  polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 return r068NativeWallLightMat;
}
// Subtle foot-of-wall contact lighting constructed ONLY from the native wall
// portions actually shown after nominal hosted-opening cuts. This thin alpha
// gradient is NOT a baseboard, tile, moisture detail, separate floor or
// room boundary; it creates perceived spatial depth without adding scope.
function sourceWallContactMaterial(){
 const c=document.createElement('canvas');c.width=16;c.height=128;
 const g=c.getContext('2d');
 const fade=g.createLinearGradient(0,0,0,128);
 fade.addColorStop(0,'rgba(16,20,24,.30)');
 fade.addColorStop(.17,'rgba(16,20,24,.13)');
 fade.addColorStop(.65,'rgba(16,20,24,.025)');
 fade.addColorStop(1,'rgba(16,20,24,0)');
 g.fillStyle=fade;g.fillRect(0,0,16,128);
 const t=new THREE.CanvasTexture(c);
 t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping;
 const m=new THREE.MeshBasicMaterial({map:t,transparent:true,depthWrite:false,
  depthTest:true,side:THREE.DoubleSide,polygonOffset:true,
  polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 // This is persistent and does NOT use pooled scene maps.
 return m;
}
const sourceWallContactAO=sourceWallContactMaterial();
function makeNativeHostedFinishCornerShade(){
 const c=document.createElement('canvas');c.width=128;c.height=12;
 const g=c.getContext('2d');const fade=g.createLinearGradient(0,0,128,0);
 fade.addColorStop(0,'rgba(19,24,29,.23)');
 fade.addColorStop(.20,'rgba(19,24,29,.10)');
 fade.addColorStop(1,'rgba(19,24,29,0)');
 g.fillStyle=fade;g.fillRect(0,0,128,12);
 const map=new THREE.CanvasTexture(c);
 map.wrapS=map.wrapT=THREE.ClampToEdgeWrapping;
 return new THREE.MeshBasicMaterial({map,side:THREE.DoubleSide,
  transparent:true,depthWrite:false,depthTest:true});
}
const sourceWetFinishCornerShadeMaterial=makeNativeHostedFinishCornerShade();
// R068 source-hosted, view-only tub/finish contact illumination. The
// registered Duravit 59x29.5 nominal footprint is ALREADY drawing-calibrated
// and wall-face contained in PH/TX Bath2; it is not a native tub solid.
// Add no new tile/waterproofing/rough-in here. Only source-backed W1/W2/W3
// planes that actually approach that nominal silhouette get a soft optical
// contact ribbon near its ILLUSTRATIVE ~1.5ft vessel lip. For 305A/B W1 is
// the old .72ft REVIEW CUTAWAY and consequently cannot get a floating ribbon.
let r068TubContactMaterial=null;
function r068TubContactPhotoMaterial(){
 if(r068TubContactMaterial)return r068TubContactMaterial;
 const c=document.createElement('canvas');c.width=64;c.height=128;
 const g=c.getContext('2d'),f=g.createLinearGradient(0,0,0,128);
 f.addColorStop(0,'rgba(25,32,39,0)');
 f.addColorStop(.38,'rgba(25,32,39,.02)');
 f.addColorStop(.74,'rgba(25,32,39,.13)');
 f.addColorStop(1,'rgba(25,32,39,.29)');
 g.fillStyle=f;g.fillRect(0,0,64,128);
 const tex=new THREE.CanvasTexture(c);
 tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=8;
 r068TubContactMaterial=new THREE.MeshBasicMaterial({map:tex,
  transparent:true,depthWrite:false,side:THREE.DoubleSide,
  polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 return r068TubContactMaterial;
}
function drawR068TubSourceFinishContact(room,arch){
 if(!['PH-BATH2','TX-BATH2'].includes(room?.id))return 0;
 const tub=arch?.selected_tub_proxy;
 if(!tub?.local_center_xz_ft||tub.model_or_sku!=='700332000000090')return 0;
 const [tx,tz]=tub.local_center_xz_ft,hw=tub.nominal_width_ft/2,
  hd=tub.nominal_depth_ft/2;
 const lip=1.52,bandH=.30;let made=0;
 // Must not augment a source-unmatched return, a false niche or a generic
 // wet plane. The plane's native host ID and real local source wall line are
 // recorded independently; named room attribution remains drawing-inferred.
 const selected=[...renderObjects].filter(o=>o.userData?.category==='FULL_ROOM_WET_WALL'&&
  o.userData.native_host_face_id &&o.geometry?.parameters?.width);
 for(const wet of selected){
  const H=wet.geometry.parameters.height||0;
  if(wet.position.y+H/2<lip+bandH*.55)continue;
  const vertical=Math.abs(Math.sin(wet.rotation.y))>.70;
  const face=vertical?wet.position.x:wet.position.z;
  const nearer=vertical?Math.min(Math.abs(face-(tx-hw)),Math.abs(face-(tx+hw))):
   Math.min(Math.abs(face-(tz-hd)),Math.abs(face-(tz+hd)));
  if(nearer>.22)continue;
  const center=vertical?wet.position.z:wet.position.x;
  const radius=(wet.geometry.parameters.width||0)/2;
  const tubMin=vertical?tz-hd:tx-hw,tubMax=vertical?tz+hd:tx+hw;
  const lo=Math.max(center-radius,tubMin),hi=Math.min(center+radius,tubMax);
  if(hi-lo<.48)continue;
  const mid=(lo+hi)/2;
  const p=vertical?
   [face+Math.sign(tx-face)*.029,lip+.04,mid]:
   [mid,lip+.04,face+Math.sign(tz-face)*.029];
  const shade=new THREE.Mesh(new THREE.PlaneGeometry(hi-lo,bandH),
   r068TubContactPhotoMaterial());
  shade.position.set(...p);shade.rotation.y=wet.rotation.y;
  shade.renderOrder=7;shade.raycast=()=>{};
  shade.userData={category:'ARCH_R068_SOURCE_WET_CONTACT_LIGHT',
   room_number:instance()?.room_number,wall:wet.userData.wall,
   native_host_face_id:wet.userData.native_host_face_id,
   native_host_face_receipt:wet.userData.native_host_face_receipt,
   source_tub_sku:tub.model_or_sku,
   source_tub_center_local_xz_ft:tub.local_center_xz_ft,
   source_nominal_tub_width_ft:tub.nominal_width_ft,
   source_nominal_tub_depth_ft:tub.nominal_depth_ft,
   r068_render_span_ft:hi-lo,r068_study_gap_ft:nearer,
   r068_not_additional_tile_area:true,r068_contact_studio_light_only:true,
   no_tub_installed_height_verified:true,no_waterproofing_slope_roughin:true,
   source:'R068 optical contact shade ONLY on pre-existing selected tile plane with actual matched native host wall ID, near drawing-calibrated nominal Duravit tub footprint. Tub installation height, tile joint termination, waterproofing, silicone, trims, drain, rough-ins and takeoff NOT certified.'};
  modelGroup.add(shade);renderObjects.push(shade);made++;
 }
 return made;
}
function sourceWetFinishCornerShade(origin,inwardTangent,inwardNormal,h,meta){
 // The specified wet finish already exists as W1/W2/W3. Overlay ONLY a
 // microscopic view-lighting gradient at a source-supported wall-face
 // intersection. This is NOT a fourth wall/edge tile, new grout selection,
 // fabricated partition or extra material quantity. Unmatched returns get
 // neither plane nor shadow.
 if(!(h>.25)||!meta?.source_return_supported||!meta?.native_host_face_id)return;
 const length=.19,off=.018;
 const p0=[origin[0]+inwardNormal[0]*off,origin[1]+inwardNormal[1]*off];
 const p1=[p0[0]+inwardTangent[0]*length,p0[1]+inwardTangent[1]*length];
 const geom=new THREE.BufferGeometry();
 geom.setAttribute('position',new THREE.Float32BufferAttribute([
  p0[0],-h/2,p0[1],p1[0],-h/2,p1[1],
  p1[0],h/2,p1[1],p0[0],h/2,p0[1]],3));
 geom.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,1,0,1,1,0,1],2));
 geom.setIndex([0,1,2,0,2,3]);geom.computeVertexNormals();
 const shade=new THREE.Mesh(geom,sourceWetFinishCornerShadeMaterial);
 shade.position.y=h/2;shade.renderOrder=5;
 shade.raycast=()=>{};
 shade.userData={...meta,category:'ARCH_R063_NATIVE_HOST_FINISH_CORNER_SHADE',
  surfaceIndex:-1,review_return_full_height_ft:h,
  review_return_rendered_height_ft:h,review_return_section_only:false,
  native_face_visual_study:true,new_tile_plane:false,
  material_quantities_unchanged:true,finish_joint_installed_profile:false,
  source:'Viewer-only soft corner contact lighting over selected source-native-wall-supported W2/W3; no additional tile area, verified trim, grout profile or niche placement'};
 modelGroup.add(shade);renderObjects.push(shade);
}
// R069 wet-zone photographic reveal: every strip is a child of an ALREADY
// SOURCE-HOSTED SELECTED W1/W2/W3 plane. It cannot float if the plane is
// hidden by a section, and it cannot create a shower/tub body in the Bath3
// UNSELECTED branch or at TX4's selected-but-UNLOCATED bathtub.
let r069WetJunctionMat=null;
function r069WetJunctionOpticalMaterial(){
 if(r069WetJunctionMat)return r069WetJunctionMat;
 const c=document.createElement('canvas');c.width=64;c.height=256;
 const g=c.getContext('2d'),im=g.createImageData(c.width,c.height);
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){
  const t=y/(c.height-1),edge=Math.pow(1-Math.min(x,63-x)/31.5,3.1);
  const contact=Math.pow(t,4.2)*.31+edge*.064;
  const j=(y*c.width+x)*4;
  im.data[j]=20;im.data[j+1]=26;im.data[j+2]=29;
  im.data[j+3]=Math.min(110,Math.round(contact*255));
 }
 g.putImageData(im,0,0);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 r069WetJunctionMat=new THREE.MeshBasicMaterial({map:tex,
  transparent:true,depthWrite:false,side:THREE.DoubleSide,
  polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 return r069WetJunctionMat;
}
function drawR069SelectedWetJunctions(room){
 if(!R069_FOCUS.has(room.id))return 0;
 let count=0;
 for(const wall of [...renderObjects]){
  const u=wall.userData||{},g=wall.geometry?.parameters;
  if(u.category!=='FULL_ROOM_WET_WALL'||!u.native_host_face_id||
     !(g?.width>.4&&g?.height>.30))continue;
  // Every optical overlay stays ON the selected wall study, no installed
  // termination or waterproofing strip. Only the first .45ft is modified.
  const bandH=Math.min(.42,g.height-.025);
  const shadow=new THREE.Mesh(new THREE.PlaneGeometry(g.width-.055,bandH),
   r069WetJunctionOpticalMaterial());
  shadow.position.set(0,-g.height/2+bandH/2+.014,.017);
  shadow.renderOrder=7;shadow.raycast=()=>{};
  shadow.userData={category:'ARCH_R069_SELECTED_WET_HOST_JUNCTION',
   room_number:instance()?.room_number,wall:u.wall,
   native_host_face_id:u.native_host_face_id,
   native_host_face_receipt:u.native_host_face_receipt||null,
   original_wall_tile_height_ft:g.height,
   r069_source_hosted:true,r069_parent_selected_finish:true,
   r069_not_an_installed_joint:true,r069_no_additional_area:true,
   no_curb_drain_slope_roughin_glass:true,
   source:'R069 optical ceramic-to-floor contact on existing selected W1/W2/W3 SOURCE-NATIVE-HOSTED plane; does NOT add surface area, floor trim, waterproofing, caulk, curb, partition, wet branch selection or construction dimensions.'};
  wall.add(shadow);renderObjects.push(shadow);count++;
 }
 return count;
}
// R069 Wet Zone Study is independent of Full Bathroom/native wall assignment.
// Its known W1/W2/W3 dimensions are drawing-derived, not verified in-room
// installation points. Soft floor-wall ambient contact is attached to the
// EXISTING schematic selected-material planes, creating no 3D shower curb,
// niche, tub, drain, waterproofing/caulk termination or additional tile.
function drawR069WetStudyOpticalDepth(room){
 if(!(R069_FOCUS.has(room.id)||R070_DRY_FOCUS.has(room.id))||state.mode!=='study')return 0;
 let count=0;
 for(const parent of [...renderObjects]){
  const u=parent.userData||{},g=parent.geometry?.parameters;
  if(u.category!=='sourceWall'||!(g?.width>.5&&g?.height>.6))continue;
  const stripH=Math.min(.83,g.height*.18);
  const shade=new THREE.Mesh(new THREE.PlaneGeometry(g.width-.065,stripH),
    r069WetJunctionOpticalMaterial());
  shade.position.set(0,-g.height/2+stripH/2+.012,.035);
  shade.renderOrder=6;shade.raycast=()=>{};
  shade.userData={category:R070_DRY_FOCUS.has(room.id)?
   'ARCH_R070_DRAWING_WET_DEPTH':'ARCH_R069_DRAWING_WET_STUDY_DEPTH',
   room_number:instance()?.room_number,wall:u.wall,
   drawing_width_ft:g.width,drawing_height_ft:g.height,
   parent_existing_selected_study_wall:true,
   verified_native_host:false,installed_wall_finish_location_verified:false,
   added_tile_area_sf:0,drain_or_pan_installed:false,
   no_shower_tub_glazing_niche_or_fixture_created:true,
   source:'Photographic floor-to-wall light falloff parented to existing drawing-dimensioned W1/W2/W3 wet zone MATERIAL study; not Revit native wet surface, installed wet-zone layout, new wall, drain, pan or tile area.'};
  parent.add(shade);renderObjects.push(shade);count++;
 }
 return count;
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
// R070 photographic SURFACE RESPONSE, never a construction assembly:
// wood floor grain/raking light stays on the original native-derived room
// footprint, while plaster/contact gradients stay children of their ORIGINAL
// wall segment. Consequently camera-facing sections/hosted opening gaps and
// 310 adjacency cannot leave new orphaned/incorrectly attributed partitions.
let r070DryPlasterPhoto=null,r070DryCornerPhoto=null;
function r070DryPhotoMaterial(edgeOnly=false){
 if(edgeOnly&&r070DryCornerPhoto)return r070DryCornerPhoto;
 if(!edgeOnly&&r070DryPlasterPhoto)return r070DryPlasterPhoto;
 const c=document.createElement('canvas');c.width=128;c.height=256;
 const g=c.getContext('2d'),p=g.createImageData(c.width,c.height);
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){
  const u=x/127,v=y/255;
  const corner=Math.pow(1-Math.min(u,1-u)*2,2.5);
  const foot=Math.pow(v,3.0);
  const upper=Math.pow(1-v,4.8);
  const a=edgeOnly?.27*corner*(.44+foot*.45):
   .052+.065*corner+.082*foot+.017*upper;
  const j=(y*128+x)*4;
  p.data[j]=edgeOnly?24:41;p.data[j+1]=edgeOnly?31:36;
  p.data[j+2]=edgeOnly?34:32;p.data[j+3]=Math.min(110,Math.round(a*255));
 }
 g.putImageData(p,0,0);
 const texture=new THREE.CanvasTexture(c);
 texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=8;
 const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,
  depthWrite:false,depthTest:true,side:THREE.DoubleSide,
  polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 if(edgeOnly)r070DryCornerPhoto=material;else r070DryPlasterPhoto=material;
 return material;
}
function drawR070RetainedWoodOptical(floor,shape,arch){
 if(!R070_DRY_FOCUS.has(current()?.id)||!current()?.program?.dry_floor_retained)return 0;
 // Fully coincident floor-shape footprint, 0 area/level change. A faint
 // varnish light veil catches the raking normal texture on the SAME source
 // wood preview. No board boundaries, thresholds or selected species.
 const overlay=new THREE.Mesh(new THREE.ShapeGeometry(shape),
  new THREE.MeshPhysicalMaterial({color:0xd9b48c,roughness:.43,
   metalness:0,clearcoat:.22,clearcoatRoughness:.34,
   transparent:true,opacity:.058,side:THREE.DoubleSide,depthWrite:false,
   polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}));
 overlay.rotation.x=-Math.PI/2;overlay.position.y=.021;
 overlay.userData={category:'ARCH_R070_WOOD_FLOOR_MICRORELIEF',
  native_wall_face_polygon:true,named_room_assignment_inferred:true,
  room_number:instance()?.room_number,
  r070_parent_source_floor:true,source_floor_area_addition_sf:0,
  not_extra_wood_layer_or_plank_layout:true,selected_floor_sku:null,
  source:'R070 photographic varnish/light on EXACT original native-wall-face-derived dry retained-WOOD plan polygon; NOT installed floor, added finish layer, board size/direction/species/takeoff or approved product.'};
 modelGroup.add(overlay);renderObjects.push(overlay);
 floor.userData.r070_retained_wood_grain_normal_study=true;
 floor.userData.r070_no_invented_floor_sku=true;
 return 1;
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
  chosenFloor?registeredFloorMaterial(chosenFloor):neutral.flooring;
 const floor=new THREE.Mesh(new THREE.ShapeGeometry(shape),floorMaterial);
 floor.rotation.x=-Math.PI/2;floor.position.y=adjacent ? .011 : .018;
 floor.receiveShadow=true;floor.castShadow=false;
 floor.userData={category:adjacent?'ARCH_ADJACENT_FLOOR':'ARCH_REGISTERED_FLOOR',surfaceIndex:floorIdx,
  source:'NATIVE REVIT WALL FACE-DERIVED POLYGON; NAME drawing-inferred, NOT certified Room element',
  room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
  floor_area_not_a_purchase_quantity:true,
  r063_source_floor_uv_kind:'PLANAR_SOURCE_FEET_NOT_NORMALIZED',
  r063_nominal_tile_size_ft:chosenFloor?normalizeSize(chosenFloor.size).sort((a,b)=>b-a):null,
  r063_map_repeat_per_source_ft:chosenFloor?floorMaterial.userData.repeat_per_source_ft:null,
  r063_floor_material_selected:!!chosenFloor};
 modelGroup.add(floor);renderObjects.push(floor);
 if(!adjacent)drawR070RetainedWoodOptical(floor,shape,arch);
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
 // R059: only when an independently accepted native GWB AABB underside
 // exists, offer an OPTIONAL ghost canopy at that exact Z elevation. The
 // canopy is CLIPPED TO THE DRAWING-REGISTERED WALL-FACE POLYGON; it is not
 // a native ceiling cut profile, floor/roof slab, light or built soffit.
 // Default OFF: owner sees the bathroom, not an opaque artificial roof.
 if(ceilingEvidence?.id&&Number.isFinite(ceilingY)){
  const canopy=new THREE.Mesh(new THREE.ShapeGeometry(shape),
   new THREE.MeshPhysicalMaterial({color:adjacent?0xb6c3c6:0xe3d8c8,
    side:THREE.DoubleSide,roughness:.82,transparent:true,
    opacity:adjacent?.11:.18,depthWrite:false}));
  canopy.rotation.x=-Math.PI/2;
  canopy.position.y=ceilingY-.018;
  canopy.visible=false;
  canopy.userData={
   category:'ARCH_R059_DERIVED_GWB_CEILING_CANOPY',surfaceIndex:-1,
   room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
   source:'ACTUAL independently matched read-only GWB underside ELEVATION + wall-face drawing-inferred XY clipped silhouette. NOT Revit GWB trimmed profile, native Room ceiling, slab, soffit, lighting or approved assembly',
   native_ceiling_id:ceilingEvidence.id,native_ceiling_receipt:ceilingEvidence.receipt_id,
   height_ft:ceilingY,derived_xy_only:true,not_native_ceiling_solid:true,
   parent_compartment:adjacent?'310_CONTEXT':'MAIN'};
  modelGroup.add(canopy);renderObjects.push(canopy);
 }
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
 // Actual DOOR source family AABB and the nominal hosted opening are
 // independent evidence layers. The native family box may contain symbolic
 // swing extents; it is NOT the actual hinge arc, clear opening or leaf solid.
 for(const door of openings||[]){
  if(door.kind!=='door')continue;
  drawNativeDoorAABBWitness(door.native_door_family_aabb,
   adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number);
 }
 // The ACTUAL native WINDOW category AABB is kept independent from the
 // nominal hosted-opening/transparent glazing illustration. Both may differ
 // materially. Preserve separate 310 source window attribution rather than
 // assigning the neighboring 310 element to 311 wet-room construction.
 for(const window of openings||[]){
  if(window.kind!=='window')continue;
  drawNativeWindowAABBWitness(window.native_window_family_aabb,
   adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number);
 }
 const h=ceilingY;
  const dryOrInheritedWC=room.program?.dry_floor_retained===true||room.program?.kind==='WC_PRIMARY_INHERITED';
 const primaryNeutral=!adjacent&&room.program?.kind==='PRIMARY_WALK_IN_LINEAR';
 const r070Dry=!adjacent&&R070_DRY_FOCUS.has(room.id);
 const wallMat=adjacent?new THREE.MeshPhysicalMaterial({color:0x93a6ad,roughness:.86,transparent:true,opacity:.20,
  side:THREE.DoubleSide,depthWrite:false}):
   new THREE.MeshPhysicalMaterial({color:primaryNeutral?0xe3dbd0:dryOrInheritedWC?0xded6ca:0xddd5ca,
   roughness:primaryNeutral?.87:r070Dry?.78:dryOrInheritedWC?.92:.89,
   normalMap:neutralWallPlasterNormal,
   normalScale:r070Dry?new THREE.Vector2(.31,.30):new THREE.Vector2(.21,.21),
   metalness:0,transparent:true,
   opacity:primaryNeutral?.94:dryOrInheritedWC?.89:.87,
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
   const geometry=new THREE.BoxGeometry(to-from,y1-y0,th);
   if(!adjacent){
    // Per-piece BoxGeometry UVs are normalized. Convert them to FEET/2ft,
    // so the single neutral material normal map does not stretch grain
    // differently over 2ft door jambs and 10ft full source wall lengths.
    const uv=geometry.getAttribute('uv');
    const uFt=Math.max(.06,(to-from)/2),vFt=Math.max(.06,(y1-y0)/2);
    for(let k=0;k<uv.count;k++)uv.setXY(k,uv.getX(k)*uFt,uv.getY(k)*vFt);
    uv.needsUpdate=true;
   }
   const mesh=new THREE.Mesh(geometry,wallMat);
   const t=(from+to)/2-len/2;
   mesh.position.set(wallX+ux*t,(y0+y1)/2,wallZ+uz*t);mesh.rotation.y=rot;
   mesh.castShadow=false;mesh.receiveShadow=false;
   mesh.userData={category:'ARCH_REGISTERED_WALL',surfaceIndex:-1,revit_id:seg.id,
    receipt_id:seg.receipt_id,thickness_ft:th,height_from_native_bounds_ft:seg.height_ft,
    visual_cutaway_height_ft:visualH,type_name:seg.type_name,
    review_compartment:adjacent?'ADJACENT':'MAIN',
    review_face_midpoint_xz_ft:[midX,midZ],
    review_outward_xz:[nx*outSign,nz*outSign],
    review_original_y_center_ft:(y0+y1)/2,review_original_bottom_ft:y0,
    review_original_top_ft:y1,review_rendered_top_ft:y1,
    review_cutaway_only:false,review_source_native_geometry_unchanged:true,
    r065_neutral_plaster_display_only:!adjacent,
    r065_plaster_microtexture:!adjacent,
    r065_plaster_uv_ft_per_repeat:2,
    r065_wall_thickness_geometry_unchanged:true,
    r065_illustrative_finish_not_revit_material:true,
    native_location:{start:seg.native_location_start_ft,end:seg.native_location_end_ft},
    ...archSource};
   modelGroup.add(mesh);renderObjects.push(mesh);walls++;
   if(!adjacent&&(R068_WET_FOCUS.has(room.id)||R069_FOCUS.has(room.id))){
    const inset=new THREE.Mesh(new THREE.PlaneGeometry(
     Math.max(.04,to-from-.015),Math.max(.04,y1-y0-.015)),
     r068SourceWallLightMaterial());
    // R043 native wall's local +Z = native signed perpendicular to its
    // source location line. Put the optical gradient at its INTERIOR source
    // face and parent it to the native wall mesh (auto-section/hide).
    inset.position.z=-outSign*(th/2+.011);
    inset.userData={category:R069_FOCUS.has(room.id)?
       'ARCH_R069_SOURCE_NATIVE_LIGHT':'ARCH_R068_NATIVE_WALL_DEPTH_LIGHT',
     revit_id:seg.id,receipt_id:seg.receipt_id,room_number:instance()?.room_number,
     r068_parent_wall_id:seg.id,source_wall_span_ft:to-from,
     source_wall_height_ft:y1-y0,source_wall_thickness_ft:th,
     source_wall_inner_face_only:true,not_additional_wall_solid:true,
     not_selected_wall_material:true,actual_wall_dimensions_unchanged:true,
     selected_tile_coverage_area_ft2:null,
     source:'Photographic neutral corner/foot ambient light on actual native wall-box INSIDE face; follows existing wall cutaway/visibility. No new wall, selected plaster, trim, ceiling, wet enclosure, product or added area.',
     r069_wall_face_source_supported:R069_FOCUS.has(room.id),
     r069_reversible_parent_source_wall:true};
    mesh.add(inset);renderObjects.push(inset);
   }
   if(r070Dry){
    const faceZ=-outSign*(th/2+.014);
    // Source wall pieces already split at actual hosted doors/windows.
    // Both optical layers are CHILDREN of these same pieces, so 1.12/2.35ft
    // reversible sections and nominal openings remain identical.
    const glow=new THREE.Mesh(new THREE.PlaneGeometry(
     Math.max(.035,to-from-.022),Math.max(.035,y1-y0-.022)),
     r070DryPhotoMaterial(false));
    glow.position.z=faceZ;glow.renderOrder=5;glow.raycast=()=>{};
    glow.userData={category:'ARCH_R070_PLASTER_FACE_STUDY',
     revit_id:seg.id,receipt_id:seg.receipt_id,
     room_number:instance()?.room_number,
     native_source_wall_id:seg.id,real_native_wall_thickness_ft:th,
     source_wall_run_ft:to-from,source_wall_height_ft:y1-y0,
     native_hosted_openings_already_cut:true,source_wall_unchanged:true,
     not_a_selected_paint_or_new_wall:true,
     source:'R070 photographic gypsum/plaster tonal falloff on ORIGINAL native wall-box interior face only; parented to reversible source section, not a new wall, architectural reveal, selected paint, baseboard or ceiling.'};
    mesh.add(glow);renderObjects.push(glow);
    for(const s of [-1,1]){
     const corner=new THREE.Mesh(new THREE.PlaneGeometry(
      Math.min(.16,Math.max(.041,(to-from)*.10)),
      Math.max(.035,y1-y0-.035)),r070DryPhotoMaterial(true));
     corner.position.set(s*((to-from)/2-Math.min(.085,(to-from)*.055)),
      0,faceZ+.004*(-outSign));
     corner.renderOrder=6;corner.raycast=()=>{};
     corner.userData={category:'ARCH_R070_CORNER_DEPTH_STUDY',
      revit_id:seg.id,receipt_id:seg.receipt_id,
      room_number:instance()?.room_number,source_wall_span_ft:to-from,
      source_wall_thickness_ft:th,
      optical_only:true,not_new_return_or_joint:true,selected_product:null,
      native_hosted_opening_excluded:true,reversible_with_source_wall:true,
      source:'Thin corner ambient-shadow PHOTO region INSIDE actual native wall-run and parented to existing hosted-gap wall piece. NOT a return wall, trim, grout, caulk, waterproofing or installed architectural component.'};
     mesh.add(corner);renderObjects.push(corner);
    }
   }
   if(!adjacent&&y0<.001&&to-from>.18){
    // Exact source-wall line station and polygon winding define a wholly
    // INTERIOR visual contact ribbon. Only show beneath physical wall runs;
    // door/window open portions are individually omitted in wallBox calls.
    const depth=.31,sideX=-nx*outSign,sideZ=-nz*outSign;
    const q0=[a[0]+ux*from,a[1]+uz*from],q1=[a[0]+ux*to,a[1]+uz*to];
    const coords=[q0[0],.031,q0[1],q1[0],.031,q1[1],
     q1[0]+sideX*depth,.031,q1[1]+sideZ*depth,
     q0[0]+sideX*depth,.031,q0[1]+sideZ*depth];
    const geom=new THREE.BufferGeometry();
    geom.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));
    geom.setAttribute('uv',new THREE.Float32BufferAttribute([0,1,1,1,1,0,0,0],2));
    geom.setIndex([0,1,2,0,2,3]);geom.computeVertexNormals();
    const ao=new THREE.Mesh(geom,sourceWallContactAO);ao.renderOrder=4;
    ao.userData={category:'ARCH_R063_SOURCE_WALL_FOOT_CONTACT_LIGHT',
     revit_id:seg.id,receipt_id:seg.receipt_id,
     source_wall_face_segment:[q0,q1],depth_visual_ft:depth,
     source_bounded_to_actual_wall_run:true,
     actual_floor_area_ft2:null,quantity_added:false,installed_baseboard:false,
     source:'VIEWER ONLY ambient contact gradient tied to actual native wall-box spans (hosted-opening gaps excluded), not a baseboard, waterproofing, tile trim or construction material'};
    modelGroup.add(ao);renderObjects.push(ao);
   }
   if(y1>2.35+.05){
    // Transparent UPPER REMNANT of the old visualization span keeps the
    // original source-wall relationship legible in R057's camera-facing
    // section. It is NOT real glazing, native geometry, a design or demolition.
    const ghost=new THREE.Mesh(new THREE.BoxGeometry(to-from,1,th),
     new THREE.MeshBasicMaterial({color:0x91b3c2,transparent:true,
      opacity:.075,side:THREE.DoubleSide,depthWrite:false,depthTest:true}));
    ghost.position.copy(mesh.position);ghost.rotation.y=rot;ghost.visible=false;
    ghost.userData={category:'ARCH_VISUAL_CUTAWAY_UPPER_REMNANT',surfaceIndex:-1,
     revit_id:seg.id,receipt_id:seg.receipt_id,
     source:'R058 CAMERA-FACING SECTION PRESENTATION ONLY; source wall span stays separately recorded; transparent upper region NOT an actual material or Revit family solid',
     original_source_wall_height_ft:seg.height_ft,
     source_visual_wall_top_ft:y1,not_family_solid:true,visual_section_only:true};
    mesh.userData.review_ghost=ghost;
    modelGroup.add(ghost);renderObjects.push(ghost);
   }
  }
  let cursor=0;
  for(const cut of cuts){
   wallBox(cursor,cut.start,0,visualH);
   const head=visualH,openingHeight=cut.opening.nominal_height_ft;
   const sill=cut.opening.kind==='window'?Math.max(0,cut.opening.sill_height_ft||0):0;
   // The family NOMINAL opening may extend beyond a drawing-inferred face
   // segment or beyond this viewer's shortened wall cutaway. Keep the real
   // visual extent distinct from the nominal type dimensions in all metadata.
   const station=(cut.opening.location_local_ft[0]-a[0])*ux+
    (cut.opening.location_local_ft[1]-a[1])*uz;
   const nominalStart=station-cut.opening.nominal_width_ft/2;
   const nominalEnd=station+cut.opening.nominal_width_ft/2;
   const renderedWidth=cut.end-cut.start;
   const clippedByInferredFace=cut.start>nominalStart+.002||cut.end<nominalEnd-.002;
   const edgeY=Math.max(sill,Math.min(head,sill+openingHeight));
   const renderedHeight=edgeY-sill;
   const clippedByVisualCutaway=renderedHeight<openingHeight-.002;
   const visualClass=(clippedByVisualCutaway||clippedByInferredFace)?
    'VISUALLY_CLIPPED':'NOMINAL_SPAN_WITHIN_SOURCE_FACE';
   const displayedSpan={nominal_width_ft:cut.opening.nominal_width_ft,
    nominal_height_ft:openingHeight,rendered_width_ft:renderedWidth,
    rendered_height_ft:renderedHeight,
    clipped_by_visual_cutaway:clippedByVisualCutaway,
    clipped_by_inferred_face:clippedByInferredFace,
    visual_classification:visualClass,
    unresolved_nominal_width_ft:Math.max(0,cut.opening.nominal_width_ft-renderedWidth),
    unresolved_nominal_height_ft:Math.max(0,openingHeight-renderedHeight)};
   if(sill>0)wallBox(cut.start,cut.end,0,sill);
   if(head>sill+openingHeight)wallBox(cut.start,cut.end,sill+openingHeight,head);
   const mid=(cut.start+cut.end)/2-len/2;
   const isWindow=cut.opening.kind==='window';
   const doorLeaf=new THREE.Mesh(new THREE.BoxGeometry(cut.end-cut.start,Math.max(.05,Math.min(openingHeight,head-sill)),isWindow?.05:.105),
    isWindow?neutral.glass:neutral.contextualDoor);
   doorLeaf.position.set(wallX+ux*mid,sill+Math.max(.05,Math.min(openingHeight,head-sill))/2,wallZ+uz*mid);
   doorLeaf.rotation.y=rot;doorLeaf.castShadow=false;
   doorLeaf.userData={category:isWindow?'ARCH_HOSTED_WINDOW':'ARCH_HOSTED_DOOR_LEAF',revit_id:cut.opening.id,
    receipt_id:cut.opening.receipt_id,host_id:seg.id,...displayedSpan,
    review_face_midpoint_xz_ft:[midX,midZ],
    review_outward_xz:[nx*outSign,nz*outSign],review_visual_hidden_only:false,
    swing:isWindow?'NOT APPLICABLE':'UNKNOWN (neutral closed-plane depiction)',
    source:cut.opening.source+' VISUALLY_CLIPPED when shown dimensions differ from nominal; NOT actual leaf/window family geometry'};
   modelGroup.add(doorLeaf);renderObjects.push(doorLeaf);doors++;
   // R062 source-thickness wall REVEAL visualization. These are not jamb
   // stock, door frames, window trim, native opening profiles, or fabricated
   // rough openings. Their STATION/visible width comes from the clipped
   // NOMINAL hosted element; their transverse DEPTH from original native
   // host thickness. No hinge, handing or glazing pattern is constructed.
   const revealMat=new THREE.MeshPhysicalMaterial({color:0xe1d9cf,
    roughness:.88,metalness:0,side:THREE.DoubleSide});
   const revealH=Math.max(0,edgeY-sill);
   const revealDepth=Math.max(.045,th-.015);
   const baseReveal={category:'ARCH_R062_NATIVE_HOST_REVEAL_VISUAL',surfaceIndex:-1,
    revit_id:cut.opening.id,host_id:seg.id,receipt_id:cut.opening.receipt_id,
    source_wall_receipt_id:seg.receipt_id,
    native_host_thickness_ft:th,
    nominal_width_ft:cut.opening.nominal_width_ft,
    nominal_height_ft:cut.opening.nominal_height_ft,
    rendered_width_ft:renderedWidth,
    rendered_height_ft:renderedHeight,
    clipped_by_visual_cutaway:clippedByVisualCutaway,
    clipped_by_inferred_face:clippedByInferredFace,
    visual_classification:visualClass,
    not_swing_or_rough_opening:true,
    native_room_membership_certified:false,
    review_outward_xz:[nx*outSign,nz*outSign],
    review_face_midpoint_xz_ft:[midX,midZ],
    source:'SOURCE-native host-wall bounded depth, drawing-inferred wall-face and NOMINAL clipped opening station; zero verified jamb/frame stock, true reveal construction, hinge, glazing or rough opening'};
   const appendReveal=(geo,station,y,part)=>{
    const obj=new THREE.Mesh(geo,revealMat);
    obj.position.set(wallX+ux*(station-len/2),y,
      wallZ+uz*(station-len/2));
    obj.rotation.y=rot;obj.castShadow=false;obj.receiveShadow=true;
    obj.userData={...baseReveal,review_reveal_part:part,
     opening_station_ft:station,source_bounded_display_only:true};
    modelGroup.add(obj);renderObjects.push(obj);
   };
   if(revealH>.18&&renderedWidth>.1){
    for(const [station,part] of [[cut.start,'JAMB_STATION_A'],[cut.end,'JAMB_STATION_B']])
     appendReveal(new THREE.BoxGeometry(.028,revealH,revealDepth),station,
      sill+revealH/2,part);
    // Only show a visible HEADER underside when actual native-derived wall
    // remains above the NOMINAL cut: do NOT fabricate a 3ft cutaway header.
    if(head>edgeY+.045)appendReveal(new THREE.BoxGeometry(renderedWidth,.025,revealDepth),
     (cut.start+cut.end)/2,edgeY,'WALL_HEAD_UNDERSIDE');
    if(isWindow&&sill>.04)appendReveal(new THREE.BoxGeometry(renderedWidth,.025,revealDepth),
     (cut.start+cut.end)/2,sill,'WALL_SILL_RETURN');
   }
   // Native host and nominal family width establish an opening station,
   // but NOT a construction rough opening or door handing. Trace the two
   // nominal jamb stations and visible head/sill with zero-thickness lines;
   // never fabricate a frame stock dimension or a swing arc.
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
    ...displayedSpan,
    source:'NATIVE HOST + NOMINAL FAMILY DIMENSIONS; rendered span can be VISUALLY_CLIPPED by view cutaway or inferred face. NOT frame, rough opening, hinge, threshold or swing'};
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
   // Independent extents measured from the actual wire vertices, in the wall
   // tangent and local Y coordinates, to expose/test 3D visible geometry.
   const along=revealPts.map(p=>(p.x-wallX)*ux+(p.z-wallZ)*uz);
   const elevations=revealPts.map(p=>p.y);
   const physicalWidth=Math.max(...along)-Math.min(...along);
   const physicalHeight=Math.max(...elevations)-Math.min(...elevations);
   const reveal=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(revealPts),
    new THREE.LineBasicMaterial({color:isWindow?0x9dc8d0:0x9ab9b3,
     transparent:true,opacity:.43,depthTest:false}));
   reveal.renderOrder=12;
   reveal.userData={category:'ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS',
    room_number:adjacent?arch.adjacent_zone_geometry.number:instance()?.room_number,
    revit_id:cut.opening.id,host_id:seg.id,
    receipt_id:cut.opening.receipt_id,host_wall_receipt_id:seg.receipt_id,
    native_host_thickness_ft:th,...displayedSpan,
    geometry_rendered_width_ft:physicalWidth,
    geometry_rendered_height_ft:physicalHeight,
    source:'REAL Revit host bounded thickness and insertion with NOMINAL family dimensions; 3D rendered spans can be VISUALLY_CLIPPED by cutaway/ceiling or inferred wall-face endpoints (e.g. 007A). Missing nominal width/height is UNRESOLVED, NOT fabricated to meet type dimension. OPENING DEPTH WIRES ONLY, NOT rough opening, actual jamb, glazing, sill, hinge or swing'};
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
function drawNativeWindowAABBWitness(bounds,roomNumber){
 const lo=bounds?.min_local_xyz_ft,hi=bounds?.max_local_xyz_ft;
 if(!lo||!hi||lo.length!==3||hi.length!==3)return false;
 const w=hi[0]-lo[0],h=hi[1]-lo[1],d=hi[2]-lo[2];
 if(!(w>.2&&h>.2&&d>.2&&w<16&&h<15&&d<16))return false;
 // SOURCE element AABB is not a glass pane or window frame mesh; it may
 // include family symbolic extensions beyond type NOMINAL width and height.
 // Sparse purple/blue dashed bounds provide a trustworthy envelope without
 // creating non-native window grid, glazing mullions, sill/rough-opening stock.
 const geometry=new THREE.BoxGeometry(w,h,d);
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geometry),
  new THREE.LineDashedMaterial({color:0x9f9bd2,dashSize:.19,gapSize:.13,
   transparent:true,opacity:.68,depthTest:false}));
 edges.position.set((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);
 edges.computeLineDistances();edges.renderOrder=11;
 edges.userData={category:'ARCH_NATIVE_WINDOW_FAMILY_AABB_WITNESS',
  room_number:roomNumber,revit_id:bounds.revit_id,host_id:bounds.host_id,
  receipt_id:bounds.receipt_id,native_bounds_ft:bounds.bounds_native_ft,
  native_aabb_dimensions_ft:[w,h,d],
  not_family_solid:true,not_glazing_or_rough_opening:true,
  source:bounds.confidence};
 modelGroup.add(edges);renderObjects.push(edges);
 return true;
}
function drawNativeDoorAABBWitness(bounds,roomNumber){
 const lo=bounds?.min_local_xyz_ft,hi=bounds?.max_local_xyz_ft;
 if(!lo||!hi||lo.length!==3||hi.length!==3)return false;
 const w=hi[0]-lo[0],h=hi[1]-lo[1],d=hi[2]-lo[2];
 if(!(w>.1&&h>.5&&d>.1&&w<12&&h<15&&d<12))return false;
 const edges=new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(w,h,d)),
  new THREE.LineDashedMaterial({color:0xd3b083,dashSize:.13,gapSize:.11,
   transparent:true,opacity:.55,depthTest:false}));
 edges.position.set((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);
 edges.computeLineDistances();edges.renderOrder=10;
 edges.userData={category:'ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS',
  room_number:roomNumber,revit_id:bounds.revit_id,host_id:bounds.host_id,
  receipt_id:bounds.receipt_id,native_bounds_ft:bounds.bounds_native_ft,
  native_aabb_dimensions_ft:[w,h,d],not_family_solid:true,
  not_swing_or_rough_opening:true,source:bounds.confidence};
 modelGroup.add(edges);renderObjects.push(edges);
 return true;
}
function drawPH4AdjacentNativeFixtures(arch,side){
 const z=arch.adjacent_zone_geometry;
 const items=z?.native_fixture_evidence||[];
 const map=new Map(items.map(x=>[x.kind,x]));
 // Nov-07 A2.2 calls 310A WIC 4 and 310B BATH 4. The READ-ONLY native
 // fixture-neighborhood dataset contains toilet and lavatory candidates in
 // BOTH bands. It does NOT verify OST_Rooms membership. For WIC 310A, do not
 // display a generic toilet/sink/cabinet as actual closet contents merely
 // because those Revit elements are nearby. Keep their native category
 // witnesses available with Source traces ON. 310B is a drawn bathroom and
 // can retain its conservatively classified illustrative fixtures.
 const representedBathroom=side==='B';
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
  if(representedBathroom){
   const sign=1; // 310B west half; source-native projection remains illustrative
   const x=p[0]+sign*1.03;
   drawNativeFixtureOffsetWitness(p,[x,p[1]],toilet.id,toilet.receipt_id,'310'+side);
   const fixture=drawPlanFixtureSymbol('toilet',x,p[1],-Math.PI/2,{
    room_number:'310'+side,native_anchor_id:toilet.id,native_anchor_receipt_id:toilet.receipt_id,
    native_anchor_coordinate_ft:toilet.native_insertion_ft,illustrative_offset_from_anchor_ft:1.03});
   if(fixture)fixture.userData={context:'310'+side,confidence:'Native plumbing insertion in drawing-named 310B bath; 1.03ft generic offset, not native family or plumbing rough-in'};
  }
 }
 const countertop=map.get('countertop');
 if(countertop?.bounds_native_ft){
  const bb=countertop.bounds_native_ft;
  const width=bb.max[0]-bb.min[0],depth=bb.max[1]-bb.min[1];
  const minY=Math.max(0,bb.min[2]-arch.native_level_elevation_ft),
   maxY=Math.min(9.25,bb.max[2]-arch.native_level_elevation_ft);
  if(width>.6&&depth>.6&&maxY>minY){
   if(!representedBathroom){
    const x=(bb.max[0]+bb.min[0])/2-arch.origin_native_xy_ft[0],
     zz=arch.origin_native_xy_ft[1]-(bb.max[1]+bb.min[1])/2;
    const wires=new THREE.LineSegments(
     new THREE.EdgesGeometry(new THREE.BoxGeometry(width,maxY-minY,depth)),
     new THREE.LineDashedMaterial({color:0xc8b092,dashSize:.17,gapSize:.12,
       transparent:true,opacity:.58,depthTest:false}));
    wires.position.set(x,(maxY+minY)/2,zz);
    wires.computeLineDistances();wires.visible=false;
    wires.userData={category:'ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS',
     revit_id:countertop.id,receipt_id:countertop.receipt_id,room_number:'310A',
     native_bounds_ft:bb,not_family_solid:true,
     source:'Actual source-native casework AABB in 310A vicinity, while Nov-07 drawing calls 310A WIC4. OST_Rooms membership UNVERIFIED; do not display a cabinet/sink in the closet as constructed.'};
    modelGroup.add(wires);renderObjects.push(wires);
   }else{
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
   // Reviewer97 R069 FINAL FIX: the previous 310B photographic lid
   // straddled native category maxY by +0.095ft (1.14in). Keep this
   // generic light-only top STRICTLY inside its own native Countertop
   // AABB, without claiming an installed slab thickness or basin opening.
   const lidH=Math.min(.09,maxY-minY);
   const top=new THREE.Mesh(new THREE.BoxGeometry(width,lidH,depth),
    new THREE.MeshPhysicalMaterial({color:0xdbd9d1,roughness:.28,clearcoat:.18,
     transparent:true,opacity:.80}));
   top.position.set(x,maxY-lidH/2,zz);
   top.userData={...mesh.userData,category:'ARCH_R070_310B_NATIVE_BOUNDED_LID',
    strictly_within_native_countertop_xyz:true,native_max_y_ft:maxY,
    native_min_y_ft:minY,visual_top_y_ft:maxY,visual_bottom_y_ft:maxY-lidH,
    not_manufacturer_solid:true,no_basin_cutout:true,
    source:'Viewer-only neutral 310B top light VOLUME INSIDE exact native Countertop-category AABB; corrects Reviewer97 +0.095ft top overshoot. Neither installed stone shape nor source fixture approval.'};
   modelGroup.add(top);renderObjects.push(top);
   }
  }
 }
 const lav=map.get('lavatory_reference');
 if(lav){
  const p=lav.location_local_xz_ft;
  const locator=new THREE.Mesh(new THREE.RingGeometry(.10,.18,28),
   new THREE.MeshBasicMaterial({color:0xb6dfec,side:THREE.DoubleSide,transparent:true,opacity:.8,depthWrite:false}));
  locator.rotation.x=-Math.PI/2;locator.position.set(p[0],3.16,p[1]);
  locator.visible=state.sourceTraces;
  locator.userData={category:'ARCH_NATIVE_FIXTURE_2D_LOCATOR',surfaceIndex:-1,revit_id:lav.id,
   receipt_id:lav.receipt_id,context:'310'+side,
   source:side==='A'?
    'READ-ONLY vicinity candidate near drawing-labeled 310A WIC4, spatial attribution NOT VERIFIED; no basin, cabinet or bathtub depiction':
    'Actual lavatory-associated native insertion in drawing-labeled 310B Bath4, family identification and solid NOT CERTIFIED'};
  modelGroup.add(locator);renderObjects.push(locator);
 }
}
// R067: photographic LIGHT/SHAPE STUDIES of three dry powder countertop
// CATEGORY AABBs, never native countertop family geometry. All six sides of
// every added feature remain INSIDE that particular source object's X/Y/Z
// envelope. In particular 102A/B has a .125ft TOP SLAB ONLY; no lower vanity
// panels, floor pedestal, manufactured edge or supports can be inferred.
function drawR067PowderCounterFacets(item,room,x,zz,w,d,z0,z1,visualTopH,arch){
 if(!['PH-POWDER','TX-POWDER','TX-POWDER2'].includes(room.id))return 0;
 const span=z1-z0,thin=span<=.16,longZ=d>w,poly=arch?.floor_polygon_local_xz_ft||[];
 const xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
 const out=longZ?
  (Math.abs(x-Math.min(...xs))<Math.abs(x-Math.max(...xs))?1:-1):
  (Math.abs(zz-Math.min(...zs))<Math.abs(zz-Math.max(...zs))?1:-1);
 const bounds=[x-w/2,x+w/2,z0,z1,zz-d/2,zz+d/2];
 let drawn=0;
 function facet(category,geometry,position,material,part){
  const mesh=new THREE.Mesh(geometry,material);
  mesh.position.set(...position);mesh.receiveShadow=true;
  mesh.userData={category,surfaceIndex:-1,revit_id:item.id,receipt_id:item.receipt_id,
   room_number:instance()?.room_number,visual_part:part,
   source_native_bounds:item.native_bounds_ft,source_bounds_local_ft:bounds,
   r067_inside_native_category_aabb_xyz:true,not_native_solid:true,
   not_selected_counter_material:true,not_manufactured_edge:true,
   installed_joinery_or_mounting_verified:false,
   no_sink_cutout:true,no_faucet_installation:true,
   source:'R067 neutral photo-lit countertop CATEGORY-AABB volume study, all mesh XYZ within native source bounds; illustrative light catcher ONLY, not installed fabrication thickness/profile, joinery, support, selected stone/wood, basin or faucet.'};
  modelGroup.add(mesh);renderObjects.push(mesh);drawn++;return mesh;
 }
 if(thin){
  // Actual 102A/B elevation interval 2.7083--2.8333ft is retained EXACTLY;
  // shallow neutral edge/underside facets give this isolated source slab a
  // legible physical *visual*, not a fictitious cabinet below its AABB.
  const material=new THREE.MeshPhysicalMaterial({color:0xcfc6bb,metalness:0,
   roughness:.43,clearcoat:.15,clearcoatRoughness:.45,
   transparent:true,opacity:.97,side:THREE.DoubleSide});
  const edgeH=Math.max(.035,Math.min(.075,span-.032)),cy=z0+span*.54;
  for(const sign of [-1,1]){
   facet('ARCH_R067_THIN_COUNTER_LIGHT_EDGE',
    new THREE.BoxGeometry(.024,edgeH,d-.045),
    [x+sign*(w/2-.017),cy,zz],material,'LONG_EDGE_'+sign);
   facet('ARCH_R067_THIN_COUNTER_LIGHT_EDGE',
    new THREE.BoxGeometry(w-.06,edgeH,.024),
    [x,cy,zz+sign*(d/2-.017)],material,'END_EDGE_'+sign);
  }
  facet('ARCH_R067_THIN_COUNTER_LIGHT_EDGE',
   new THREE.BoxGeometry(w-.07,.013,d-.07),[x,z0+.011,zz],
   new THREE.MeshStandardMaterial({color:0x7f7972,roughness:.93,
    transparent:true,opacity:.56,depthWrite:false,side:THREE.DoubleSide}),
   'OPTICAL_UNDERSIDE');
  return drawn;
 }
 // Tall source Countertop CATEGORY volumes (405 / 010) are not thin slabs.
 // Readable *bounded* faces and ambient lower contact only; no cupboard
 // doors, drawers, hardware, floor supports or chosen stone. Face direction
 // follows near side of the source wall-face polygon, not a manufactured front.
 const frontH=Math.min(span-visualTopH-.06,1.72);
 if(frontH<.28)return 0;
 const frontMat=new THREE.MeshPhysicalMaterial({color:0xb8aa98,roughness:.72,
  metalness:0,clearcoat:.06,transparent:true,opacity:.84,
  side:THREE.DoubleSide,depthWrite:false});
 const capMat=new THREE.MeshPhysicalMaterial({color:0xd1c3b2,roughness:.67,
  metalness:0,transparent:true,opacity:.79,
  side:THREE.DoubleSide,depthWrite:false});
 const hY=z0+.026+frontH/2;
 facet('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET',
  new THREE.BoxGeometry(longZ?.024:w-.06,frontH,longZ?d-.06:.024),
  [x+(longZ?out*(w/2-.018):0),hY,zz+(longZ?0:out*(d/2-.018))],
  frontMat,'SOURCE_FACING_NEUTRAL_MASS');
 for(const sign of [-1,1]){
  facet('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET',
   new THREE.BoxGeometry(longZ?w-.08:.027,frontH,longZ?.027:d-.08),
   [x+(longZ?0:sign*(w/2-.020)),hY,zz+(longZ?sign*(d/2-.020):0)],
   capMat,'SOURCE_END_RETURN_'+sign);
 }
 const bandH=Math.min(.068,span*.085),bandY=z1-visualTopH-bandH/2-.008;
 if(bandY-bandH/2>z0+.03)facet('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET',
  new THREE.BoxGeometry(w-.07,bandH,d-.07),[x,bandY,zz],
  new THREE.MeshPhysicalMaterial({color:0xe3d7c8,metalness:0,
   roughness:.48,clearcoat:.12,transparent:true,opacity:.93,
   side:THREE.DoubleSide}), 'UPPER_VOLUME_LIGHT_CATCH');
 facet('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET',
  new THREE.BoxGeometry(w-.09,.02,d-.09),[x,z0+.017,zz],
  new THREE.MeshStandardMaterial({color:0x6d645d,roughness:1,
   transparent:true,opacity:.48,depthWrite:false,side:THREE.DoubleSide}),
  'OPTICAL_LOWER_SHADE');
 return drawn;
}
function drawR070NativeCounterSurfacePhoto(item,room,x,zz,w,d,z0,z1){
 if(!R070_DRY_FOCUS.has(room.id)||room.program?.kind!=='DRY_WOOD')return 0;
 if(!(w>.45&&d>.45&&z1-z0>.08))return 0;
 // Native read-only CATEGORY AABB is the unaltered dimensional limit,
 // including 102A/B's 1.5in thick slab-only program. R070 adds no
 // free-standing supports below it and does not turn an UNSELECTED sink
 // into a drilled counter or selected faucet/mirror.
 const cap=new THREE.Mesh(new THREE.PlaneGeometry(w-.062,d-.062),
  new THREE.MeshPhysicalMaterial({color:0xfff5e7,
   roughness:.19,metalness:0,clearcoat:.48,clearcoatRoughness:.21,
   transparent:true,opacity:.24,side:THREE.DoubleSide,
   depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,
   polygonOffsetUnits:-2}));
 cap.rotation.x=-Math.PI/2;cap.position.set(x,z1-.004,zz);
 cap.renderOrder=7;cap.raycast=()=>{};
 cap.userData={category:'ARCH_R070_NATIVE_COUNTER_SURFACE_STUDY',
  revit_id:item.id,receipt_id:item.receipt_id,
  room_number:instance()?.room_number,
  source_category_xyz_min:[x-w/2,z0,zz-d/2],
  source_category_xyz_max:[x+w/2,z1,zz+d/2],
  r070_native_counter_contained:true,display_surface_y_ft:z1-.004,
  no_basin_cutout_or_faucet:true,no_installation_selection:true,
  no_underslab_pedestal_or_joinery:true,
  source:'Native AABB XYZ-bounded photographic specular catch strictly INSIDE source read-only Countertop category; not actual sink cutout, chosen stone, cabinet solid, tap, hardware, levelling or installation height.'};
 modelGroup.add(cap);renderObjects.push(cap);return 1;
}
// R068: registered Countertop CATEGORY bounds remain the sole dimensional
// envelope of all glossy light catchers. Thin view-only planar illumination
// makes both long primary and compact Bath2 counters legible in a high-end
// interior without manufacturing an imagined sink opening, cabinet, support,
// stone profile or installation height.
function drawR068NativeCounterLight(item,room,x,zz,w,d,z0,z1){
 const r069=R069_FOCUS.has(room.id);
 if(!(R068_WET_FOCUS.has(room.id)||r069)||!(w>1&&d>1&&z1-z0>.38))return 0;
 const longZ=d>w,s=(z1-z0),limit=[x-w/2,x+w/2,z0,z1,zz-d/2,zz+d/2];
 const mat=(color,roughness,opacity)=>new THREE.MeshPhysicalMaterial({
  color,roughness,metalness:0,clearcoat:.31,clearcoatRoughness:.25,
  transparent:true,opacity,side:THREE.DoubleSide,depthWrite:false,
  polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
 let count=0;
 function place(part,g,p,rotation,m){
  const o=new THREE.Mesh(g,m);o.position.set(...p);
  if(rotation)o.rotation.set(...rotation);
  o.renderOrder=6;
  o.userData={category:r069?'ARCH_R069_BOUNDED_CASEWORK_LIGHT':
    'ARCH_R068_SOURCE_COUNTER_LIGHT_REVEAL',
   revit_id:item.id,receipt_id:item.receipt_id,room_number:instance()?.room_number,
   r068_inside_native_countertop_xyz:true,source_bounds_local_ft:limit,
   source_native_bounds_ft:item.native_bounds_ft,r068_part:part,
   r069_within_native_aabb:r069,r069_part:part,
   r069_no_new_cabinet_or_pedestal:true,
   category_aabb_not_manufacturer_solid:true,not_selected_counter_material:true,
   no_basin_cutout:true,no_faucet_or_drawer:true,installed_base_or_support:false,
   actual_material_quantity_ft2:null,
   source:'R068/R069 photographic optical surface at TRUE native Countertop-category XYZ AABB boundary. Light/shadow only; not Revit family solid, installed cabinetry, selected stone, ceramic basin, tapped opening or manufacturer profile. For TX-BATH3, original category begins 0.1667ft BELOW finished floor; no new pedestal fabricated.'};
  modelGroup.add(o);renderObjects.push(o);count++;
 }
 const long=longZ?d:w,short=longZ?w:d;
 // Coincident source category TOP (not above it); polygon offset resolves
 // optical overlay against R066's exact native-maximum-height top visual.
 place('TOP_SATIN_REFLECTANCE',
  new THREE.PlaneGeometry(w-.09,d-.09),[x,z1,zz],[-Math.PI/2,0,0],
  mat(0xf5efe8,.24,.35));
 const height=Math.min(.062,s*.16),y=z1-Math.min(.13,s*.27);
 for(const side of [-1,1]){
  if(longZ){
   place('LONG_SOURCE_BOUNDED_EDGE_'+side,
    new THREE.PlaneGeometry(d-.085,height),[x+side*w/2,y,zz],
    [0,Math.PI/2,0],mat(0xd4c3ac,.30,.74));
  }else{
   place('LONG_SOURCE_BOUNDED_EDGE_'+side,
    new THREE.PlaneGeometry(w-.085,height),[x,y,zz+side*d/2],
    [0,0,0],mat(0xd4c3ac,.30,.74));
  }
 }
 // A soft neutral underside reflector stays within the ORIGINAL category
 // depth. It cannot certify a free-hung vanity or a room-floor support.
 place('SOURCE_BOUNDED_UNDERSIDE_SHADE',
  new THREE.PlaneGeometry(w-.12,d-.12),[x,z0+.001,zz],[-Math.PI/2,0,0],
  mat(0x66594e,.82,.18));
 return count;
}
function drawRegisteredCasework(arch,room){
 const items=arch?.native_casework_proxies||[];
 // Native Revit plumbing membership alone cannot create a picked basin.
 // 102B has a real nearby insertion but its entire powder scheme is NO PICK.
 // 010A/B has a selected deck faucet, yet the basin is still UNSELECTED.
 const basinProgramBlocked=room.id==='TX-POWDER'||
  /basin UNSELECTED|sink UNSELECTED/i.test(room.program?.plumbing_truth||'');
 const hasSelectedBasin=!basinProgramBlocked;
 let drawn=0;
 for(const item of items){
  const w=item.width_x_ft,d=item.depth_z_ft;
  if(!(w>.7&&d>.7))continue;
  const z0=Math.max(0,item.min_height_ft),z1=Math.min(5,item.max_height_ft);
  if(z1<=z0)continue;
  const x=item.local_center_xz_ft[0],zz=item.local_center_xz_ft[1];
   const base=new THREE.Mesh(new THREE.BoxGeometry(w,z1-z0,d),
   new THREE.MeshPhysicalMaterial({color:0xada79d,roughness:.60,metalness:0,
     transparent:true,opacity:room.program?.kind === 'DRY_WOOD' ? .16 : .30,
     side:THREE.DoubleSide,depthWrite:false}));
  base.position.set(x,(z0+z1)/2,zz);
  base.userData={category:'ARCH_NATIVE_CASEWORK_AABB_STUDY',surfaceIndex:-1,
   revit_id:item.id,receipt_id:item.receipt_id,
   source:'READ ONLY Revit category native AABB; not a certified physical cabinet/vanity solid',
   name:'Countertop',room_id:instance()?.room_number,bounds_ft:item.native_bounds_ft,
   room_assignment:'DRAWING INFERRED',material:'UNSELECTED NEUTRAL STUDY'};
  modelGroup.add(base);renderObjects.push(base);
  // The source AABB is not a finished stone shape; this neutral top/cabinet
  // separation improves legibility without making a source-material claim.
   const visualTopH=Math.min(.09,(z1-z0)*.75);
   const top=new THREE.Mesh(new THREE.BoxGeometry(w,visualTopH,d),
    new THREE.MeshPhysicalMaterial({color:0xe9e5db,roughness:.32,clearcoat:.21,
     transparent:true,opacity:.95,side:THREE.DoubleSide}));
   top.position.set(x,z1-visualTopH/2,zz);
   top.receiveShadow=true;
   top.userData={...base.userData,category:'ARCH_NATIVE_COUNTERTOP_VISUAL',
    contained_within_native_category_aabb_xyz:true,
    source:'R060 neutral TOP VOLUME strictly contained inside read-only native countertop CATEGORY AABB XYZ; generic visual only, not actual fabricated stone, thickness, profile, cutout, selected material or certified mounting.'};
  modelGroup.add(top);renderObjects.push(top);
  drawR068NativeCounterLight(item,room,x,zz,w,d,z0,z1);
   if(basinProgramBlocked){
    const wording=room.id==='TX-POWDER'?'NO PICK YET':'BASIN UNSELECTED';
    base.userData.basin_program_status=wording+'; 3D BASIN NOT DRAWN';
    top.userData.basin_program_status=base.userData.basin_program_status;
    const s=item.closest_native_plumbing_insertion;
    if(s?.location_local_xz_ft){
     const locator=new THREE.Mesh(new THREE.RingGeometry(.09,.155,28),
      new THREE.MeshBasicMaterial({color:0x79b8d1,transparent:true,opacity:.83,
       depthWrite:false,side:THREE.DoubleSide}));
     locator.rotation.x=-Math.PI/2;
     locator.position.set(s.location_local_xz_ft[0],z1+.12,s.location_local_xz_ft[1]);
     locator.visible=state.sourceTraces;
     locator.userData={category:'ARCH_NATIVE_UNSELECTED_PLUMBING_LOCATOR',
      revit_id:s.id,receipt_id:s.receipt_id,countertop_id:item.id,
      room_number:instance()?.room_number,basin_program_status:wording,
      source_native_insertion_xyz_ft:s.location_native_ft,
      source_local_y_ft:s.location_native_ft?.[2]-arch.native_level_elevation_ft,
      displayed_plan_marker_y_ft:z1+.12,not_exact_native_3d_insertion:true,
      source:'Native PLAN-XY plumbing vicinity for a NO-PICK/UNSELECTED basin; raised PLAN locator ON SOURCE TRACES ONLY; no basin, countertop cutout, faucet installation, or approved product.'};
     modelGroup.add(locator);renderObjects.push(locator);
    }
   }
  // R059: native Countertop category AABB may START above the room floor.
  // R058's fascia extended that ambiguous volume to the FLOOR, falsely
  // implying a free-standing cabinet/pedestal. Restrict the illustrative
  // FRONT exclusively to the actual native category AABB's vertical
  // bounds; it is a color/contrast face, not a door, joinery or true family.
  const planVanity=(room.full_room_plan?.fixture_symbol_diagram?.items||[])
    .some(p=>p.kind==='vanity'||p.kind==='lavatory');
  const pts=arch?.floor_polygon_local_xz_ft||[];
  const r063CompactFocus=['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3'].includes(room.id);
  // A countertop CATEGORY AABB beginning below level (TX-BATH3 207A/B)
  // does not prove an installed cabinet/pedestal extending into the slab.
  // Preserve its original read-only source proxy and conditional basin
  // containment; WITHHOLD fabricated front/end/underside panels entirely.
  const r067Powder=['PH-POWDER','TX-POWDER','TX-POWDER2'].includes(room.id);
  if(r067Powder)drawR067PowderCounterFacets(item,room,x,zz,w,d,z0,z1,visualTopH,arch);
  if(r067Powder)drawR070NativeCounterSurfacePhoto(item,room,x,zz,w,d,z0,z1);
  // The generic pre-R067 front must not overlay the source-only .125ft slab
  // or duplicate the new carefully bounded powder visual faces.
  if(planVanity&&pts.length&&z0>.60&&!r067Powder){
   const xs=pts.map(p=>p[0]),zs=pts.map(p=>p[1]);
   const minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs);
   const longZ=d>w,faceAxis=longZ?'x':'z';
   const wallSide=longZ?
    (Math.abs(x-minX)<Math.abs(x-maxX)?'left':'right'):
    (Math.abs(zz-minZ)<Math.abs(zz-maxZ)?'rear':'front');
   const outward=longZ?(wallSide==='left'?1:-1):(wallSide==='rear'?1:-1);
   const primaryEnvelope=room.program?.kind==='PRIMARY_WALK_IN_LINEAR';
   // Primary long native Countertop AABBs range roughly 9.2-9.6ft and
   // FLOAT above the floor; use ONLY that native Y envelope to complete a
   // visually dimensional neutral study. NOT a selected cabinet height or
   // Revit family solid. Do not force a standard 34.5in manufactured size.
   const frontH=primaryEnvelope?
    Math.min(2.05,Math.max(.12,z1-z0-visualTopH-.035)):
    r063CompactFocus?
    Math.min(2.65,Math.max(.12,z1-z0-visualTopH-.035)):
    Math.min(1.09,Math.max(.12,z1-z0-.12));
   const face=new THREE.Mesh(new THREE.PlaneGeometry(longZ?d:w,frontH),
    new THREE.MeshPhysicalMaterial({color:primaryEnvelope?0xaaa093:r063CompactFocus?0xb9ad9c:0x9b8773,
     roughness:primaryEnvelope?.76:r063CompactFocus?.76:.83,
     clearcoat:primaryEnvelope?.06:r063CompactFocus?.045:0,
     transparent:true,opacity:primaryEnvelope?.97:r063CompactFocus?.83:.48,
     side:THREE.DoubleSide,depthWrite:false}));
   face.rotation.y=longZ?Math.PI/2:0;
   face.position.set(x+(longZ?outward*(w/2-.025):0),z0+frontH/2,
    zz+(!longZ?outward*(d/2-.025):0));
   face.userData={category:'ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL',
    revit_id:item.id,receipt_id:item.receipt_id,
    room_number:instance()?.room_number,front_source_axis:faceAxis,
    front_dimension_ft:longZ?d:w,front_display_height_ft:frontH,
    front_bottom_ft:z0,front_top_ft:z0+frontH,
    inside_native_aabb_y:true,
    source_countertop_aabb:item.native_bounds_ft,
    cabinet_family_solid:false,installed_face_location_verified:false,
    source:'TRANSPARENT GENERIC VANITY COLOR FACE strictly WITHIN native countertop category AABB bounds. Long axis from source, FRONT side drawing-INFERRED, not a native cabinet/vanity solid, full-height floor base, joinery, installation elevation or selected finish.'};
   modelGroup.add(face);renderObjects.push(face);
   if(r063CompactFocus&&w>.7&&d>.7&&z1-z0>.25){
    // Complete the little native Countertop-category footprint into a
    // legible neutral MASS STUDY, not a manufactured cabinet. Selected (or
    // unselected) basins retain their independent R056/R060 source gates;
    // these planar end/underside faces cannot establish vanity joinery,
    // support location, doors, tap, drawers, or material procurement.
    const sideMat=new THREE.MeshPhysicalMaterial({color:0xc7bdae,
     roughness:.78,clearcoat:.04,metalness:0,
     transparent:true,opacity:.83,depthWrite:false,side:THREE.DoubleSide});
    const hh=Math.max(.09,frontH-.012);
    for(const [endName,end] of [['END_A',-1],['END_B',1]]){
     const cap=new THREE.Mesh(longZ?
      new THREE.BoxGeometry(w-.055,hh,.028):
      new THREE.BoxGeometry(.028,hh,d-.055),sideMat);
     cap.position.set(x+(longZ?0:end*(w/2-.02)),z0+hh/2,
      zz+(longZ?end*(d/2-.02):0));
     cap.userData={category:'ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_SIDE_STUDY',
      revit_id:item.id,receipt_id:item.receipt_id,end_id:endName,
      source_bounds_native_ft:item.native_bounds_ft,
      source_bounds_local_ft:[x-w/2,x+w/2,z0,z1,zz-d/2,zz+d/2],
      visual_top_ft:z0+hh,visual_bottom_ft:z0,
      inside_native_category_aabb_xyz:true,not_native_family_solid:true,
      installed_support_verified:false,finish_selected:false,
      source:'Generic neutral side surface fully within native Revit Countertop category bounds; no invented floor pedestal (when native bottom floats), cabinet family, manufactured panel, sink or joinery'};
     modelGroup.add(cap);renderObjects.push(cap);
    }
    const under=new THREE.Mesh(new THREE.BoxGeometry(w-.065,.025,d-.065),
     new THREE.MeshPhysicalMaterial({color:0x777169,roughness:.94,
      transparent:true,opacity:.33,depthWrite:false,side:THREE.DoubleSide}));
    under.position.set(x,z0+.022,zz);
    under.userData={category:'ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_UNDERSIDE_STUDY',
     revit_id:item.id,receipt_id:item.receipt_id,
     source_bounds_native_ft:item.native_bounds_ft,
     source_bounds_local_ft:[x-w/2,x+w/2,z0,z1,zz-d/2,zz+d/2],
     visual_top_ft:z0+.035,visual_bottom_ft:z0+.009,
     inside_native_category_aabb_xyz:true,not_native_family_solid:true,
     floor_support_verified:false,finish_selected:false,
     source:'Viewer-only ambient underside entirely within original native Revit Countertop category AABB, not a floor pedestal, cabinet bottom specification or vanity support'};
    modelGroup.add(under);renderObjects.push(under);
   }
   if(primaryEnvelope&&longZ&&w>1&&d>4){
    // Both native bounding ends and a recessed underside read as one
    // abstract floating mass. No drawer seams, doors, sinks, faucet holes,
    // mounting brackets, selected wood/stone finish or floor-pedestal base.
    const returnMat=new THREE.MeshPhysicalMaterial({color:0xc8c0b5,
     metalness:0,roughness:.78,transparent:true,opacity:.65,
     side:THREE.DoubleSide,depthWrite:false});
    const hh=Math.max(.10,frontH-.012);
    for(const [index,end] of [['A',-1],['B',1]]){
     const cap=new THREE.Mesh(new THREE.BoxGeometry(w-.065,hh,.034),returnMat);
     cap.position.set(x,z0+hh/2,zz+end*(d/2-.023));
     cap.userData={category:'ARCH_R062_NATIVE_BOUND_VANITY_END_STUDY',
      revit_id:item.id,receipt_id:item.receipt_id,
      room_number:instance()?.room_number,end_id:index,
      original_native_category_aabb:item.native_bounds_ft,
      source_bound_height_min_ft:z0,source_bound_height_max_ft:z1,
      contained_within_native_category_aabb_xyz:true,
      not_selected_cabinet_joinery:true,
      source:'ILLUSTRATIVE bounded end surface within true native countertop category AABB and drawing-traced vanity long axis; never an installed finished panel, hardware, sink cutout or exact cabinet solid'};
     modelGroup.add(cap);renderObjects.push(cap);
    }
    const under=new THREE.Mesh(new THREE.BoxGeometry(w-.10,.027,d-.10),
     new THREE.MeshPhysicalMaterial({color:0x8f877d,roughness:.91,
      transparent:true,opacity:.37,depthWrite:false,side:THREE.DoubleSide}));
    under.position.set(x,z0+.025,zz);
    under.userData={category:'ARCH_R062_NATIVE_BOUND_VANITY_UNDERSIDE_STUDY',
     revit_id:item.id,receipt_id:item.receipt_id,room_number:instance()?.room_number,
     contained_within_native_category_aabb_xyz:true,
     source_bound_height_min_ft:z0,source_bound_height_max_ft:z1,
     original_native_category_aabb:item.native_bounds_ft,
     source:'Neutral viewer-only floating underside within actual Revit Countertop category bound; no cabinets, floor supports, mounting method, sink profile, fixture count or selected finish asserted'};
    modelGroup.add(under);renderObjects.push(under);
   }
   if((primaryEnvelope||room.id==='TX-BATH4')&&w>.90&&d>1.20&&z1-z0>.40){
    // R066: complete the SOURCE-NATIVE Countertop CATEGORY bounding study
    // with two shallow, light-catching edge tiers and, for short TX4
    // counters only, restrained open-end mass faces. Every vertex remains
    // INSIDE the original (x,z,y) native AABB. This is a *neutral extent
    // visualization* -- there is no evidence for fabrication thickness,
    // finished wood/stone, supports, sinks, tap or an installed cabinet.
    const tierH=Math.min(.085,(z1-z0)*.115),
     tierY=z1-visualTopH-tierH/2-.003;
    if(tierY-tierH/2>=z0+.005){
     const band=new THREE.Mesh(new THREE.BoxGeometry(w-.035,tierH,d-.035),
      new THREE.MeshPhysicalMaterial({color:0xb3aa9e,metalness:0,
       roughness:.49,clearcoat:.19,clearcoatRoughness:.31,
       transparent:true,opacity:.97,side:THREE.DoubleSide}));
     band.position.set(x,tierY,zz);
     band.receiveShadow=true;band.castShadow=false;
     band.userData={category:'ARCH_R066_NATIVE_BOUNDED_COUNTER_EDGE',
      revit_id:item.id,receipt_id:item.receipt_id,
      room_number:instance()?.room_number,source_native_bounds:item.native_bounds_ft,
      local_extent_ft:[x-w/2,x+w/2,tierY-tierH/2,tierY+tierH/2,zz-d/2,zz+d/2],
      r066_inside_category_aabb_xyz:true,r066_nominal_band_thickness_unverified:true,
      no_sink_cutout:true,not_native_solid:true,not_selected_counter_material:true,
      source:'Shallow shaded extent tier completely INSIDE native Countertop category AABB: neutral illumination edge ONLY. Not actual stone fabrication, thickness, trim, bracket, basin or selected finish.'};
     modelGroup.add(band);renderObjects.push(band);
    }
    const shadeH=Math.min(.045,(z1-z0)*.075),
      shadeY=z0+shadeH/2+.006;
    const shade=new THREE.Mesh(new THREE.BoxGeometry(w-.085,shadeH,d-.085),
      new THREE.MeshStandardMaterial({color:0x777069,metalness:0,
       roughness:.92,transparent:true,opacity:.43,side:THREE.DoubleSide,
       depthWrite:false}));
    shade.position.set(x,shadeY,zz);
    shade.userData={category:'ARCH_R066_NATIVE_BOUNDED_COUNTER_EDGE',
      revit_id:item.id,receipt_id:item.receipt_id,
      room_number:instance()?.room_number,source_native_bounds:item.native_bounds_ft,
      local_extent_ft:[x-w/2,x+w/2,shadeY-shadeH/2,shadeY+shadeH/2,zz-d/2,zz+d/2],
      r066_inside_category_aabb_xyz:true,r066_visual_shadow_only:true,
      not_floor_support:true,not_native_solid:true,not_selected_counter_material:true,
      source:'Recessed optical underside INSIDE native Countertop category AABB, not floor support, real family geometry, mounting hardware or selected finish.'};
    modelGroup.add(shade);renderObjects.push(shade);
    if(!primaryEnvelope){
     const endH=Math.min(1.06,Math.max(.10,z1-z0-visualTopH-.09));
     const mat=new THREE.MeshPhysicalMaterial({color:0xc2b9ad,
      roughness:.74,clearcoat:.04,transparent:true,opacity:.72,
      depthWrite:false,side:THREE.DoubleSide});
     const longZ=d>w;
     for(const [label,sign] of [['A',-1],['B',1]]){
      const cap=new THREE.Mesh(new THREE.BoxGeometry(longZ?w-.08:.024,
       endH,longZ?.024:d-.08),mat);
      cap.position.set(x+(longZ?0:sign*(w/2-.018)),z0+endH/2,
       zz+(longZ?sign*(d/2-.018):0));
      cap.userData={category:'ARCH_R066_NATIVE_BOUND_COUNTER_END_VISUAL',
       revit_id:item.id,receipt_id:item.receipt_id,
       room_number:instance()?.room_number,source_native_bounds:item.native_bounds_ft,
       end_label:label,r066_inside_category_aabb_xyz:true,
       not_native_family_solid:true,not_selected_wood_or_stone:true,
       source:'Neutral side plane INSIDE source Countertop category AABB, not a fabricated cabinet wall, support or selected joinery.'};
      modelGroup.add(cap);renderObjects.push(cap);
     }
    }
   }
  }
  if(hasSelectedBasin&&w>.95&&d>.96&&z1>1.8){
   // Basin is a visibly generic rendering atop source countertop bounds;
   // actual basin selection, opening, rough-in and faucet point NOT certified.
   const sourceSink=item.closest_native_plumbing_insertion;
   if(!sourceSink){
    // A broad countertop (notably the 202A/B double vanity) supplies NO
    // located basin or plumbing installation. Never make up a centered sink
    // in its 9.56-ft-long native bounding study.
    base.userData.basin_spatial_status='3D UNLOCATED; no native attributable plumbing insertion';
    top.userData.basin_spatial_status=base.userData.basin_spatial_status;
    drawn++;
    continue;
   }
   const sinkX=sourceSink?.location_local_xz_ft?.[0]??x;
   const sinkZ=sourceSink?.location_local_xz_ft?.[1]??zz;
   const basinRadiusX=Math.min(.52,w*.31),basinRadiusZ=Math.min(.38,d*.30);
   // An insertion can be associated with a nearby counter without fitting
   // a basin at that precise point. Do not render a basin hanging off its
   // native element AABB merely to make the room appear finished.
   const sourceFits=!sourceSink||(
    Math.abs(sinkX-x)+basinRadiusX<=w/2+.00001&&
    Math.abs(sinkZ-zz)+basinRadiusZ<=d/2+.00001);
   if(!sourceFits){
    const locator=new THREE.Mesh(new THREE.RingGeometry(.10,.18,24),
     new THREE.MeshBasicMaterial({color:0x9bd2ec,side:THREE.DoubleSide,
      transparent:true,opacity:.85,depthWrite:false}));
    locator.rotation.x=-Math.PI/2;
   // This raised ring is a PLAN-XY locator for visibility above the neutral
   // counter study, NOT the exact three-dimensional Revit insertion point.
   const nativeSourceY=sourceSink.location_native_ft[2]-arch.native_level_elevation_ft;
   const displayedLocatorY=z1+.14;
   locator.position.set(sinkX,displayedLocatorY,sinkZ);
    locator.userData={...base.userData,category:'ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR',
     plumbing_reference_id:sourceSink.id,
     plumbing_reference_receipt:sourceSink.receipt_id,
    source:'Read-only native plumbing PLAN XY, raised visually above study countertop. Ring elevation is NOT native Revit Z; generic basin envelope crosses native countertop AABB. Basin 3D UNLOCATED; no installed location, cabinet cutout or family solid certified',
     source_countertop_center_local_xz_ft:[x,zz],
     source_plumbing_local_xz_ft:[sinkX,sinkZ],
    source_plumbing_native_xyz_ft:sourceSink.location_native_ft,
    source_plumbing_local_y_ft:nativeSourceY,
    displayed_locator_y_ft:displayedLocatorY,
    visual_y_offset_from_source_ft:displayedLocatorY-nativeSourceY,
    not_exact_native_3d_insertion:true,
     generic_basin_radius_ft:[basinRadiusX,basinRadiusZ],
     not_family_solid:true,not_installed_clearance:true};
    modelGroup.add(locator);renderObjects.push(locator);
    drawn++;
    continue;
   }
   const basin=new THREE.Mesh(new THREE.SphereGeometry(1,28,14,0,Math.PI*2,0,Math.PI/2),
    neutral.porcelain);
   basin.scale.set(basinRadiusX,.10,basinRadiusZ);
   basin.rotation.x=Math.PI;
   basin.position.set(sinkX,z1+.065,sinkZ);
   basin.userData={...base.userData,category:'ARCH_ILLUSTRATIVE_BASIN_NO_FAMILY',
    source:sourceSink?'Generic basin placed at nearby native plumbing insertion; exact fixture/basin identity UNVERIFIED':
     'Generic countertop basin diagram; native source provides countertop bounds only',
    plumbing_reference_id:sourceSink?.id||null,
    plumbing_reference_receipt:sourceSink?.receipt_id||null};
   modelGroup.add(basin);renderObjects.push(basin);
   // A visible elliptical basin rim improves perceived fixture completeness
   // but is not a sink cutout, manufacturer geometry, selected basin SKU,
   // faucet rough-in or drain position.
   const rim=new THREE.Mesh(new THREE.TorusGeometry(1,.070,9,42),
    neutral.porcelain);
   rim.rotation.x=Math.PI/2;rim.scale.set(basinRadiusX,basinRadiusZ,1);
   rim.position.set(sinkX,z1+.155,sinkZ);
   rim.userData={...basin.userData,category:'ARCH_ILLUSTRATIVE_BASIN_RIM',
    actual_countertop_cutout:false,actual_drain_location:false,
    source:'Generic visual bowl rim at read-only native plumbing XZ, ONLY after full footprint containment; not sink family solid or countertop cutout'};
   modelGroup.add(rim);renderObjects.push(rim);
  }
  drawn++;
 }
 return drawn;
}
// R067: the 405 and 010 plans put a lavatory pictogram at the rear, and their
// native Countertop category bounds abut a specific native rear wall segment.
// A photographed SELECTED dry-WALL product can therefore be shown as a
// localized, source-hosted MATERIAL PREVIEW, never a certified installed
// tile extent. The display window width is constrained to the registered
// countertop and wall; its vertical size/starting course are intentionally
// illustrative with NO quantity, cost, layout or construction inference.
function drawR067DryVanityWallPreview(arch,room,wallP,wallIndex){
 if(!arch||!wallP||!['PH-POWDER','TX-POWDER2'].includes(room.id))return 0;
 const planItems=room.full_room_plan?.fixture_symbol_diagram?.items||[];
 if(!planItems.some(p=>(p.kind==='lavatory'||p.kind==='vanity')&&p.z_fraction>.70))return 0;
 const c=arch.native_casework_proxies?.[0],poly=arch.floor_polygon_local_xz_ft||[];
 if(!c||poly.length<3)return 0;
 const zMax=Math.max(...poly.map(p=>p[1]));
 const rear=arch.wall_segments?.filter(s=>
  Math.abs(s.start_local_ft[1]-zMax)<.13&&
  Math.abs(s.end_local_ft[1]-zMax)<.13&&
  Math.abs(s.end_local_ft[0]-s.start_local_ft[0])>2.4)
  .sort((a,b)=>Math.abs(b.end_local_ft[0]-b.start_local_ft[0])-
                  Math.abs(a.end_local_ft[0]-a.start_local_ft[0]))[0];
 if(!rear||Math.abs(c.local_center_xz_ft[1]+c.depth_z_ft/2-zMax)>.42||
    (arch.openings||[]).some(o=>o.host_id===rear.id))return 0;
 const lo=Math.min(rear.start_local_ft[0],rear.end_local_ft[0])+.085,
       hi=Math.max(rear.start_local_ft[0],rear.end_local_ft[0])-.085;
 const x0=Math.max(lo,c.local_center_xz_ft[0]-c.width_x_ft/2+.08),
       x1=Math.min(hi,c.local_center_xz_ft[0]+c.width_x_ft/2-.08);
 const width=x1-x0,ceiling=arch.native_ceiling_evidence?.underside_height_ft||9.25;
 const bottom=c.max_height_ft+.065,
       height=Math.min(3.55,ceiling-bottom-.30);
 if(width<1.5||height<1)return 0;
 // 0.035ft is a camera-display separation from the SOURCE-derived inner wall
 // face, not a tile build-up thickness, adhesive or substrate dimension.
 const preview=addPlane(width,height,[(x0+x1)/2,bottom+height/2,zMax-.035],
  [0,0,0],tileMaterial(wallP,width,height,'wall'),
  'ARCH_R067_SOURCE_HOSTED_DRY_FINISH_PREVIEW',wallIndex,{
   room_number:instance()?.room_number,selected_product:wallP.name,
   native_host_face_id:rear.id,native_host_face_receipt:rear.receipt_id,
   source_countertop_id:c.id,source_countertop_receipt:c.receipt_id,
   source_wall_face_z_ft:zMax,source_wall_segment_start:rear.start_local_ft,
   source_wall_segment_end:rear.end_local_ft,
   drawing_lavatory_rear_symbol:true,source_host_revit_wall:true,
   selected_product_visual_only:true,installed_tile_extent_verified:false,
   starting_course_verified:false,tile_layout_selected:false,
   actual_tile_coverage_area_ft2:null,additional_purchase_quantity_ft2:null,
   native_room_membership_certified:false,
   source:'SOURCE-HOSTED VIEWER-ONLY dry vanity WALL finish sample: selected maker image and nominal tile size on a rear wall native face, corresponding to drawing REAR lavatory symbol and native countertop vicinity; preview WIDTH source-bounded, preview HEIGHT/installed coverage UNVERIFIED. NOT manufacturer field sample, purchased square footage, grout choice, tile layout, installation point or approval.'});
 preview.userData.r067_dry_source_host=true;
 return 1;
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
 // Associate W1/W2/W3 visualization with the *actual native wall-line ID*
 // using the individual 311A/B source wall spans, not a generic "W1 is on
 // the east" assumption. B mirrors the actual exterior wall. Wet tile
 // membership remains DRAWING-calibrated; this ID only anchors existing
 // selected finish visibility and never supplies new niche/partition data.
 const matchedHost=(axis,value,minSpan)=>{
  const wall=(arch.wall_segments||[]).find(seg=>{
   const a=seg.start_local_ft,b=seg.end_local_ft;
   if(!a||!b)return false;
   const center=(a[axis]+b[axis])/2;
   return Math.abs(center-value)<.09&&
    Math.abs(a[1-axis]-b[1-axis])>=minSpan-.14;
  });
  return wall?{native_host_face_id:wall.id,
   native_host_face_receipt:wall.receipt_id,
   native_host_face_wall_source_only:true,
   named_room_membership_inferred:true}:{};
 };
 // On source-derived inner wall faces, tile is offset 1/4 inch inward to
 // avoid coplanarity against the physically thick wall solids.
 const source={source:'Frozen Pienza Terra + source-dimensioned wet run projected onto native-derived 311 wall faces',
  revit_wall_alignment:'NATIVE FACE DERIVED, NAMED-ROOM ASSIGNMENT INFERRED',room_number:inst.room_number};
 if(wallP){
  addPlane(long,h,[outerX-sign*.021,h/2,0],[0,Math.PI/2,0],
   tileMaterial(wallP,long,h,'wall'),'FULL_ROOM_WET_WALL',wallIndex,
   {...source,...matchedHost(0,outerX,long),wall:'W1',verified_hand:wetSide});
  for(const [wall,z] of [['W2',-main.d/2+.02],['W3',main.d/2-.02]]){
   // The +Z wall is also the exterior cutaway camera's near side. In the
   // general Full Bathroom review only, lower its display height to expose
   // the PH4 311 shower pan and 310 relationship. Wet Zone Study remains full
   // source height and purchase/tile geometry is never recalculated.
   const visualH=wall==='W3'?Math.min(h,2.8):h;
   addPlane(short,visualH,[wetCenter,visualH/2,z],[0,0,0],tileMaterial(wallP,short,visualH,'wall'),
    'FULL_ROOM_WET_WALL',wallIndex,{...source,...matchedHost(1,z,main.w),
     wall,verified_hand:wetSide,
     full_specification_height_ft:h,rendered_cutaway_height_ft:visualH,
     cutaway_only_visualization:wall==='W3',material_quantities_unchanged:true});
   if(wall==='W3'&&visualH<h-.02){
    // Wet-wall viewing mode can restore the full chosen product's visual
    // height. It does not add material area or change the low default W3.
    const original=addPlane(short,h,[wetCenter,h/2,z],[0,0,0],
     tileMaterial(wallP,short,h,'wall'),'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW',
     wallIndex,{...source,wall,full_specification_height_ft:h,
      rendered_cutaway_height_ft:visualH,view_only:true,
      no_additional_area:true,source_specification_unchanged:true});
    original.visible=false;
   }
  }
 }
 if(room.program?.pan_selected===true){
  // R066: In FULL BATHROOM the entire independently read-only native-wall
  // FACE polygon already has the one frozen Pienza LEVEL/POINT PAN material
  // (`ARCH_REGISTERED_FLOOR`, source ft UV). The second opaque rectangular
  // 2.54x5ft tile plane from early schematic rounds falsely split that
  // continuous finish and implied a second installed pan/curb. Suppress it
  // in Full Bathroom and retain schematic only in WET ZONE STUDY.
  // No slope, pan sub-boundary, drain center or quantity reconciliation.
  const registeredFloor=renderObjects.find(o=>o.userData?.category==='ARCH_REGISTERED_FLOOR');
  if(registeredFloor){
   registeredFloor.userData.r066_continuous_combined_level_point_pool=true;
   registeredFloor.userData.r066_no_duplicate_physical_pan_surface=true;
   registeredFloor.userData.source+=' One selected Pienza finish for ORIGINAL combined LEVEL/POINT PAN 40.2 gross SF pool: actual wall-face polygon rendered ONCE, no separately located pan/curb/drain or additional material area.';
   // Highlight the exact SAME polygon boundary already established by
   // source wall faces. NOT a second pan polygon or inserted curb. The
   // line is 0-width visualization only: visually connects floor/wet-wall
   // extents while leaving PH4 slope, drain centre and combined POOL open.
   const coords=arch.floor_polygon_local_xz_ft;
   if(coords?.length>2){
    const line=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
     coords.map(p=>new THREE.Vector3(p[0],.063,p[1]))),
     new THREE.LineBasicMaterial({color:0xb3a18b,transparent:true,
      opacity:.30,depthTest:true}));
    line.userData={category:'ARCH_R066_SHARED_LEVEL_POINT_SOURCE_EDGE',
     room_number:inst.room_number,selected_pool_gross_sf:40.2,
     area_added_sf:0,not_a_pan_boundary:true,not_a_curb:true,
     no_native_slope_or_drain:true,
     source:'Thin visual contact line exactly on registered source wall-face polygon. Original one 40.2 SF LEVEL/POINT PAN gross pool retained; not a second pan, waterproofing boundary, curb, confirmed drain or shop tile layout.'};
    modelGroup.add(line);renderObjects.push(line);
   }
  }
 }
 const r069SourceJunctions=drawR069SelectedWetJunctions(room);
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
  'Separate 310'+side+' compartment ('+(side==='A'?'WIC4: nearby fixture source IDs UNATTRIBUTED, no visible invented bathroom fixtures':'BATH4: native fixtures depicted generically, no native Room membership')+'), excluded from 311 purchase quantities. '+
  'Original 40.2 SF combined LEVEL/POINT PAN unchanged; drawing 27.08 versus frozen 35 SF unresolved. '+
  (arch.native_ceiling_evidence?'GWB native ceiling underside '+arch.native_ceiling_evidence.underside_height_ft.toFixed(3)+' ft; frozen 9.25ft height remains a distinct source, actual ceiling profile unverified. ':'')+
  'Full Bathroom uses ONE source-wall-face Pienza selected LEVEL/POINT floor across the registered 311 polygon (no duplicate schematic rectangular pan surface); no separate pan area, drain center or slope established. Front W3 Pienza wall is visually lowered only for cutaway; full tile height and quantities unchanged in Wet Zone Study. '+
  'R069 '+r069SourceJunctions+' light-only selected-finish/native-host junction(s) are optical contact, not an installed waterproofing joint, extra tile or fabricated drain. No invented niche, glass partition or precise point drain.';
 modelInfo.textContent='311'+side+' NATIVE WALL-FACE STUDY Â· '+main.w.toFixed(3)+' Ã— '+main.d.toFixed(3)+
  ' ft Â· '+main.walls+' wall parts Â· '+main.doors+' hosted door(s); room assignment drawing-inferred';
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
  if(o.material?.userData?.r065DisplayWallClone)o.material.dispose();
  if(o.material?.userData?.ownDiagramLabelTexture){
   o.material.map?.dispose();o.material.dispose();
  }
  if(o.material?.isLineBasicMaterial||o.material?.isLineDashedMaterial)o.material.dispose();
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
let r067WCOpticalShadow=null;
function r067WCOpticalShadowMaterial(){
 if(r067WCOpticalShadow)return r067WCOpticalShadow;
 const c=document.createElement('canvas');c.width=c.height=128;
 const ctx=c.getContext('2d'),g=ctx.createRadialGradient(64,64,5,64,64,64);
 g.addColorStop(0,'rgba(36,39,43,.25)');
 g.addColorStop(.34,'rgba(36,39,43,.12)');
 g.addColorStop(1,'rgba(36,39,43,0)');
 ctx.fillStyle=g;ctx.fillRect(0,0,128,128);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 r067WCOpticalShadow=new THREE.MeshBasicMaterial({map:tex,transparent:true,
  opacity:.44,depthWrite:false,side:THREE.DoubleSide});
 return r067WCOpticalShadow;
}
function drawPlanFixtureSymbol(kind,x,z,rotate=0,metadata={}){
 // Schematic diagram volumes from the latest floor plan's toilet/lavatory
 // pictograms. Dimensions are NOT manufacturer family dimensions or clearances.
 const root=new THREE.Group();root.position.set(x,.12,z);root.rotation.y=rotate;
 // R063/067: softly reflective studio ceramic, not a chosen manufacturer
 // fixture enamel, exact family geometry, installed height or model.
 // This is a generic bathroom fixture appearance only; exact porcelain,
 // glazing material and manufacturer family geometry are NOT claimed.
 const r069Ceramic=R069_FOCUS.has(state.room),r070DryCeramic=R070_DRY_FOCUS.has(state.room);
 const porcelain=new THREE.MeshPhysicalMaterial({
  color:(r069Ceramic||r070DryCeramic)?0xf7f5f0:0xf1f0eb,
  roughness:r070DryCeramic?.16:r069Ceramic?.18:.22,metalness:0,
  clearcoat:r070DryCeramic?.42:r069Ceramic?.38:.26,
  clearcoatRoughness:r070DryCeramic?.14:r069Ceramic?.16:.20,
  envMapIntensity:r070DryCeramic?1.1:r069Ceramic?1.04:.92});
 const brass=new THREE.MeshStandardMaterial({color:0x555f63,metalness:.75,roughness:.32});
 if(kind==='toilet'){
  // R067 refined continuous wall-hung-looking *GENERIC* porcelain shell
  // with shallow oval well and slimmer seat, INSIDE the pre-existing
  // collision-gated 1.4 x 2.05 ft illustrative plan envelope. Read-only
  // 270AA.101 AABB is NOT a ceramic mesh, so do not manufacture a cistern,
  // concealed carrier, trap, discharge point, rough-in or mounting dimension.
  // A rounded under-bowl volume makes the shell coherent from low angles,
  // but cannot imply actual supports, heights, SKU or wall-hung certification.
  // R070 follow-up: R067's detached two overlapping spheres looked like a
  // hovering ball in PH/TX WC Chrome. Use ONE continuous tapered neutral
  // ceramic VISUAL profile under the already source-gated seat. This has
  // no floor mounting or carrier assertion and never shifts native anchor,
  // footprint, source toe datum, wall or opening. The shell is narrower at
  // its visible underside and broadens to the generic (not SKU) seat.
  const bowlProfile=[
   [.055,.46],[.24,.475],[.37,.53],[.47,.64],[.54,.77],
   [.59,.90],[.595,1.07],[.56,1.19],[.49,1.255]
  ].map(v=>new THREE.Vector2(v[0],v[1]));
  const body=new THREE.Mesh(new THREE.LatheGeometry(bowlProfile,64),porcelain);
  body.scale.z=1.20;body.position.z=.18;
  body.userData={wc_visual_piece:'R070_CONTINUOUS_CERAMIC_SHELL',
   r070_ceramic_continuous_bowl:true,
   generic_wc_envelope_ft:[1.4,2.05],
   actual_wc_family_solid:false,not_a_carrier_or_pedestal:true,
   native_wall_support_verified:false,installed_height_verified:false,
   not_floor_mounted_claim:true,
   source:'Single continuous tapered generic porcelain visual INSIDE pre-existing 1.4x2.05ft source-gated plan envelope; bottom remains deliberately not certified to floor or wall. No manufacturer solid, carrier, mounting height, trap or rough-in.'};
  root.add(body);
  const seat=new THREE.Mesh(new THREE.TorusGeometry(1,.10,14,64),
   new THREE.MeshPhysicalMaterial({color:0xf8f7f3,roughness:.17,
    metalness:0,clearcoat:.43,clearcoatRoughness:.17}));
  seat.rotation.x=-Math.PI/2;seat.scale.set(.52,.67,1);
  seat.position.set(0,1.29,.21);
  seat.userData={wc_visual_piece:'R067_ABSTRACT_OVAL_SEAT',
   generic_wc_envelope_ft:[1.4,2.05],
   actual_wc_family_solid:false,installed_height_verified:false};
  root.add(seat);
  const well=new THREE.Mesh(new THREE.SphereGeometry(1,48,20),
   new THREE.MeshPhysicalMaterial({color:0x89989b,roughness:.23,
    metalness:0,clearcoat:.21,side:THREE.DoubleSide}));
  well.scale.set(.34,.020,.44);well.position.set(0,1.275,.22);
  well.userData={wc_visual_piece:'R067_GENERIC_RECESSED_WELL',
   actual_drain_location:false,not_installed_trap:true,
   installed_height_verified:false};
  root.add(well);
  const innerLip=new THREE.Mesh(new THREE.TorusGeometry(1,.035,10,64),
   new THREE.MeshPhysicalMaterial({color:0xeaeae5,roughness:.27,clearcoat:.24}));
  innerLip.rotation.x=-Math.PI/2;innerLip.scale.set(.35,.455,1);
  innerLip.position.set(0,1.294,.22);
  innerLip.userData={wc_visual_piece:'R067_GENERIC_INNER_LIP',
   generic_wc_envelope_ft:[1.4,2.05],actual_wc_family_solid:false};
  root.add(innerLip);
  // Do not add a separate floating rear shoulder: on mirrored lateral
  // anchors it falsely read as a detached second fixture. The continuous
  // shell/seat is the only 3D ceramic, with mounting hardware UNLOCATED.
  // The previous simulated GPU-cast WC shadow was a misleading long stripe.
  // This faint floor optical contact is small and strictly illustrative; it
  // is not a fixture support, wall carrier, drain or installed height.
  const groundGlow=new THREE.Mesh(new THREE.PlaneGeometry(1.17,1.58),
   r067WCOpticalShadowMaterial());
  groundGlow.rotation.x=-Math.PI/2;groundGlow.position.set(0,-.091,.16);
  groundGlow.renderOrder=2;
  groundGlow.userData={wc_visual_piece:'R067_GENERIC_OPTICAL_FLOOR_OCCLUSION',
   source_2d_envelope_ft:[1.4,2.05],actual_floor_support:false,
   not_native_family_solid:true,installed_height_verified:false};
  root.add(groundGlow);
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
  if(ref){
   // TX-BATH3 / PH-BATH3: the drawing shows a TUB REFERENCE, not an
   // owner-selected TUB or WALK-IN. Keep an explicitly two-dimensional
   // source-plan footprint; NO 3D bathtub, tiled pan or drain is selected.
   const plate=new THREE.Mesh(new THREE.PlaneGeometry(width,depth),
    new THREE.MeshBasicMaterial({color:0x8abaca,transparent:true,opacity:.10,
     depthWrite:false,side:THREE.DoubleSide}));
   plate.rotation.x=-Math.PI/2;plate.position.y=-.070;root.add(plate);
   const trace=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(width,depth)),
    new THREE.LineDashedMaterial({color:0x9bb8bc,dashSize:.22,gapSize:.15,
      opacity:.86,transparent:true,depthTest:false}));
   trace.rotation.x=-Math.PI/2;trace.position.y=-.065;
   trace.computeLineDistances();root.add(trace);
  }else{
   // SELECTED nominal Duravit exterior 59 x 29.5 inches: keep exact source
   // outer footprint while making an easily recognized HOLLOW vessel rather
   // than four opaque square walls. Rounded rim, inside well and ALL vertical
   // dimensions are generic illustrative design, not a native family solid
   // or verified installed plumbing. No invented tap/spout/drain.
   const outer=new THREE.Shape(),rad=Math.min(.22,width*.07,depth*.10);
   const lx=-width/2,rx=width/2,bz=-depth/2,fz=depth/2;
   outer.moveTo(lx+rad,bz);
   outer.lineTo(rx-rad,bz);outer.quadraticCurveTo(rx,bz,rx,bz+rad);
   outer.lineTo(rx,fz-rad);outer.quadraticCurveTo(rx,fz,rx-rad,fz);
   outer.lineTo(lx+rad,fz);outer.quadraticCurveTo(lx,fz,lx,fz-rad);
   outer.lineTo(lx,bz+rad);outer.quadraticCurveTo(lx,bz,lx+rad,bz);
   outer.closePath();
   const well=new THREE.Path();
   well.absellipse(0,0,(width-.43)/2,(depth-.40)/2,0,Math.PI*2,true,0);
   outer.holes.push(well);
   const shell=new THREE.Mesh(new THREE.ExtrudeGeometry(outer,{
     depth:1.34,steps:1,curveSegments:28,bevelEnabled:false}),
    new THREE.MeshPhysicalMaterial({color:0xf3f2ec,roughness:.18,
      clearcoat:.36,clearcoatRoughness:.16,envMapIntensity:1.06,
      side:THREE.DoubleSide}));
   shell.rotation.x=-Math.PI/2;shell.position.y=.055;
   shell.userData={generic_visual_profile:true,nominal_exterior_width_ft:width,
    nominal_exterior_depth_ft:depth,vertical_profile_verified:false,
    actual_manufacturer_solid:false,actual_drain_location:false,
    actual_faucet_location:false};
   root.add(shell);
   // The prior single extrusion read like a square plastic perimeter with
   // an empty dark oval. A source-footprint-CONTAINED thin 3D render-only
   // ceramic lip catches soft studio highlights. Reuses the SAME rounded
   // nominal outside and hole profile; zero plumbing, apron, tub flange,
   // drain/spout, exact manufacturer profile or construction depth implied.
   const lip=new THREE.Mesh(new THREE.ShapeGeometry(outer,32),
    new THREE.MeshPhysicalMaterial({color:0xfffefa,roughness:.12,
     clearcoat:.58,clearcoatRoughness:.10,envMapIntensity:1.1,
     side:THREE.DoubleSide}));
   lip.rotation.x=-Math.PI/2;
   lip.position.y=1.402;
   lip.userData={generic_visual_profile:false,
    r063_tub_part:'CERAMIC_TOP_RIM_STUDY',
    nominal_exterior_width_ft:width,nominal_exterior_depth_ft:depth,
    actual_manufacturer_solid:false,not_selected_rim_design:true,
    actual_drain_location:false,actual_faucet_location:false,
    source:'Thin generic highlight top face within pre-existing frozen nominal exterior Duravit selected tub footprint; NOT accurate Starck family profile, cutout/flange, drain/spout or selected installation elevation'};
   root.add(lip);
   const wellFloor=new THREE.Mesh(new THREE.CircleGeometry(1,54),
    new THREE.MeshPhysicalMaterial({color:0xd9dfe0,roughness:.32,
     clearcoat:.16,clearcoatRoughness:.29,side:THREE.DoubleSide}));
   wellFloor.rotation.x=-Math.PI/2;
   wellFloor.scale.set((width-.47)/2,(depth-.44)/2,1);
   wellFloor.position.y=.26;root.add(wellFloor);
   // R070 follow-up: a shallow, continuous illustrative porcelain INNER
   // bowl surface replaces the disconnected black void reading in selected
   // PH/TX Bath2. It stays entirely inside frozen nominal Duravit exterior
   // XY and below the existing generic rim; no new exterior body, flange,
   // drain/overflow location or manufacturer-specific shell geometry.
   const innerProfile=[
    [0,.292],[.30,.305],[.49,.39],[.66,.55],
    [.80,.82],[.90,1.11],[.97,1.325]
   ].map(v=>new THREE.Vector2(v[0],v[1]));
   const inner=new THREE.Mesh(new THREE.LatheGeometry(innerProfile,72),
    new THREE.MeshPhysicalMaterial({color:0xf1f3f0,roughness:.24,
     clearcoat:.34,clearcoatRoughness:.20,metalness:0,
     envMapIntensity:.89,side:THREE.DoubleSide}));
   inner.scale.set((width-.45)/2,1,(depth-.43)/2);
   inner.userData={wc_visual_piece:'R070_GENERIC_TUB_INNER_PORCELAIN',
    r070_illustrative_tub_inner:true,nominal_exterior_width_ft:width,
    nominal_exterior_depth_ft:depth,actual_manufacturer_solid:false,
    actual_drain_location:false,actual_overflow_location:false,
    actual_installation_elevation_verified:false,
    no_tub_flange_or_spout_modelled:true,
    source:'Visual-only curved white inner basin BELOW existing nominal-size selected Duravit generic lip; not a manufacturer family solid, bottom thickness, waste/overflow cut, depth or installed fixture elevation.'};
   root.add(inner);
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
  // R061: real-time contact shadows from the existing GENERIC, source-gated
  // opaque porcelain/tub study silhouettes. No phantom shower, pan, outline,
  // manufacturer family, fixture height or new installed geometry is added.
  // Wall-hung WC geometry is generic and source Z is not a certified
  // mounting mesh: its elevated bowl produced a detached, 2ft-long floor
  // shadow in R061 Chrome. Only nominal source-fitted selected TUB shells
  // may cast studio shadows until a true native fixture solid exists.
  const castIllustrativeShadow=kind==='tub';
  o.castShadow=castIllustrativeShadow;
  o.receiveShadow=castIllustrativeShadow||kind==='toilet';
  o.userData={...o.userData,category:'PLAN_SCHEMATIC_FIXTURE',surfaceIndex:-1,
   source:kind==='tub'?
    'SELECTED nominal Duravit exterior footprint; rounded hollow shell is GENERIC manufacturer-noncertified visualization; no fabricated drain/spout':
    kind==='tub-reference'?
    'LATEST ARCHITECT PLAN TUB REFERENCE ONLY; owner TUB/WALK-IN UNSELECTED, no bathtub solid or pan, 2D outline at drawing-relative coordinate':
    kind==='toilet'?
    'R059 porcelain WC silhouette INSIDE existing source-gated 1.4x2.05ft illustrative plan footprint; native insertion and family AABB remain distinct. No manufacturer solid, mounting elevation, carrier, drain, cistern or plumbing rough-in':
    'Latest architectural plan pictogram; appearance and size ILLUSTRATIVE',
   kind,room_number:metadata.room_number,not_native_revit_family:true,
   fixture_visual_classification:kind==='tub'?'NOMINAL_SELECTED_TUB_HOLLOW_GENERIC':
    kind==='tub-reference'?'UNSELECTED_BRANCH_2D_PLAN_ONLY':'GENERIC_PLAN_PROXY',
   not_installed_tub_clearance:true,
   no_bathtub_drain_or_spout_location:true,
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
 return ring;
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
  if(type==='shower-reference'&&room.program?.kind==='PRIMARY_WALK_IN_LINEAR'){
   // R062 source truth: the Nov-07 primary walk-in graphic has only an
   // approximate RELATIVE coordinate, while the native counter, corner and
   // hosted entry geometry do not yet certify a physical shower footprint.
   // Even a source-native WALL host cannot establish the selected shower
   // INSTALLATION position. Withhold the earlier dark, floor-sized reference
   // slab; keep a small 2D survey ring under Source traces only.
   const mark=addUnlocatedFixtureMarker(type,x,z,
    'PRIMARY WALK-IN source plan symbol has no collision-free native verified 3D installation; selected 48in LINEAR drain position unknown',inst?.room_number);
   mark.userData.primary_source_only=true;
   mark.userData.primary_no_physical_shower_model=true;
   mark.visible=state.sourceTraces;
   suppressed++;continue;
  }
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
   if(type==='tub-reference'){
    // The previous opaque BLACK rectangular floor placard visually read as a
    // constructed step or blocking pan. Retain the exact annotation in the
    // existing program/inspector; draw it ONLY in Source traces mode. The
    // 2D plan footprint stays available in the normal full-room study.
    const note=addPlanLabel('ARCH DRAWING TUB / UNSELECTED',x,z,'#d9c3a5');
    note.userData={category:'ARCH_R061_UNSELECTED_PLAN_LABEL',surfaceIndex:-1,
     room_number:inst?.room_number,
     source:'Nov-07 architecture tub PICTOGRAM ONLY; OWNER TUB/WALK-IN UNSELECTED, annotation not physical fixture/step/PAN. Source traces toggles label.'};
    note.visible=state.sourceTraces;
    renderObjects.push(note);
   }
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
 // dimensioned, so show a translucent continuous faÃ§ade, not a fake cutout.
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
 modeInfo='A2.2 LATEST OWNER-UPLOADED 2026-11-07: '+inst.room_number+' is a MIRRORED 5â€²-5â€³ Ã— 5â€²-0â€³ shower room; open bedroom-side entry on the '+
  entry.toUpperCase()+'. Side-wall-break length approximated; actual opening dimensions unverified. '+
  'Shower along '+wetSide+' outer wall per actual plan. '+adj.number+' '+adj.label+
  ' shown in subdued plan context with schematic toilet/lav symbols, NOT part of the 311 shower material allowance. '+
  'Selected walk-in and shared Pienza LEVEL/POINT PAN original 40.2 SF pool preserved exactly once. '+
  '311 display polygon '+plan.display_area_ft2+' SF conflicts with frozen 35 SF owner figure; NO takeoff change. '+
  'No invented drain location, niche, shower glazing, slope, fixture families or wall thickness.';
 modelInfo.textContent=inst.room_number+' MIRRORED '+entry.toUpperCase()+' ENTRY, '+wetSide.toUpperCase()+' SHOWER'+
  ' Â· 311 '+w.toFixed(3)+'Ã—'+d.toFixed(3)+' ft Â· adjacent 310 context separately';
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
  // R061: when the actual native wet host is shorter than the frozen W1
  // length (notably TX2 205A/B with a stepped room face), clamp the VIEWER
  // center using the shorter native-visible run. The former wetRun/2 clamp
  // could put both W2/W3 *inside* the source side wall, hiding valid native
  // returns and making a fake floating wall strip. NEVER change the frozen
  // source W1 length, tile quantity, drawing fixture placement or wet SKU.
  const visualRun=Math.min(wetRun,selected.run);
  const midpoint=Math.max(selected.min+visualRun/2,
   Math.min(selected.max-visualRun/2,target));
 return {...selected,center:midpoint,
   rendered_run_ft:visualRun,
  original_wet_run_ft:wetRun,
  run_difference_ft:Math.max(0,wetRun-selected.run),
  source:'Native wall-face run, trimmed when shorter than frozen drawing-derived wet-wall length; source quantities remain unchanged'};
}
function registeredWetReturnSupport(arch,from,to){
 // R061: W2/W3 may only become THREE-DIMENSIONAL selected finish planes
 // when an actual read-only native wall-face SEGMENT supports the proposed
 // drawing return. A drawing wet-wall LENGTH by itself is NOT a partition.
 // This check is strictly positional, not construction tolerance, slope,
 // profile, installer tile coverage, or room-to-wall native membership.
 const dx=to[0]-from[0],dz=to[1]-from[1];
 const isX=Math.abs(dx)>Math.abs(dz),axis=isX?0:1,fixed=isX?1:0;
 const wanted=Math.abs(isX?dx:dz);
 if(wanted<.15)return null;
 const fixedValue=(from[fixed]+to[fixed])/2;
 const lo=Math.min(from[axis],to[axis]),hi=Math.max(from[axis],to[axis]);
 let winner=null;
 for(const wall of arch?.wall_segments||[]){
  const a=wall.start_local_ft,b=wall.end_local_ft;
  if(Math.abs(a[fixed]-b[fixed])>.08)continue;
  const perpendicular=Math.max(Math.abs(a[fixed]-fixedValue),Math.abs(b[fixed]-fixedValue));
  if(perpendicular>.13)continue;
  const wlo=Math.min(a[axis],b[axis]),whi=Math.max(a[axis],b[axis]);
  const overlap=Math.max(0,Math.min(hi,whi)-Math.max(lo,wlo));
  const nearest=q=>q<wlo?wlo-q:q>whi?q-whi:0;
  const endpointError=Math.max(nearest(from[axis]),nearest(to[axis]));
  if(overlap+.17<wanted||endpointError>.17)continue;
  const score=perpendicular*4+endpointError*2+(wanted-overlap);
  if(!winner||score<winner.score)winner={wall_id:wall.id,
   wall_receipt_id:wall.receipt_id,score,overlap_ft:overlap,
   length_ft:wanted,perpendicular_error_ft:perpendicular,
   endpoint_error_ft:endpointError,
   native_wall_placement_read_only:true,
   room_assignment_inferred:true,not_native_wall_finish_parameter:true};
 }
 return winner;
}
function auditedPrimaryWetCandidate(arch,placement,host,wetWidth,wetDepth){
 // R062: Primary programme is selected WALK-IN/48in factory-solid LINEAR,
 // but its position is NOT supplied by a native Revit fixture solid/drain.
 // This gate only vetoes a misleading 3D wet-room projection using precise
 // source-native wall faces, original CATEGORY countertop AABBs and native
 // hosted door insertions. A PASS would establish only an illustrative
 // nonconflicting wet-envelope *study*, NEVER an installed shower footprint.
 if(!arch?.floor_polygon_local_xz_ft?.length||!placement||!host||
    !(wetWidth>.1&&wetDepth>.1)||!['left','right'].includes(placement.side))
  return {classification:'NO_REGISTERED_WET_ENVELOPE',valid:false,
   source:'No sufficient mapped native wall-face supporting source drawing wet reference',
   counter_overlap_sf:null,hosted_entry_conflicts:[],polygon_support:false};
 const sign=placement.side==='left'?-1:1;
 const x0=Math.min(host.face,host.face-sign*wetDepth),
  x1=Math.max(host.face,host.face-sign*wetDepth);
 const run=Math.min(wetWidth,host.rendered_run_ft),
  z0=host.center-run/2,z1=host.center+run/2;
 const inset=.09;
 const p=arch.floor_polygon_local_xz_ft;
 const polygonSupport=[.018,.50,.982].every(fx=>
  [.018,.50,.982].every(fz=>diagramPointWithinPolygon(
   x0+inset+(x1-x0-2*inset)*fx,
   z0+inset+(z1-z0-2*inset)*fz,p)));
 let overlap=0;
 const counterIds=[];
 for(const counter of arch.native_casework_proxies||[]){
  const c=counter.local_center_xz_ft||[];
  if(c.length<2)continue;
  const ax=Math.max(0,Math.min(x1,c[0]+counter.width_x_ft/2)-
   Math.max(x0,c[0]-counter.width_x_ft/2));
  const az=Math.max(0,Math.min(z1,c[1]+counter.depth_z_ft/2)-
   Math.max(z0,c[1]-counter.depth_z_ft/2));
  const area=ax*az;
  if(area>.015){overlap+=area;counterIds.push(counter.id);}
 }
 const doorIds=[];
 for(const door of arch.openings||[]){
  if(door.kind!=='door'||!door.location_local_ft)continue;
  const [x,z]=door.location_local_ft;
  const dx=Math.max(x0-x,0,x-x1),dz=Math.max(z0-z,0,z-z1);
  // 0.32ft is a SOURCE-VETO visual buffer around a nominal hosted station,
  // not any legal, fabrication, swing or installer-clearance dimension.
  if(Math.hypot(dx,dz)<.32)doorIds.push(door.id);
 }
 const valid=polygonSupport&&overlap<.015&&doorIds.length===0;
 return {classification:valid?'DRAWING_RELATIVE_NONCONFLICTING_STUDY_ONLY':
  'PRIMARY_WET_3D_UNLOCATED_SOURCE_CONFLICT',valid,
  counter_overlap_sf:Math.round(overlap*1000)/1000,
  native_countertop_conflicts:counterIds,
  hosted_entry_conflicts:doorIds,
  polygon_support:polygonSupport,
  candidate_native_wall_id:host.wall_id,
  candidate_native_wall_receipt:arch.wall_receipt_id,
  candidate_bbox_local_xz_ft:[x0,z0,x1,z1],
  source:'Source-bound PROVISIONAL projected wet envelope tested against true Revit wall-face polygon, category countertop AABB and hosted door station; drawing-relative fixture location and installation remains UNLOCATED; not construction clearance, native shower family, tile quantity, exact drain placement, PAN or proposed change'};
}
function drawPrimaryUnlocatedWetTrace(truth,roomNumber){
 const box=truth?.candidate_bbox_local_xz_ft;
 if(!box||box.length!==4)return;
 const w=box[2]-box[0],d=box[3]-box[1];
 if(!(w>.1&&d>.1))return;
 const line=new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.PlaneGeometry(w,d)),
  new THREE.LineDashedMaterial({color:0xd0ab7a,dashSize:.20,gapSize:.15,
   transparent:true,opacity:.76,depthTest:false}));
 line.position.set((box[0]+box[2])/2,.082,(box[1]+box[3])/2);
 line.rotation.x=-Math.PI/2;line.computeLineDistances();
 line.visible=state.sourceTraces;
 line.userData={category:'ARCH_R062_PRIMARY_WET_UNLOCATED_PLAN_TRACE',
  room_number:roomNumber,...truth,
  not_installed_shower:true,selected_48in_drain_center:null,
  no_slope_glass_niche_or_tub:true};
 modelGroup.add(line);renderObjects.push(line);
}
function buildLegacyFullRoom(room){
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
 const primary=room.program?.kind==='PRIMARY_WALK_IN_LINEAR';
 const primaryTruth=primary?auditedPrimaryWetCandidate(arch,placement,nativeSupport,wetW,wetD):null;
 if(primary&&reconstructed)drawPrimaryUnlocatedWetTrace(primaryTruth,instance()?.room_number);
 const showWet=Boolean(placement&&wetW>0&&wetD>0&&
  (isSide?wetW<=d+.5&&wetD<=w+.5:wetW<=w+.5&&wetD<=d+.5)&&
  (!reconstructed||nativeSupport)&&(!primary||primaryTruth?.valid));
 const ph2FrontReview=room.id==='PH-BATH2'&&placement?.side==='front'&&Boolean(arch?.selected_tub_proxy);
 let supportedReturns=0,withheldReturns=0;
 if(showWet){
  const tw=Math.min(wetW,isSide?d:w,nativeSupport?.rendered_run_ft??Infinity),
   td=Math.min(wetD,isSide?w:d),th=Math.min(wetH,ceiling);
  // 305A/B: the Nov-07 plan places the selected tub immediately behind
  // SOUTH/front W1. A full opaque 9-ft W1 conceals that tub from the default
  // 3D camera despite a source-compatible fixture fit. In Full Bathroom ONLY,
   // present the FRONT W1 as a low visual cutaway; R061 now preserves the
   // registered full-height return finish planes on actual native side walls.
   // Original frozen heights remain accessible in Wet Zone and Wet wall view.
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
   const support=reconstructed?registeredWetReturnSupport(arch,
    [edgeX,z],[edgeX-sign*length,z]):null;
   if(reconstructed&&!support){withheldReturns++;continue;}
    const m=wallP?tileMaterial(wallP,length,th,'wall'):neutral.wall;
    addPlane(length,th,[edgeX-sign*length/2,th/2,z],[0,0,0],m,
    'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W'+(idx+1),
     native_host_face_id:support?.wall_id||null,
     native_host_face_receipt:support?.wall_receipt_id||null,
     source_return_supported:Boolean(support),derived_return_not_partition:true,
     review_return_face_midpoint_xz_ft:[edgeX-sign*length/2,z],
     review_return_outward_xz:[0,idx===1?-1:1],
     review_return_full_height_ft:th,review_return_rendered_height_ft:th,
     review_return_section_only:false});
   if(support&&R063_FOCUS_BATHS.has(room.id))sourceWetFinishCornerShade(
    [edgeX,z],[-sign,0],[0,idx===1?1:-1],th,{
     native_host_face_id:support.wall_id,native_host_face_receipt:support.wall_receipt_id,
     source_return_supported:true,review_return_face_midpoint_xz_ft:[edgeX-sign*length/2,z],
     review_return_outward_xz:[0,idx===1?-1:1],
     wall:'W'+(idx+1),room_number:instance()?.room_number});
   if(support)supportedReturns++;
   }
   [panW,panD,panX,panZ]=[td,tw,x,zMid];
  }else{
   const sign=placement.side==='front'?1:-1,
    edgeZ=nativeSupport?nativeSupport.face:sign*d/2,
    xMid=nativeSupport?nativeSupport.center:0;
   const m=wallP?tileMaterial(wallP,tw,reviewHeight,'wall'):neutral.wall;
   addPlane(tw,reviewHeight,[xMid,reviewHeight/2,edgeZ-sign*.042],[0,0,0],m,
    'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W1'});
   if(ph2FrontReview&&reviewHeight<th-.02){
    const full=addPlane(tw,th,[xMid,th/2,edgeZ-sign*.042],[0,0,0],
     wallP?tileMaterial(wallP,tw,th,'wall'):neutral.wall,
     'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW',wallIndex,
     {...wetSource,wall:'W1',view_only:true,no_additional_area:true});
    full.visible=false;
   }
   for(const [idx,x,rotation] of [[1,xMid-tw/2,Math.PI/2],[2,xMid+tw/2,-Math.PI/2]]){
    if(!s.wall_segments?.[idx])continue;
    const run=stdNum(s.wall_segments[idx]?.length);
    if(!(run>0))continue;
    const length=Math.min(td,run);
   const support=reconstructed?registeredWetReturnSupport(arch,
    [x,edgeZ],[x,edgeZ-sign*length]):null;
   if(reconstructed&&!support){withheldReturns++;continue;}
   // PH2 selected Duravit tub is behind the SOUTH/front W1; suppressing ALL
   // W1/W2/W3 at 0.72ft made the selected blue tile nearly invisible in
   // ordinary Full Bathroom. Keep W1 sectioned to disclose the physical tub,
   // but display full-height returns ONLY on verified native side-wall runs.
   // R059's full review counterparts still replace originals in Wet camera.
   const returnHeight=ph2FrontReview?th:reviewHeight;
   const m=wallP?tileMaterial(wallP,length,returnHeight,'wall'):neutral.wall;
   addPlane(length,returnHeight,[x,returnHeight/2,edgeZ-sign*length/2],[0,rotation,0],m,
    'FULL_ROOM_WET_WALL',wallIndex,{...wetSource,wall:'W'+(idx+1),
     rendered_cutaway_height_ft:returnHeight,
     full_height_return_normal_review:ph2FrontReview,
     native_host_face_id:support?.wall_id||null,
     native_host_face_receipt:support?.wall_receipt_id||null,
     source_return_supported:Boolean(support),derived_return_not_partition:true,
     review_return_face_midpoint_xz_ft:[x,edgeZ-sign*length/2],
     review_return_outward_xz:[idx===1?-1:1,0],
     review_return_full_height_ft:returnHeight,
     review_return_rendered_height_ft:returnHeight,
     review_return_section_only:false});
   if(support&&R063_FOCUS_BATHS.has(room.id))sourceWetFinishCornerShade(
    [x,edgeZ],[0,-sign],[idx===1?1:-1,0],returnHeight,{
     native_host_face_id:support.wall_id,native_host_face_receipt:support.wall_receipt_id,
     source_return_supported:true,review_return_face_midpoint_xz_ft:[x,edgeZ-sign*length/2],
     review_return_outward_xz:[idx===1?-1:1,0],
     full_height_return_normal_review:ph2FrontReview,
     wall:'W'+(idx+1),room_number:instance()?.room_number});
   if(support)supportedReturns++;
    if(ph2FrontReview&&reviewHeight<th-.02){
     const full=addPlane(length,th,[x,th/2,edgeZ-sign*length/2],[0,rotation,0],
      wallP?tileMaterial(wallP,length,th,'wall'):neutral.wall,
      'ARCH_R059_FULL_HEIGHT_FINISH_REVIEW',wallIndex,
      {...wetSource,wall:'W'+(idx+1),view_only:true,no_additional_area:true});
     full.visible=false;
    }
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
 // R068: only confirmed selected nominal Duravit tub feet and W1/W2/W3
 // actual host-ID supported finishes may have an optical tub-to-wall
 // transition. No extra tile face, installed connection or modeled drain.
 const r069WetContacts=reconstructed&&showWet?drawR069SelectedWetJunctions(room):0;
 const r068Bath2Contacts=reconstructed&&showWet?
  drawR068TubSourceFinishContact(room,arch):0;
 const sourceCasework=reconstructed?drawRegisteredCasework(arch,room):0;
 const r067DryWall=reconstructed?drawR067DryVanityWallPreview(arch,room,wallP,wallIndex):0;
 const unlocatedNativeBasins=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR');
 const missingSourceBasins=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_CASEWORK_AABB_STUDY'&&
  o.userData?.basin_spatial_status);
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
  'REGISTERED REVIT WALL-FACE ARCHITECTURE â€” '+reconstructed.area.toFixed(2)+
   ' SF visual polygon; wall location/host openings source-native, ROOM NUMBER still drawing-inferred. '+reconstructed.doors+
   ' nominal hosted door leaves, swing/rough opening unknown. ':
  'FULL BATHROOM FLOOR-PLAN ENCLOSURE â€” '+plan.confidence+'. '+plan.evidence+
   '. Actual wall thickness, door/window opening geometry and Revit room polygon UNVERIFIED.')+
  (showWet?' Frozen wet tiles displayed alongside the '+placement.side.toUpperCase()+
    (ph2FrontReview?' PH-BATH2 south W1 LOWERED TO 0.72 FT FOR TUB REVIEW; only native-wall-supported side returns shown at original full height. Wet wall camera restores W1 full height; selected specification and quantities unchanged.':'')+
   (nativeSupport?' native-derived host wall face (membership drawing-inferred).'+
    (nativeSupport.run_difference_ft>.015?' W1 visual run trimmed '+nativeSupport.run_difference_ft.toFixed(3)+' ft to actual native wall-face segment; FROZEN source W1 dimensions and material pool are unchanged.':'') :
    ' plan-traced tub/shower reference; native spatial location NOT VERIFIED.'):
   (wallP?r067DryWall?
    ' Selected dry vanity WALL displayed as a bounded illustrative finish preview on native rear wall near drawing lavatory/countertop; installed coverage/location beyond source face NOT verified; zero added purchased area.':
    ' Selected wall material remains an UNLOCATED study pending wall-face/fixture evidence.':''))+
  (areaConflict?' DISPLAY AREA '+plan.display_area_ft2+' SF versus legacy/owner '+plan.source_floor_area_ft2+' SF: RECONCILIATION OPEN.':'')+
  (spec?' Fixture diagrams follow plan pictograms with illustrative model dimensions; exact native family geometry/positions NOT established.':'')+
  ' No unverified niche, shower drain position or glazing fabricated.'+
   (primary?' R062 PRIMARY SELECTED WALK-IN/48in LINEAR: '+primaryTruth.classification+
    '; physical 3D wet assembly withheld if native casework/hosted entry or room polygon conflict; '+
    'counter overlap '+(primaryTruth.counter_overlap_sf??'unknown')+' SF, nearby source door IDs '+
    (primaryTruth.hosted_entry_conflicts?.join(',')||'none')+'. Source-trace-only 2D envelope; Wet Zone Study dimensions are NOT certified installation or additional PAN.':'')+
   (showWet&&reconstructed?' R061 wet RETURN SOURCE GATE: '+supportedReturns+' native-wall-supported selected-finish return(s); '+withheldReturns+' UNSUPPORTED 3D return(s) WITHHELD (original wet-zone study dimensions and selections remain accessible).':'')+
  (sourceCasework?' '+sourceCasework+' native bounded countertop/vanity proxy(s) replace generic plan-lavatory positions; countertop geometry and basin are schematic, not certified.':'')+
  (r068Bath2Contacts?' R068 '+r068Bath2Contacts+' source-native-hosted selected-finish/tub photograph contact gradients are VISUAL ONLY; no waterproofing joint, tile quantity, installed tub elevation, rough-in or manufacturer geometry asserted.':'')+
  (r069WetContacts?' R069 '+r069WetContacts+' source-native-hosted selected finish-to-level optical contact(s), no installed edge, extra purchased surface, tub/pan/partition or drain location.':'')+
  (missingSourceBasins.length?' '+missingSourceBasins.length+' native countertop record(s) have NO attributable native basin insertion: centered generic basin suppressed, 3D BASIN UNLOCATED; do not assume number, position or selected sink family.':'')+
  (unlocatedNativeBasins.length?' '+unlocatedNativeBasins.length+' native countertop/plumbing association(s) fail illustrative basin footprint containment: PLAN-XY ring marker raised above source native elevation for visibility only, BASIN 3D UNLOCATED; native 3D insertion NOT represented by ring height.':'')+
  (symbolGate.suppressed?' '+symbolGate.suppressed+' diagram fixture(s) rendered as 2D UNLOCATED source markers because native boundary/hosted-door overlap made a 3D placement misleading.':'');
 modelInfo.textContent=(reconstructed?'Registered wall-face geometry ':'Drawing-only envelope ')+
  w.toFixed(2)+' Ã— '+d.toFixed(2)+' ft Â· ceiling '+ceiling.toFixed(2)+
  ' ft Â· '+(reconstructed?reconstructed.walls+' wall segments / '+reconstructed.doors+' native openings':'entry wall outlined')+
  (arch?.area_conflict_flag?' Â· DRAWING AREA CONFLICT '+arch.drawing_vs_wall_face_difference_percent.toFixed(1)+'%':'');
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
 const r069DrawingWetLights=drawR069WetStudyOpticalDepth(room);
 addMarker();
 const desc=kind==='WALK_IN_SELECTED'?'Selected WALK-IN; footprint is 5.0 Ã— 2.54 ft drawing-derived. Drain location / four-plane slope NOT modeled.':
 kind==='DURAVIT_TUB_SELECTED'?'Selected Duravit TUB; dimensions indicate alcove only. Tub family and pan are NOT modeled.':
 kind==='TUB_OR_WALK_IN_UNSELECTED'?'TUB/WALK-IN unselected. No pan or tub geometry invented; floor shown as neutral source footprint.':
 kind==='PRIMARY_WALK_IN_LINEAR'?'Primary wet walls remain neutral; 48-inch factory-solid linear drain location and wet overhead not mapped.':
 kind==='DRY_WOOD'?'Dry vanity WALL only. Existing WOOD floor retained; no room slab dimensions available.':
 'Source wall segment only; no guessed room floor or plumbing fixtures.';
 modeInfo='SOURCE-DIMENSIONED DRAWING STUDY â€” not a Revit room reconstruction. '+desc+
 (r069DrawingWetLights?' R069 '+r069DrawingWetLights+' optical ceramic joint-depth fade(s) parented to DRAWING-DIMENSIONED selected W1/W2/W3 plane(s); no additional installed wall, wet-zone geometry, tile area or pan.':'')+
 (floorP?' The separate bordered 2Ã—2-ft LEVEL tile swatch is UNLOCATED MATERIAL-ONLY, not a second floor/PAN area or purchase.':'');
 modelInfo.textContent='W1 '+actualWidth.toFixed(2)+' ft'+(d>0?' Â· wet-zone depth '+d.toFixed(2)+' ft':'')+
  ' Â· '+height.toFixed(2)+' ft height Â· floor outline unverified';
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
// R069 link full-room drawing-registered source wall-face polygons to the
// ACTUAL REFERENCE FRAME of the read-only Revit level AABBs. The native
// origin is preserved; never call the shape a real OST_Rooms boundary.
// No source-local wall/counter/fixture coordinate, room membership, imported
// model or frozen tile assignment changes. 310 is a separate subdued locator.
function drawR069LevelContextRoomLocator(inst,anchor){
 if(!(R069_FOCUS.has(current()?.id)||R070_DRY_FOCUS.has(current()?.id)))return 0;
 const arch=inst?.architecture,origin=arch?.origin_native_xy_ft;
 if(!origin?.length||!arch.floor_polygon_local_xz_ft?.length)return 0;
 let placed=0;
 for(const [which,poly] of [
  ['MAIN',arch.floor_polygon_local_xz_ft],
  ['ADJACENT_310',arch.adjacent_zone_geometry?.floor_polygon_local_xz_ft||[]]]){
  if(poly.length<3)continue;
  const points=poly.map(p=>[origin[0]+p[0]-anchor[0],
   origin[1]-p[1]-anchor[1]]);
  const shape=new THREE.Shape();shape.moveTo(points[0][0],-points[0][1]);
  for(let i=1;i<points.length;i++)shape.lineTo(points[i][0],-points[i][1]);
  shape.closePath();
  const face=new THREE.Mesh(new THREE.ShapeGeometry(shape),
   new THREE.MeshBasicMaterial({color:which==='MAIN'?0x8ab7ae:0x94a4ae,
    transparent:true,opacity:which==='MAIN'?.20:.075,
    depthWrite:false,side:THREE.DoubleSide}));
  face.rotation.x=-Math.PI/2;face.position.y=.052;
  face.renderOrder=3;
  face.userData={category:R070_DRY_FOCUS.has(current()?.id)?
    'ARCH_R070_CONTEXT_REGISTERED_LOCATOR':'ARCH_R069_CONTEXT_REGISTERED_LOCATOR',
   instance:inst.room_number,compartment:which,
   native_origin_xy_ft:origin,actual_level_anchor_ft:anchor,
   r069_mapped_back_to_native_model_coordinates:true,
   native_room_element_id:null,room_name_membership_certified:false,
   not_a_revit_floor_solid:true,not_a_floor_purchase_area:true,
   selected_tile_applied:false,
   source:'Derived source wall-face polygon registered into real native level AABB XYZ coordinates via original read-only model origin. Named-room assignment drawing-inferred; not a native OST_Rooms element or tile purchase footprint. 310 context separate.'};
  modelGroup.add(face);renderObjects.push(face);
  const edge=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
   points.map(p=>new THREE.Vector3(p[0],.083,p[1]))),
   new THREE.LineBasicMaterial({color:which==='MAIN'?0xb4d2c2:0x7596a7,
    transparent:true,opacity:which==='MAIN'?.63:.19,depthTest:false}));
  edge.renderOrder=9;
  edge.userData={...face.userData,category:'ARCH_R069_CONTEXT_REGISTERED_EDGE'};
  modelGroup.add(edge);renderObjects.push(edge);placed++;
 }
 return placed;
}
function buildLegacyContext(room,inst){
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
 const r069RoomLocators=drawR069LevelContextRoomLocator(inst,anchor);
 addMarker(0x425e74);
 modeInfo='READ-ONLY REVIT LEVEL CONTEXT: actual native element bounds ('+
 Object.entries(counts).map(([k,n])=>k+' '+n).join(' Â· ')+
 '). R069 native-frame registered source-wall-face locator(s): '+r069RoomLocators+
 ' â€” drawing-inferred room association, NOT verified OST_Rooms. Native fixture/casework insertion markers: '+Object.values(insertions).reduce((a,b)=>a+b,0)+
 ' actual source points/rotations where valid. Room assignment unverified; markers are not fixture solids and NO tile is painted on unidentified Revit walls.';
 modelInfo.textContent=(inst?.room_number||room.id)+' Â· '+(inst?.level?.name||'UNKNOWN LEVEL')+
 ' Â· elevation '+Number(inst?.level?.elevation_ft).toFixed(2)+' ft Â· Level receipt '+(inst?.level?.receipt_id||'N/A');
}
function physicalBounds(){
 const b=new THREE.Box3();let hit=0;
 for(const o of renderObjects){if(!o.visible)continue;b.expandByObject(o);hit++;}
 return hit?b:null;
}
function setLegacyCamera(preset,force=true){
 state.preset=preset;
 const b=physicalBounds(),center=b?b.getCenter(new THREE.Vector3()):new THREE.Vector3(0,4,0);
 const ext=b?b.getSize(new THREE.Vector3()):new THREE.Vector3(8,8,8);
 if(state.mode==='full'&&state.room==='TX-BATH4'&&preset==='r066-tx4-counter'){
  const arch=instance()?.architecture;
  const c=arch?.native_casework_proxies?.[0];
  const poly=arch?.floor_polygon_local_xz_ft||[];
  if(c&&poly.length){
   const xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
   const cx=(Math.min(...xs)+Math.max(...xs))/2,
    cz=(Math.min(...zs)+Math.max(...zs))/2;
   const hand=c.local_center_xz_ft[0]>=cx?1:-1;
   // Exterior camera *frames the entire source room* with its one
   // verifiable ~2.48x1.5ft Countertop category AABB, not a close-up
   // floating over its surface that crops the adjoining toilet/door.
   // No occupied viewpoint, countertop fabrication or tub placement inferred.
   const target=new THREE.Vector3(cx+(c.local_center_xz_ft[0]-cx)*.38,
    3.25,cz+(c.local_center_xz_ft[1]-cz)*.22);
   camera.fov=46;orbit.target.copy(target);
   const r069Closer=R069_FOCUS.has(state.room)&&state.focusView;
   camera.position.set(target.x+hand*(r069Closer?12.4:13.8),
    target.y+(r069Closer?8.8:10.5),
    target.z+(r069Closer?12.7:14.1));
   camera.up.set(0,1,0);camera.near=.025;camera.far=1100;
   camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
   if(force)renderer.render(scene,camera);
   return;
  }
 }
 if(state.mode==='full'&&R063_FOCUS_BATHS.has(state.room)&&preset==='r063-bath-finish'){
  const arch=instance()?.architecture;
  const poly=arch?.floor_polygon_local_xz_ft||[];
  if(poly.length){
   const xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
   const loX=Math.min(...xs),hiX=Math.max(...xs),
    loZ=Math.min(...zs),hiZ=Math.max(...zs);
   const sourceTub=arch.selected_tub_proxy?.local_center_xz_ft;
   // R065 physical Focus screenshots showed the 9.16/9.25ft wall tops
   // cropped beneath the compact toolbar. Center on the real GWB underside
   // when matched, else use only the recorded drawing 9.25ft study datum.
   // Exterior review camera optics, NOT a new interior standing position.
   const studyCeiling=arch.native_ceiling_evidence?.underside_height_ft||9.25;
   const r068CloserBath2=R068_WET_FOCUS.has(state.room)&&
    current()?.program?.kind==='DURAVIT_TUB_SELECTED'&&state.focusView;
   const r069Bath3Focus=R069_FOCUS.has(state.room)&&state.focusView;
   const target=new THREE.Vector3(sourceTub?.[0]??(loX+hiX)/2,
    r069Bath3Focus?Math.min(3.65,Math.max(3.0,studyCeiling*.39)):
    r068CloserBath2?Math.min(3.55,Math.max(2.85,studyCeiling*.35)):
      Math.min(4.1,Math.max(3.4,studyCeiling*.43)),
    sourceTub?.[1]??(loZ+hiZ)/2);
   const placement=wetPlacementFromPlan(current(),instance());
   const hand=instance()?.plan_is_mirrored_B===true?-1:1;
   let dx=hand*.54,dz=1.17;
   // PH2 original SOUTH/front W1 is deliberately only 0.72ft high in
   // Full Bathroom; camera from the SOUTH opens a direct view over this
   // established reversible section instead of looking through a north
   // hosted door/opaque room partition. This is an EXTERIOR review camera.
   if(placement?.side==='front'){dx=hand*.64;dz=1.21;}
   if(placement?.side==='rear'){dx=hand*.55;dz=1.21;}
   if(placement?.side==='left'){dx=1.25;dz=hand*.54;}
   if(placement?.side==='right'){dx=-1.25;dz=hand*.54;}
   const magnitude=Math.hypot(dx,dz);
   // R068: smaller source-bounded selected Bath2 photoreview frames lift
   // the tub, selected ceramic and native hosted entry out of the tiny
   // distant 9ft-wall schematic. Only camera optics change; preserving
   // material areas, all wall/tub coordinates and A/B mirror relationship.
   const dist=r069Bath3Focus?
    Math.max(15.8,Math.min(18.4,Math.hypot(hiX-loX,hiZ-loZ)*1.65)):
    r068CloserBath2?
    Math.max(14.6,Math.min(18.0,Math.hypot(hiX-loX,hiZ-loZ)*1.52)):
    Math.max(17.4,Math.min(22.5,Math.hypot(hiX-loX,hiZ-loZ)*1.78));
   camera.fov=48;
   orbit.target.copy(target);
   camera.position.set(target.x+dist*dx/magnitude,
    target.y+dist*(r069Bath3Focus?.69:r068CloserBath2?.67:.83),
    target.z+dist*dz/magnitude);
   camera.up.set(0,1,0);camera.near=.025;camera.far=1100;
   camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
   if(force)renderer.render(scene,camera);
   return;
  }
  state.preset='isometric';preset='isometric';
 }
 if(state.mode==='full'&&current()?.program?.kind==='PRIMARY_WALK_IN_LINEAR'&&
   (preset==='r062-primary-vanity'||preset==='r062-primary-shell')){
  const arch=instance()?.architecture;
  const counter=arch?.native_casework_proxies?.[0];
  const poly=arch?.floor_polygon_local_xz_ft||[];
  if(counter&&poly.length){
   const q=counter.local_center_xz_ft;
   const xList=poly.map(p=>p[0]),zList=poly.map(p=>p[1]);
   const roomMidX=(Math.min(...xList)+Math.max(...xList))/2;
   const roomMidZ=(Math.min(...zList)+Math.max(...zList))/2;
   // The source-native counter's X side is unambiguous, but its true
   // manufactured FRONT, openings and installed cabinet height are NOT.
   // Camera location is outside the drawing-registered room, not a person.
   const inward=roomMidX>=q[0]?1:-1;
   const target=preset==='r062-primary-vanity'?
    new THREE.Vector3(q[0],(counter.min_height_ft+counter.max_height_ft)/2,q[1]):
    new THREE.Vector3(roomMidX,2.7,roomMidZ);
   const eye=preset==='r062-primary-vanity'?
    // Source native 9ft counter study has no physical standing viewpoint;
    // fit its FULL long-axis span rather than flying through the near wall
    // and cropping the ends/ceiling in a misleading close-up.
    new THREE.Vector3(q[0]+inward*(state.focusView?17.5:20.1),
     target.y+(state.focusView?11.5:13.0),q[1]+(state.focusView?9.5:10.7)):
    new THREE.Vector3(roomMidX+inward*18.5,target.y+15.7,roomMidZ-18.5);
   camera.fov=preset==='r062-primary-vanity'?48:46;
   orbit.target.copy(target);
   camera.position.copy(eye);camera.up.set(0,1,0);
   camera.near=.025;camera.far=1100;camera.updateProjectionMatrix();
   orbit.update();applyInteriorReveal();
   if(force)renderer.render(scene,camera);
   return;
  }
  state.preset='isometric';preset='isometric';
 }
 // PH4 includes a distinct 310 context compartment behind 311. Frame the
 // selected 311 bathroom from its actual inner-side entrance, not from the
 // outside of its shower wall; keep the separate 310 visible on orbit.
 const ph4Focus=state.mode==='full'&&state.room==='PH-BATH4'&&!nativeAuditInstalled;
 if(ph4Focus){center.set(0,3.4,-.55);ext.set(6.2,9.25,6.2);}
 if(state.mode==='full'&&R067_COMPACT_FOCUS.has(state.room)&&
   ['r060-counter','r060-wc','r067-powder-survey','r067-wc-survey'].includes(preset)){
  // R067 source-derived EXTERIOR review camera: the original high/near
  // r060 fixture zoom made these 3-7ft rooms look like an abstract shaft,
  // clipped tall wall tops and lost the WC/wood/counter relationship. Fit
  // native wall-face footprint and room GWB datum with a lower oblique view.
  // This is NOT an occupiable eye position, door swing/clearance or source
  // room geometry. Actual source camera/A-B wall coordinates stay untouched.
  const arch=instance()?.architecture,poly=arch?.floor_polygon_local_xz_ft||[];
  if(poly.length){
   const xs=poly.map(p=>p[0]),zs=poly.map(p=>p[1]);
   const loX=Math.min(...xs),hiX=Math.max(...xs),loZ=Math.min(...zs),hiZ=Math.max(...zs);
   const midX=(loX+hiX)/2,midZ=(loZ+hiZ)/2;
   const c=arch.native_casework_proxies?.[0],toilet=arch.toilet_proxy_anchor;
   const wc=room=>room==='PH-WC'||room==='TX-WC';
   const isWC=wc(state.room);
   const mirror=instance()?.plan_is_mirrored_B?-1:1;
   // A mirrored survey camera follows the photographed room's actual side;
   // TX-POWDER's countertop occupies the same source X end in both A/B.
   const counterX=c?.local_center_xz_ft?.[0]??midX;
   const sideForTxPowder=counterX<=midX?1:-1;
   const target=new THREE.Vector3(
    isWC?midX*.60+(toilet?.illustrative_proxy_center_xz_ft?.[0]??midX)*.40:
    midX*.66+counterX*.34,
    isWC?2.85:3.05,
    isWC?midZ*.76+(toilet?.illustrative_proxy_center_xz_ft?.[1]??midZ)*.24:
    midZ*.70+(c?.local_center_xz_ft?.[1]??midZ)*.30);
   const longX=hiX-loX>hiZ-loZ;
   let dx=mirror*.38,dz=-1.06;
   // The narrow 102 rooms have their SOURCE Countertop slab at the -X end.
   // Inspect from +X along the true long room axis so WC + source-only slab
   // both read; do not frame through the open hosted doorway as a blank hole.
   if(state.room==='TX-POWDER'){dx=sideForTxPowder*1.05;dz=.48;}
   // Enclosed WCs have no selected dry wall preview; see the source mirrored
   // toilet against the native rear enclosure from the hosted entry side.
   else if(isWC){dx=mirror*(longX?.46:.29);dz=1.03;}
   const radial=Math.hypot(dx,dz);
   const r070Focus=R070_DRY_FOCUS.has(state.room)&&state.focusView;
   const wcCeramicReview=r070Focus&&isWC&&
    ['r060-wc','r067-wc-survey'].includes(preset);
   const dist=wcCeramicReview?
     Math.max(9.8,Math.min(12.0,Math.hypot(hiX-loX,hiZ-loZ)*1.38)):
    Math.max(isWC?(r070Focus?14.7:12.8):(r070Focus?16.0:14.6),
     Math.min(isWC?19.8:21.2,
      Math.hypot(hiX-loX,hiZ-loZ)*(isWC?1.92:2.07)));
   // WC porcelain study reviews the generic source-gated bowl from a lower
   // exterior cutaway, not through a fictitious installed doorway or a
   // certified occupant eye location. Full ISO still frames entire 9ft
   // native enclosure. Native wall/fixture dimensions and section untouched.
   if(wcCeramicReview){
    target.y=1.72;
    target.x=toilet?.illustrative_proxy_center_xz_ft?.[0]??target.x;
    target.z=toilet?.illustrative_proxy_center_xz_ft?.[1]??target.z;
   }else if(r070Focus)target.y=Math.min(3.35,Math.max(2.9,
    arch.native_ceiling_evidence?.underside_height_ft*.34||3.10));
   camera.fov=wcCeramicReview?44:r070Focus?49:47;orbit.target.copy(target);
   camera.position.set(target.x+dist*dx/radial,
    target.y+dist*(wcCeramicReview?.36:r070Focus?(isWC?.55:.57):(isWC?.63:.67)),
    target.z+dist*dz/radial);
   camera.up.set(0,1,0);camera.near=.025;camera.far=1100;
   camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
   if(force)renderer.render(scene,camera);
   return;
  }
 }
 if(state.mode==='full'&&(preset==='r060-counter'||preset==='r060-wc')){
  const arch=instance()?.architecture;
  const counter=arch?.native_casework_proxies?.[0];
  const toilet=arch?.toilet_proxy_anchor;
  const isCounter=preset==='r060-counter';
  const p=isCounter?counter?.local_center_xz_ft:toilet?.illustrative_proxy_center_xz_ft;
  if(p){
   const point=new THREE.Vector3(p[0],isCounter?
    (counter.min_height_ft+counter.max_height_ft)/2:1.34,p[1]);
   // This is an exterior orthographic-like inspection azimuth, neither an
   // occupied interior eye position nor a native fixture orientation claim.
   const nativeVector=toilet?.illustrative_front_vector_local_xz;
   const axisX=isCounter?(counter.width_x_ft>=counter.depth_z_ft?0:1):
    (nativeVector?.[0]??0);
   const axisZ=isCounter?(counter.width_x_ft>=counter.depth_z_ft?1:0):
    (nativeVector?.[1]??1);
   const length=Math.max(8.5,Math.min(15,ext.length()*.86));
   camera.fov=43;
   orbit.target.copy(point);
   camera.position.set(point.x+axisX*length*.76+(instance()?.plan_is_mirrored_B?-.17:.17)*length,
    point.y+length*.80,point.z+axisZ*length*.76);
   camera.up.set(0,1,0);camera.near=.025;camera.far=1100;
   camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
   if(force)renderer.render(scene,camera);
   return;
  }
  // A countertop is not implied where the read-only Revit category lacks
  // one. Fall back to a conventional external overview, no false target.
  preset='isometric';state.preset=preset;
 }
 if(state.mode==='full'&&['wet','ph4-311','ph4-310'].includes(preset)){
  const inst=instance(),arch=inst?.architecture,room=current();
  const side=inst?.plan_is_mirrored_B===true?-1:1;
  let focus=new THREE.Vector3(0,3,0),eye=null;
  if(ph4Focus){
   // The two drawing-registers are distinct compartments. Source wall-face
   // XY polygons place 310 immediately behind the 311 wet compartment.
   // Camera presets are EXTERIOR, do not imply a native standing position.
   const p=arch?.floor_polygon_local_xz_ft||[];
   const q=arch?.adjacent_zone_geometry?.floor_polygon_local_xz_ft||[];
   const chosen=preset==='ph4-310'?q:p;
   if(chosen.length){
    const xx=chosen.map(v=>v[0]),zz=chosen.map(v=>v[1]);
    focus.set((Math.min(...xx)+Math.max(...xx))/2,
     (preset==='ph4-311'&&R069_FOCUS.has(state.room)&&state.focusView)?3.38:2.8,
     (Math.min(...zz)+Math.max(...zz))/2);
   }
   const hand=inst?.plan_shower_side==='left'?-1:1;
   const span=preset==='ph4-310'?16.4:
    (R069_FOCUS.has(state.room)&&state.focusView?13.0:12.5);
   // The 310 compartment is behind 311 on the architectural plan. Review
   // it from its own north/exterior side, not through 311's full-height tiled
   // wet wall. For 311, approach from the open sectional foreground.
   eye=preset==='ph4-310'?
    new THREE.Vector3(focus.x-hand*span*.52,focus.y+span*.76,
     focus.z-span*.88):
    // R069 311 wet selected W1 occupies the outer side; observing from
    // opposite inner/dry side exposes source floor and near tiled return.
    // Camera is an EXTERIOR section study, never a doorway/eye placement.
    new THREE.Vector3(focus.x-hand*span*.76,focus.y+span*.75,
     focus.z+span*.84);
  }else{
   const placement=wetPlacementFromPlan(room,inst);
   const poly=arch?.floor_polygon_local_xz_ft||[];
   if(poly.length){
    const xx=poly.map(v=>v[0]),zz=poly.map(v=>v[1]);
    focus.set((Math.min(...xx)+Math.max(...xx))/2,2.9,
     (Math.min(...zz)+Math.max(...zz))/2);
   }
   // Look towards, not FROM, the drawing-traced wet wall. The original
   // R057 cutaway remains active and fully reversible. Fixture locations
   // and a door/entry viewpoint are NOT inferred from this camera.
   const hand=(inst?.plan_is_mirrored_B===true?-1:1);
   const wet=placement?.side;
   let vx=hand*.74,vz=1.0;
   if(wet==='front'){vx=hand*.58;vz=-1.16;}
   if(wet==='rear'){vx=hand*.58;vz=1.16;}
   if(wet==='left'){vx=1.20;vz=.63;}
   if(wet==='right'){vx=-1.20;vz=.63;}
   const dist=Math.max(10.4,Math.min(22,Math.hypot(ext.x,ext.z)*1.34));
   eye=new THREE.Vector3(focus.x+dist*vx,focus.y+dist*.94,focus.z+dist*vz);
  }
  camera.fov=49;orbit.target.copy(focus);camera.position.copy(eye);
  camera.up.set(0,1,0);camera.near=.024;camera.far=1100;
  camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
  if(force)renderer.render(scene,camera);
  return;
 }
 if(preset==='fixture'&&state.mode==='full'){
  const arch=instance()?.architecture;
  // Source priority: source-wall-face-contained SELECTED nominal tub when
  // explicitly fitted (never TX4); otherwise the actual Revit casework AABB.
  // A conditional/unselected bath program cannot acquire a selected tub.
  const tub=arch?.selected_tub_proxy?.local_center_xz_ft;
  const counter=arch?.native_casework_proxies?.[0]?.local_center_xz_ft;
  const toilet=arch?.toilet_proxy_anchor?.illustrative_proxy_center_xz_ft;
  const location=tub||counter||toilet;
  const target=new THREE.Vector3(location?.[0]??center.x,
   tub?1.4:counter?2.25:1.5,location?.[1]??center.z);
  const side=state.room==='PH-BATH4'?
   (instance()?.plan_entry_side==='left'?-1:1):
   (instance()?.plan_is_mirrored_B===true?-1:1);
  const distance=Math.max(7.8,Math.min(15,Math.max(ext.x,ext.z)*1.32));
  // A conditional TUB/WALK-IN pictogram at the forward wet-wall end should
  // be viewed from the opposite dry side. The prior front-right "focus"
  // camera put a tall selected W2/W3 tile preview between the owner and the
  // room. This remains an EXTERIOR architectural view, not a guessed doorway
  // or a constructed future shower installation.
  const conditional=current()?.program?.kind==='TUB_OR_WALK_IN_UNSELECTED';
  const eyeX=conditional?side*distance*.40:side*distance*.75;
  const eyeZ=conditional?-distance*1.10:distance*.95;
  camera.fov=47;
  orbit.target.copy(target);
  camera.position.set(target.x+eyeX,
   target.y+Math.max(7.3,distance*.86),target.z+eyeZ);
  camera.up.set(0,1,0);camera.near=.025;camera.far=1100;
  camera.updateProjectionMatrix();orbit.update();applyInteriorReveal();
  if(force)renderer.render(scene,camera);
  return;
 }
 if(preset==='interior'&&state.mode==='full'){
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
  const side=ph4Focus?(wetHand==='left'?-1:1):
   (instance()?.plan_is_mirrored_B===true?-1:1);
  // Back the cutaway camera outside the whole envelope far enough that its
  // near wall does not fill/bleach the full interactive canvas.
  const eye=new THREE.Vector3(focus.x+side*Math.max(10.8,ext.x*1.65),
   Math.max(14.5,ext.y*1.52),focus.z+Math.max(11.8,ext.z*1.65));
  camera.fov=55;
  orbit.target.copy(focus);
  camera.position.copy(eye);camera.up.set(0,1,0);
  camera.near=.023;camera.far=1100;camera.updateProjectionMatrix();
  orbit.update();applyInteriorReveal();if(force)renderer.render(scene,camera);
  return;
 }
 camera.fov=48;
 // Fit the entire tall 9'-3" wall set BELOW the scene overlays, rather than
 // filling and clipping the upper viewport like the original contextual preview.
 // Source context spans a whole building wing; the old 85-ft distance cap
 // clipped its outer actual bounds. Fit the full source AABB diagonal to the
 // camera's real vertical FOV, without changing a single Revit coordinate.
 const r067CompactIso=state.mode==='full'&&state.focusView&&
  R067_COMPACT_FOCUS.has(state.room)&&preset==='isometric';
 const r070DryIso=state.mode==='full'&&state.focusView&&
  R070_DRY_FOCUS.has(state.room)&&preset==='isometric';
 const r069FocusIso=state.mode==='full'&&state.focusView&&
  R069_FOCUS.has(state.room)&&preset==='isometric';
 const r068WetIso=state.mode==='full'&&state.focusView&&
  R068_WET_FOCUS.has(state.room)&&preset==='isometric';
 const R=state.mode!=='context'
  ?Math.max(7.8,Math.min(45,ext.length()*(r070DryIso?1.44:r067CompactIso?1.23:
   r069FocusIso?1.36:r068WetIso?1.32:state.mode==='full'?1.56:1.48)))
  :Math.max(75,Math.min(350,ext.length()/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2)))*1.25));
 const entrySide=instance()?.plan_entry_side;
 // For 12 source-plan-mirrored A/B pairs, mirror the exterior review
 // azimuth instead of looking through the opposite unit's high wall.
 // PH4 instead follows its independently documented 311 entrance side.
 const innerX=ph4Focus?(entrySide==='left'?-1:1):
  (instance()?.plan_is_mirrored_B===true?-1:1);
  const u=(preset==='front')?new THREE.Vector3(.1,.10,1):
  (preset==='top')?new THREE.Vector3(.01,1,.012):
  (preset==='side')?new THREE.Vector3(1,.13,.1):
   state.mode==='full'?new THREE.Vector3(innerX*.80,r070DryIso?.76:1.03,1.0):
   new THREE.Vector3(.80,.55,1.0);
 u.normalize().multiplyScalar(R);
 orbit.target.copy(center);
 camera.position.copy(center).add(u);
 camera.up.set(0,1,0);
 camera.near=Math.max(.015,R/1000);camera.far=1100;camera.updateProjectionMatrix();
 orbit.update();
 applyInteriorReveal();
 if(force)renderer.render(scene,camera);
}
// A/B mini plans are generated from the very same registered local wall-face
// polygons and native fixture/hosted-opening coordinates as the 3D scene.
// No unrecorded width, door swing, toilet solid or clearance is drawn.
function makeABSourcePlan(inst,idx){
 const arch=inst?.architecture;
 if(!arch?.floor_polygon_local_xz_ft?.length)
  return '<div class="viewer-ab-card">No source-registered wall-face polygon for '+htmlEscape(inst?.room_number)+'</div>';
 const main=arch.floor_polygon_local_xz_ft,adj=arch.adjacent_zone_geometry;
 const loops=[main,...(adj?.floor_polygon_local_xz_ft?.length?[adj.floor_polygon_local_xz_ft]:[])];
 const points=loops.flat(),xs=points.map(p=>p[0]),zs=points.map(p=>p[1]);
 const loX=Math.min(...xs),hiX=Math.max(...xs),loZ=Math.min(...zs),hiZ=Math.max(...zs);
 const scale=Math.min(205/Math.max(.6,hiX-loX),164/Math.max(.6,hiZ-loZ));
 const at=([x,z])=>[20+(x-loX)*scale,19+(z-loZ)*scale];
 const n=v=>Number(v).toFixed(2);
 const shape=(coords,fill,dash)=>'<polygon points="'+coords.map(p=>at(p).map(n).join(',')).join(' ')+
  '" fill="'+fill+'" stroke="#d4b78a" stroke-width="1.6" '+(dash?'stroke-dasharray="5 3"':'')+'/>';
 let svg=shape(main,'#657c8245',false);
 if(adj?.floor_polygon_local_xz_ft?.length)svg+=shape(adj.floor_polygon_local_xz_ft,'#4f74802a',true);
 for(const op of arch.openings||[]){
  if(!op.location_local_ft)continue;
  const [x,y]=at(op.location_local_ft);
  svg+='<circle cx="'+n(x)+'" cy="'+n(y)+'" r="4" fill="'+(op.kind==='window'?'#91cde3':'#edba88')+
   '" stroke="#17242e" stroke-width="1.1"><title>Native '+htmlEscape(op.kind)+' '+htmlEscape(op.id)+
   ' / host '+htmlEscape(op.host_id)+': insertion point only</title></circle>';
 }
 for(const c of arch.native_casework_proxies||[]){
  const ctr=c.local_center_xz_ft;
  if(!ctr)continue;
  const [x,y]=at([ctr[0]-c.width_x_ft/2,ctr[1]-c.depth_z_ft/2]);
  svg+='<rect x="'+n(x)+'" y="'+n(y)+'" width="'+n(c.width_x_ft*scale)+'" height="'+n(c.depth_z_ft*scale)+
   '" fill="#b1aa9c66" stroke="#e4c6a0" stroke-width="1"><title>Native countertop element AABB '+htmlEscape(c.id)+
   ', NOT actual furniture solid</title></rect>';
 }
 const wc=arch.toilet_proxy_anchor;
 if(wc?.local_native_insertion_xz_ft){
  const [x,y]=at(wc.local_native_insertion_xz_ft);
  svg+='<circle cx="'+n(x)+'" cy="'+n(y)+'" r="5" fill="none" stroke="#81d0db" stroke-width="2">'+
   '<title>Native toilet insertion '+htmlEscape(wc.native_plumbing_id)+'; NOT ceramic solid</title></circle>';
 }
 const tub=arch.selected_tub_proxy;
 if(tub?.local_center_xz_ft){
  const dims=tub.rotation_degrees===90?[tub.nominal_depth_ft,tub.nominal_width_ft]:
   [tub.nominal_width_ft,tub.nominal_depth_ft];
  const [x,y]=at([tub.local_center_xz_ft[0]-dims[0]/2,tub.local_center_xz_ft[1]-dims[1]/2]);
  svg+='<rect x="'+n(x)+'" y="'+n(y)+'" width="'+n(dims[0]*scale)+'" height="'+n(dims[1]*scale)+
   '" fill="none" stroke="#e0bd75" stroke-dasharray="4 2" stroke-width="1.4">'+
   '<title>Selected nominal tub footprint; drawing-calibrated, not a native bathtub insertion</title></rect>';
 }
 const side=inst.plan_is_mirrored_B===true?' / drawing mirrored B':'';
 const note=arch.selected_tub_unlocated_reason?' / selected tub 3D UNLOCATED':'';
 const currentMark=instance()?.room_number===inst.room_number?' (selected)':'';
 return '<div class="viewer-ab-card"><strong>'+htmlEscape(inst.room_number)+htmlEscape(currentMark)+'</strong>'+
  '<svg viewBox="0 0 245 205" role="img" aria-label="Source-derived plan for '+htmlEscape(inst.room_number)+
  '"><rect width="245" height="205" fill="#0d202b"/>'+svg+'</svg>'+
  '<small>'+htmlEscape(Number(arch.floor_polygon_area_ft2).toFixed(2))+
  ' SF source-wall-face derivation, NOT certified native Room. '+htmlEscape(arch.native_wall_ids?.length||0)+
  ' native wall IDs; '+htmlEscape(arch.openings?.length||0)+' hosted openings'+htmlEscape(side+note)+'.</small>'+
  '<button type="button" class="viewer-btn viewer-ab-open" data-idx="'+idx+'">View '+htmlEscape(inst.room_number)+' in 3D</button></div>';
}
function updateABCompare(){
 const el=document.getElementById('viewer-ab-drawer'),button=document.getElementById('viewer-compare-ab');
 el.hidden=!state.compareAB;
 button.setAttribute('aria-pressed',String(state.compareAB));
 button.textContent=state.compareAB?'Close A/B comparison':'Compare A/B';
 if(!state.compareAB)return;
 const r=current();
 el.innerHTML='<div style="font-size:12px;line-height:1.45;margin-bottom:10px"><strong>'+htmlEscape(r?.id)+
  '</strong> Â· A/B wall-face comparison from Nov 7 plan registration. Orange = hosted native door insertion; '+
  'cyan = toilet native insertion; sand box = countertop element AABB; dashed tub = nominal drawing-calibrated. '+
  'Dotted secondary polygon = separate adjacent compartment. No native Room IDs, swings or family solids asserted.</div>'+
  '<div style="display:flex;gap:10px;flex-wrap:wrap">'+
  (r?.physical_instances||[]).map((inst,i)=>makeABSourcePlan(inst,i)).join('')+'</div>';
 for(const b of el.querySelectorAll('.viewer-ab-open'))b.onclick=()=>{
  state.instance=Number(b.dataset.idx);state.surface=-1;updateInstanceSelect();rebuild();
 };
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
  s.textContent=prod.name+(/niche/i.test(prod.surface)?' Â· location unknown':'');
  t.append(h,s);row.append(image,t);b.append(row);b.onclick=()=>selectMaterial(index);
  list.append(b);
 });
 const alt=document.getElementById('alternative');alt.disabled=!r.alternative;alt.checked=state.alt&&!!r.alternative;
 document.getElementById('alternative-label').textContent=r.alternative?(state.alt?'Unselected preview':'Compare unselected'):'Not available';
 document.getElementById('spec-title').textContent=r.id+' Â· '+(state.alt?'Historic unselected alternative':r.has_pick?'Frozen current picks':'No pick yet');
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
  '<a href="'+htmlEscape(p.url)+'" target="_blank" rel="noopener noreferrer">Official product page â†—</a>';
}
function showLegacyNativeElement(x){
 selectedRevit.hidden=false;selectedRevit.open=true;
 const p=x.location?.point,b=x.bounds_ft;
 const point=Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)?
  p.map(v=>v.toFixed(3)).join(', ')+' ft (native X,Y,Z)':'not returned';
 const rotation=Number.isFinite(x.location?.rotation_radians)?
  (x.location.rotation_radians*180/Math.PI).toFixed(2)+'Â°':'not returned';
 const range=b?.min&&b?.max?
  b.min.map(v=>Number(v).toFixed(3)).join(', ')+' â†’ '+b.max.map(v=>Number(v).toFixed(3)).join(', ')+' ft':'not returned';
 const wallEnds=x.native_location?.start&&x.native_location?.end?
  x.native_location.start.map(v=>Number(v).toFixed(4)).join(', ')+' â†’ '+
  x.native_location.end.map(v=>Number(v).toFixed(4)).join(', ')+' ft':'not available';
 const openingSpan=Number.isFinite(x.nominal_width_ft)&&Number.isFinite(x.rendered_width_ft)?
  '<div><strong>Opening NOMINAL family type:</strong> '+htmlEscape((x.nominal_width_ft*12).toFixed(2))+
   ' in width Ã— '+htmlEscape((x.nominal_height_ft*12).toFixed(2))+' in height</div>'+
  '<div><strong>Actual DISPLAYED study span:</strong> '+htmlEscape((x.rendered_width_ft*12).toFixed(2))+
   ' in width Ã— '+htmlEscape((x.rendered_height_ft*12).toFixed(2))+
   ' in height Â· '+htmlEscape(x.visual_classification||'unclassified')+'</div>'+
  '<div><strong>Visual height limit:</strong> '+htmlEscape(x.clipped_by_visual_cutaway?'CLIPPED':'not clipped')+
   '; <strong>Inferred wall-face end:</strong> '+htmlEscape(x.clipped_by_inferred_face?'CLIPPED':'not clipped')+
   '. Missing nominal span is UNRESOLVED; NEVER a certified rough opening, construction-clear width or hinge/swing.</div>':'';
 document.getElementById('viewer-v2-element-detail').innerHTML=
  '<div><strong>ID:</strong> '+htmlEscape(x.revit_id)+' Â· '+htmlEscape(x.family_name||x.category)+'</div>'+
  '<div><strong>Revit native bounds:</strong> '+htmlEscape(range)+'</div>'+
  '<div><strong>Revit wall centerline endpoints:</strong> '+htmlEscape(wallEnds)+'</div>'+
  '<div><strong>Derived wall thickness:</strong> '+htmlEscape(x.thickness_ft??'not available')+' ft</div>'+
  '<div><strong>Insertion location:</strong> '+htmlEscape(point)+'</div>'+
  '<div><strong>Native rotation:</strong> '+htmlEscape(rotation)+'</div>'+
  '<div><strong>Host element:</strong> '+htmlEscape(x.host_id??'not returned')+'</div>'+
  '<div><strong>Read-only receipt:</strong> '+htmlEscape(x.receipt_id||'missing')+'</div>'+
  openingSpan+
  '<div><strong>Spatial room association:</strong> UNVERIFIED. Bounding boxes and native location markers are not family solids or room boundaries.</div>';
 modelInfo.textContent='Revit '+x.revit_id+' Â· '+(x.family_name||x.category)+' Â· room match UNVERIFIED';
}
 const wallCats=new Set(['sourceWall','revit_walls','FULL_ROOM_BOUNDARY','FULL_ROOM_WET_WALL',
 'FULL_ROOM_WALL_MATERIAL_STUDY','DRAWING_FULL_ROOM_PERIMETER',
 'DRAWING_FULL_ROOM_PARTIAL_ENTRY_WALL','DRAWING_ADJACENT_BOUNDARY','ARCH_REGISTERED_WALL',
  'ARCH_HOSTED_DOOR_LEAF','ARCH_HOSTED_WINDOW','ARCH_VISUAL_CUTAWAY_UPPER_REMNANT',
  'ARCH_R062_NATIVE_HOST_REVEAL_VISUAL','ARCH_R063_NATIVE_HOST_FINISH_CORNER_SHADE']);
wallCats.add('ARCH_R067_SOURCE_HOSTED_DRY_FINISH_PREVIEW');
function applyWallVisibility(){
 for(const o of renderObjects){
  if(wallCats.has(o.userData.category))o.visible=state.walls;
 }
 document.getElementById('toggle-walls').textContent=state.walls?'Hide walls':'Show walls';
 document.getElementById('toggle-walls').setAttribute('aria-pressed',String(state.walls));
 if(nativeAuditInstalled)applyNativeViewState();
}
function applyCeilingPreview(){
 // The canopy appears only at individually corroborated source GWB elevations,
 // not as a manufactured native Revit profile. It never appears by default.
 const enabled=state.mode==='full'&&state.ceilingPreview&&state.walls;
 let shown=0;
 for(const o of renderObjects)if(o.userData?.category==='ARCH_R059_DERIVED_GWB_CEILING_CANOPY'){
  o.visible=enabled;
  if(enabled)shown++;
 }
 const b=document.getElementById('viewer-ceiling-preview');
 b.textContent='Ceiling '+(state.ceilingPreview?'ON':'OFF');
 b.setAttribute('aria-pressed',String(state.ceilingPreview));
 b.title='Reversible faint GWB underside at exact independent read-only ceiling AABB elevation (when matched), with XZ shaped only by inferred wall faces. '+shown+' drawn source-linked preview(s). No native Room profile, ceiling solid, soffit, light or selected overhead tile.';
 document.body.dataset.viewerCeilingCanopies=String(shown);
 if(nativeAuditInstalled)applyNativeViewState();
}
function applyInteriorReveal(){
 // R057: a reversible CAMERA-FACING SECTION of actual source-wall-derived
 // visual meshes. The wall line, thickness, host relationship, Revit
 // bounding height, analytical witnesses, and selected surfaces are NEVER
 // changed. This is not demolition, a physical lowered partition, a revised
 // hosted opening, or a native room-solid extraction.
 const active=state.mode==='full'&&state.walls&&state.interiorReveal;
 // R067 small-room EXTERIOR detail: 2.35ft front-wall remnant hid the
 // source-gated wall-hung-looking WC entirely. In Focus + selected physical
 // survey camera only, show an optical 1.12ft wall-base section. Reversible
 // Section OFF and ordinary ISO restore the exact existing native-height
 // boxes and hosted opening relationships. NOT a demolition/design change.
 const r067Detail=state.focusView&&R067_COMPACT_FOCUS.has(state.room)&&
  ['r060-counter','r060-wc','r067-powder-survey','r067-wc-survey'].includes(state.preset);
 const limit=r067Detail?1.12:2.35;
 const cameraFacing=o=>{
  const a=o.userData?.review_outward_xz,p=o.userData?.review_face_midpoint_xz_ft;
  if(!a||!p)return false;
  const vx=camera.position.x-p[0],vz=camera.position.z-p[1];
  const magnitude=Math.hypot(vx,vz);
  return magnitude>.01&&(vx*a[0]+vz*a[1])/magnitude>.26;
 };
 let cuts=0,hiddenWet=0;
 for(const o of renderObjects){
  const u=o.userData||{};
  if(u.category==='ARCH_REGISTERED_WALL'&&u.review_outward_xz){
   const facing=active&&cameraFacing(o);
   const y0=u.review_original_bottom_ft,y1=u.review_original_top_ft;
   const shownTop=facing?Math.max(y0,Math.min(y1,limit)):y1;
   o.position.y=(y0+shownTop)/2;
   o.scale.y=(shownTop-y0)/(y1-y0);
   o.visible=state.walls&&shownTop>y0+.015;
   u.review_rendered_top_ft=shownTop;
   u.review_cutaway_only=facing&&shownTop<y1-.001;
   u.r067_photo_section_height_ft=r067Detail?limit:null;
   if(u.review_cutaway_only)cuts++;
   if(u.review_ghost){
    const remnant=u.review_ghost;
    const height=y1-shownTop;
    remnant.visible=state.walls&&u.review_cutaway_only&&height>.035;
    remnant.position.set(o.position.x,(shownTop+y1)/2,o.position.z);
    remnant.scale.y=Math.max(.001,height);
    remnant.userData.rendered_start_y_ft=shownTop;
    remnant.userData.rendered_end_y_ft=y1;
   }
   }else if((u.category==='ARCH_HOSTED_DOOR_LEAF'||u.category==='ARCH_HOSTED_WINDOW'||
     u.category==='ARCH_R062_NATIVE_HOST_REVEAL_VISUAL')&&u.review_outward_xz){
   const hide=active&&cameraFacing(o);
   o.visible=state.walls&&!hide;
   u.review_visual_hidden_only=hide;
  }else if((u.category==='FULL_ROOM_WET_WALL'||u.category==='ARCH_R063_NATIVE_HOST_FINISH_CORNER_SHADE')&&
    u.source_return_supported&&
    u.review_return_outward_xz&&u.review_return_face_midpoint_xz_ft){
    // R061: selected finish adhered to a camera-facing SOURCE native wall
    // cannot remain a 7.75ft free-standing sheet when that very host wall
    // is visually sectioned to 2.35ft. Clip only the display triangle strip
    // on that camera side, not the frozen wet-wall height or applied area.
    const hostFacing=cameraFacing({userData:{
      review_outward_xz:u.review_return_outward_xz,
      review_face_midpoint_xz_ft:u.review_return_face_midpoint_xz_ft}});
    const full=u.review_return_full_height_ft;
    const wetReview=state.preset==='wet'||state.preset==='ph4-311';
    const shown=active&&hostFacing&&!wetReview?Math.min(full,limit):full;
    o.scale.y=full>.001?shown/full:1;
    o.position.y=shown/2;
    o.visible=state.walls&&!(wetReview&&u.full_height_return_normal_review);
    u.review_return_rendered_height_ft=shown;
    u.review_return_section_only=shown<full-.001;
  }else if(u.category==='ARCH_R059_FULL_HEIGHT_FINISH_REVIEW'){
   // A distinct visual-only counterpart, not an additional applied tile
   // plane or material quantity. PH2 front W1/returns or PH4 311 W3.
   o.visible=state.mode==='full'&&state.walls&&state.preset==='wet';
  }else if(u.category==='FULL_ROOM_WET_WALL'&&u.cutaway_only_visualization&&
   state.preset==='wet'){
   o.visible=false;
  }else if(u.category==='FULL_ROOM_WET_WALL'&&u.wall==='W1'){
   // Front-facing tall tile study faces sometimes hide the very fixture they
   // describe. Hide ONLY the view-facing W1 overlay, keep W2/W3 and ALL source
   // records intact. Wet-Zone Study is unaffected and preserves full heights.
   const side=u.plan_placement;
   const h=o.geometry?.parameters?.height||0;
   const near=side==='front'?camera.position.z>0:
    side==='rear'?camera.position.z<0:
    side==='left'?camera.position.x<0:
    side==='right'?camera.position.x>0:false;
   const hide=active&&near&&h>3.5;
   // A wet-wall inspection intentionally keeps the actual selected-tile
   // preview surface visible. The earlier camera-facing section sometimes
   // hid precisely the one W1 tile plane the owner wanted to inspect.
   const keepForMaterialStudy=state.preset==='wet'||state.preset==='ph4-311';
   o.visible=state.walls&&(!hide||keepForMaterialStudy);
   if(u.cutaway_only_visualization&&keepForMaterialStudy)o.visible=false;
   u.review_visual_hidden_only=hide;
   if(hide&&!keepForMaterialStudy)hiddenWet++;
  }
 }
 const button=document.getElementById('viewer-reveal-interior');
 button.textContent='Interior reveal '+(state.interiorReveal?'ON':'OFF');
 button.setAttribute('aria-pressed',String(state.interiorReveal));
 button.title='R057 reversible 2.35 ft camera-facing section of wall visualization; '+cuts+
  ' source-derived wall pieces shortened and '+hiddenWet+
  ' view-facing wet W1 overlays hidden in current view. Native wall/opening evidence and frozen quantities unchanged.';
 document.body.dataset.viewerInteriorReveal=String(state.interiorReveal);
 document.body.dataset.viewerRevealCuts=String(cuts);
 document.body.dataset.viewerRevealWetHidden=String(hiddenWet);
 document.body.dataset.viewerR067SectionFt=String(r067Detail?limit:0);
 if(nativeAuditInstalled)applyNativeViewState();
}
orbit.addEventListener('change',()=>{if(state.mode==='full')applyInteriorReveal();});
const analyticalSourceTraceCats=new Set([
 'ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS','ARCH_NATIVE_WINDOW_FAMILY_AABB_WITNESS',
 'ARCH_NATIVE_TOILET_FAMILY_AABB_WITNESS','ARCH_NATIVE_GWB_AABB_WITNESS',
 'ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS','ARCH_HOSTED_OPENING_NOMINAL_TRACE',
 'ARCH_NATIVE_PLUMBING_INSERTION_WITNESS','ARCH_NATIVE_FIXTURE_2D_LOCATOR',
  'ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR','ARCH_NATIVE_UNSELECTED_PLUMBING_LOCATOR',
  'ARCH_R061_UNSELECTED_PLAN_LABEL','ARCH_R062_PRIMARY_WET_UNLOCATED_PLAN_TRACE']);
function applySourceTraceVisibility(){
 for(const o of renderObjects)if(analyticalSourceTraceCats.has(o.userData?.category)||
  o.userData?.primary_source_only||
  o.userData?.category==='ARCH_R059_310A_UNATTRIBUTED_CASEWORK_WITNESS')
  o.visible=state.sourceTraces;
 const button=document.getElementById('viewer-toggle-source-traces');
 button.textContent='Source traces '+(state.sourceTraces?'ON':'OFF');
 button.setAttribute('aria-pressed',String(state.sourceTraces));
 // Hide only analytical outlines and markers, not walls, tiles, fixtures,
 // user material picks or the source metadata retained in room evidence.
 if(completionInstalled)applyFixtureStudyVisibility();
 if(nativeAuditInstalled)applyNativeViewState();
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
   ' Â· read-only receipt '+htmlEscape(x.native_anchor_receipt_id)+
   '</div><div><strong>Native insertion ft:</strong> '+htmlEscape(x.native_anchor_coordinate_ft)+
   '</div><div><strong>3D proxy projected:</strong> '+htmlEscape(x.illustrative_offset_from_anchor_ft)+
   ' ft inward, illustrative ONLY, not actual fixture center or rough-in.</div>':'')+
  '<div><strong>Fixture identification:</strong> NOT a native Revit family; NO confirmed SKU, exact dimensions, rough-in, clearance or installation coordinate.</div>'+
  (/reference/.test(x.kind)?'<div><strong>Program:</strong> The drawing pictogram DOES NOT select the undecided tub/walk-in branch.</div>':'');
 modelInfo.textContent='Architectural drawing '+x.kind+' diagram Â· source-relative placement only';
}
function rebuild(){
 const room=current(),inst=instance();
 if(nativeAuditInstalled)nativeRendered=[];
 if(!room)return;
 const registered=inst?.architecture;
 const revision=++rebuildRevision;
 document.body.dataset.viewerMaterials='LOADING';
 clearGeometry();updateViewConstraints(state.mode);selectedRevit.hidden=true;selectedRevit.open=false;
 modelInfo.textContent='';
 if(state.mode==='full')buildFullRoom(room);
 else if(state.mode==='study')buildStudy(room);
 else buildContext(room,inst);
 document.getElementById('room-title').textContent=room.id+' Â· '+(room.title||room.id);
 const nr=inst?.room_number||room.id;
 document.body.dataset.viewerRoom=room.id;
 document.body.dataset.viewerInstance=nr;
 document.body.dataset.viewerMode=state.mode;
 for(const id of ['viewer-ph4-focus-311','viewer-ph4-focus-310']){
  document.getElementById(id).hidden=room.id!=='PH-BATH4'||state.mode!=='full';
 }
 document.getElementById('viewer-camera-wet').hidden=state.mode==='context';
 document.getElementById('viewer-r060-counter-focus').hidden=state.mode!=='full'||
  !registered?.native_casework_proxies?.length;
 const primaryFocus=state.mode==='full'&&room.program?.kind==='PRIMARY_WALK_IN_LINEAR';
 document.getElementById('viewer-r062-primary-vanity').hidden=!primaryFocus;
 document.getElementById('viewer-r062-primary-shell').hidden=!primaryFocus;
 document.getElementById('viewer-r063-bath-finish').hidden=state.mode!=='full'||!R063_FOCUS_BATHS.has(room.id);
 document.getElementById('viewer-r060-wc-focus').hidden=state.mode!=='full'||
  !registered?.toilet_proxy_anchor;
 document.getElementById('viewer-ceiling-preview').hidden=state.mode!=='full';
 document.getElementById('room-description').textContent=
  nr+' / '+(inst?.level?.name||'level unknown')+' (native elevation; room-number mapping inferred). '+
  (state.mode==='full'?(registered?'Architecture from read-only native wall curves and hosted openings; room ID drawing-inferred, not certified Revit room.':
    'Entire bathroom envelope reconstructed from floor-plan study, approximate and NOT a measured Revit room.'):
   state.mode==='study'?'Dimensioned wet-zone-only surface study, not BIM-native room solids.':
   'Read-only level-context bounding geometry, not bathroom-specific walls.');
 document.getElementById('confidence').textContent=state.mode==='full'?(registered?'Native wall lines / inferred room':'Full room / drawing study'):
  state.mode==='study'?'Wet-zone / unlocated':'Revit bounds / unassigned';
 document.getElementById('model-count').textContent=renderObjects.length+
  ' physical study/model objects Â· '+nr+' Â· '+(room.program?.kind||'program unverified');
 const alert=document.querySelector('.alert');
 alert.textContent=state.mode==='full'?(registered?'FULL BATHROOM Â· NATIVE WALL-FACE STUDY':'FULL BATHROOM Â· PLAN-STUDY GEOMETRY'):
  state.mode==='study'?'WET-ZONE DETAIL Â· NOT VERIFIED':'REVIT BOUNDS Â· ROOM UNVERIFIED';
 const programs=room.program||{};
 programLabel.innerHTML='<strong>Selected program:</strong> '+htmlEscape(programs.plumbing_truth||'Not mapped')+
  '<div><strong>Scope:</strong> '+htmlEscape(programs.scope_truth||'Unknown')+'</div>'+
  '<div>Two physical rooms represented separately. No native fixture-to-room mapping verified. Owner approvals: ZERO.</div>'+
  (room.id==='TX-PRIMARY'?'<div><strong>R058 drawing/program distinction:</strong> Nov 7 A2.1 second-floor plan carries a tub-shaped bathing pictogram; the FROZEN current primary program is WALK-IN with 48-inch factory-solid linear drain. No bathtub, drain center, glass, pan slope, or rough-in added from that drawing.</div>':'')+
  (programs.kind==='TUB_OR_WALK_IN_UNSELECTED'?'<div><strong>R058 UNSELECTED BRANCH:</strong> Tub drawing pictogram is a 2D reference only, not a chosen tub solid, tiled PAN or installed fixture.</div>':'')+
  (registered?.selected_tub_unlocated_reason?'<div><strong>R058 SELECTED TUB 3D UNLOCATED:</strong> Duravit 700332000000090 (59 Ã— 29.5 in) retained as selected; its 3D footprint is withheld by original native wall/toilet/door/counter collision gates. Do not read a ring as a physical tub location.</div>':'');
 const primarySheetBath=R068_PRIMARY_BATH_SHEET[room.id]||null;
 if(primarySheetBath)programLabel.innerHTML+=
  '<div><strong>R068 separate plumbing schedule â€” BATHTUB 3D UNLOCATED:</strong> '+
  htmlEscape(primarySheetBath.manufacturer)+' '+htmlEscape(primarySheetBath.description)+
  ' Â· SKU '+htmlEscape(primarySheetBath.model_or_sku)+
  ' Â· source row '+htmlEscape(primarySheetBath.source_row_id)+
  '. SOURCE STATUS: '+htmlEscape(primarySheetBath.status)+
  '. This is a sheet-listed item, NOT a located/approved tub in the existing WALK-IN program. No 3D tub, drain, selected installation or manufacturer solid modeled.</div>';
 if(primaryFocus)programLabel.innerHTML+=
  '<div><strong>R062 primary SOURCE HOLD:</strong> Selected WALK-IN and 48-inch factory-solid LINEAR drain remain the frozen program. The actual shower/linear drain installation and sink positions are not certified; source-bounded wet-envelope studies failing countertop, room-polygon or hosted-opening checks are 3D UNLOCATED. Wet-zone detail retains the historical dimensional study; no additional selected PAN, niche, slope, glazing or fabricated countertop openings. Use Primary vanity/Primary enclosure exterior cameras for the original source relationships.</div>';
 if(room.id==='PH-BATH4')programLabel.innerHTML+=
  '<div><strong>R059 two distinct spaces:</strong> 311 shower remains independently source-walled and has the original combined LEVEL/POINT PAN budget. 310A is WIC4 on the latest floor plan; nearby native fixture-category records are NOT certified closet contents and therefore show only as optional source traces. 310B is a separate Bath4 context with strictly illustrative bathroom fixtures. Use 311 shower / 310 context exterior cameras to examine each without combining floor areas.</div>';
 const s=room.wet_zone_schematic||{};
 const w=s.wall_segments||[];
 const claims=w.map(x=>htmlEscape(x.id)+' '+htmlEscape(x.length?.value??'unknown')+' ft ('+
      htmlEscape(x.length?.classification||'unclassified')+')').join('; ')||'None';
 const clippedOpenings=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_HOST_OPENING_DEPTH_WITNESS'&&
  o.userData.visual_classification==='VISUALLY_CLIPPED').map(o=>o.userData);
 const sourceWindows=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_WINDOW_FAMILY_AABB_WITNESS')
  .map(o=>o.userData);
 const sourceDoors=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_DOOR_FAMILY_AABB_WITNESS')
  .map(o=>o.userData);
 const unresolvedBasins=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR')
  .map(o=>o.userData);
 const sourceMissingBasins=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_CASEWORK_AABB_STUDY'&&
  o.userData?.basin_spatial_status).map(o=>o.userData);
 const unselectedBasinCounters=renderObjects.filter(o=>o.userData?.category==='ARCH_NATIVE_CASEWORK_AABB_STUDY'&&
   o.userData?.basin_program_status).map(o=>o.userData);
 const illustrativeVanityFaces=renderObjects.filter(o=>o.userData?.category==='ARCH_ILLUSTRATIVE_VANITY_FRONT_VISUAL')
  .map(o=>o.userData);
 const r063Floor=renderObjects.find(o=>o.userData?.category==='ARCH_REGISTERED_FLOOR');
 const r063Compact=renderObjects.filter(o=>o.userData?.category==='ARCH_R063_NATIVE_BOUND_COMPACT_VANITY_SIDE_STUDY');
 const r063FinishedCorners=renderObjects.filter(o=>o.userData?.category==='ARCH_R063_NATIVE_HOST_FINISH_CORNER_SHADE');
 const primaryWetEvidence=room.program?.kind==='PRIMARY_WALK_IN_LINEAR'&&registered?
  auditedPrimaryWetCandidate(registered,wetPlacementFromPlan(room,inst),
   registeredWetSupport(registered,wetPlacementFromPlan(room,inst),
    stdNum(room.wet_zone_schematic?.width)||0,stdNum(room.wet_zone_schematic?.depth)||0),
   stdNum(room.wet_zone_schematic?.width)||0,stdNum(room.wet_zone_schematic?.depth)||0):null;
 const missing=inst?.missing||['Room geometry not mapped'];
 document.getElementById('viewer-evidence-content').innerHTML=
  '<div><strong>Instance:</strong> '+htmlEscape(inst?.room_number||'unknown')+'</div>'+
  (primarySheetBath?'<div><strong>R068 PRIMARY SHOWER + SEPARATE SHEET-LISTED BATHTUB:</strong> '+htmlEscape(primarySheetBath.manufacturer)+
    ' '+htmlEscape(primarySheetBath.model_or_sku)+' Â· '+htmlEscape(primarySheetBath.description)+
    ' Â· Smartsheet source row '+htmlEscape(primarySheetBath.source_row_id)+
    ' Â· '+htmlEscape(primarySheetBath.status)+
    '. PROGRAM remains WALK-IN, 48in LINEAR drain type unchanged; no tub physical installation point, source AABB, cutout, drain, or fixture solid. Inferred room membership not certified.</div>':'')+
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
  (clippedOpenings.length?'<div><strong>VISUALLY CLIPPED opening DEPTH wires (not rough openings):</strong><ul style="padding-left:16px;margin:4px 0">'+
   clippedOpenings.map(o=>'<li>Room '+htmlEscape(o.room_number)+
    ', native opening '+htmlEscape(o.revit_id)+
    ' nominal '+htmlEscape((o.nominal_width_ft*12).toFixed(2))+'Ã—'+
    htmlEscape((o.nominal_height_ft*12).toFixed(2))+' in versus actually displayed '+
    htmlEscape((o.rendered_width_ft*12).toFixed(2))+'Ã—'+
    htmlEscape((o.rendered_height_ft*12).toFixed(2))+' in;'+
    (o.clipped_by_visual_cutaway?' visual height limit;':'')+
    (o.clipped_by_inferred_face?' source wall-face endpoint;':'')+
    ' missing nominal span UNRESOLVED, not a verified clear opening</li>').join('')+'</ul></div>':'')+
  (sourceWindows.length?'<div><strong>Actual native Revit window ELEMENT AABB witnesses (not window/glass solids):</strong><ul style="padding-left:16px;margin:4px 0">'+
   sourceWindows.map(o=>'<li>Window '+htmlEscape(o.revit_id)+
    ' hosted wall '+htmlEscape(o.host_id)+' Â· compartment '+htmlEscape(o.room_number)+
    ' Â· native category AABB '+htmlEscape(o.native_aabb_dimensions_ft.map(v=>v.toFixed(3)).join(' Ã— '))+
    ' ft (X Ã— Y-height Ã— Z-depth); nominal type opening and actual frame/glazing are DISTINCT; source receipt '+
    htmlEscape(o.receipt_id)+'</li>').join('')+'</ul></div>':'')+
  (sourceDoors.length?'<div><strong>Actual native Revit door ELEMENT AABB witnesses (NOT leaf solid, hinge arc or rough opening):</strong><ul style="padding-left:16px;margin:4px 0">'+
   sourceDoors.map(o=>'<li>Door '+htmlEscape(o.revit_id)+
    ', host wall '+htmlEscape(o.host_id)+' Â· compartment '+htmlEscape(o.room_number)+
    ' Â· native family category AABB '+htmlEscape(o.native_aabb_dimensions_ft.map(v=>v.toFixed(3)).join(' Ã— '))+
    ' ft X Ã— height Ã— depth; may contain symbolic swing/voids and is NOT a construction-clear width; source receipt '+
    htmlEscape(o.receipt_id)+'</li>').join('')+'</ul></div>':'')+
  (unresolvedBasins.length?'<div><strong>Native countertop / plumbing basin spatial HOLD:</strong><ul style="padding-left:16px;margin:4px 0">'+
   unresolvedBasins.map(o=>'<li>Countertop '+htmlEscape(o.revit_id)+
    ', plumbing '+htmlEscape(o.plumbing_reference_id)+
    ', receipt '+htmlEscape(o.plumbing_reference_receipt)+
    ': generic basin envelope extends beyond source countertop AABB. PLAN-XY locator (NOT native 3D point) raised to '+htmlEscape(o.displayed_locator_y_ft.toFixed(4))+
    ' ft above level from original native insertion elevation '+htmlEscape(o.source_plumbing_local_y_ft.toFixed(4))+
    ' ft; visual Y offset '+htmlEscape(o.visual_y_offset_from_source_ft.toFixed(4))+
    ' ft. 3D BASIN UNLOCATED. No source fixture solid, altered countertop cutout or verified installed clearance.</li>').join('')+'</ul></div>':'')+
  (sourceMissingBasins.length?'<div><strong>R058 countertop WITHOUT native basin coordinates:</strong><ul style="padding-left:16px;margin:4px 0">'+
   sourceMissingBasins.map(o=>'<li>Native casework/countertop element '+htmlEscape(o.revit_id)+
    ', receipt '+htmlEscape(o.receipt_id)+
    ': no attributable read-only native plumbing insertion. Generic previously centered 3D sink suppressed, basin 3D UNLOCATED; number, form and location remain unknown.</li>').join('')+'</ul></div>':'')+
   (unselectedBasinCounters.length?'<div><strong>R060 program-dependent basin HOLD:</strong> '+
    unselectedBasinCounters.map(o=>'native countertop '+htmlEscape(o.revit_id)+' '+htmlEscape(o.basin_program_status)).join('; ')+
    '. Nearby plumbing is evidence ONLY, not a source-verified selected basin. Any optional cyan ring under Source traces ON is a raised PLAN-XY locator, not a 3D native insertion, physical sink, faucet rough-in or countertop opening.</div>':'')+
  (illustrativeVanityFaces.length?'<div><strong>R058 visually complete vanity elevation (NOT native cabinetry):</strong> '+
   illustrativeVanityFaces.map(o=>'countertop '+htmlEscape(o.revit_id)+
    ' front long-axis '+htmlEscape(o.front_source_axis)+
    ', drawing-inferred, explicitly translucent non-source fascia').join('; ')+
   '. R059 fascia remains inside original Revit countertop category AABB in Z and does not reach the floor; no doors, toe-kicks, joinery, mounting method or material selection certified.</div>':'')+
  (primaryWetEvidence?'<div><strong>R062 SELECTED PRIMARY WALK-INâ€”3D SPATIAL REVIEW:</strong> '+
   htmlEscape(primaryWetEvidence.classification)+'. Candidate source-wall span '+
   htmlEscape(primaryWetEvidence.candidate_native_wall_id||'NOT MATCHED')+
   ', native countertop category overlap '+htmlEscape(primaryWetEvidence.counter_overlap_sf??'unknown')+
   ' SF (this is NOT an installation collision certificate); source native countertop IDs '+
   htmlEscape(primaryWetEvidence.native_countertop_conflicts?.join(', ')||'none')+
   ', hosted opening IDs '+htmlEscape(primaryWetEvidence.hosted_entry_conflicts?.join(', ')||'none')+
   ', polygon interior supported '+htmlEscape(primaryWetEvidence.polygon_support)+
   '. The drawing locator does not establish a physical installation, 48-inch drain location, wet tile pick or PAN slope; 3D study planes are withheld where source conflicts. Use Source traces ON for optional 2D extent.</div>':'')+
  (r063Floor?.userData.r063_floor_material_selected?'<div><strong>R063 source-scale floor finish:</strong> native-derived polygon uses original unnormalized XY feet-based UV; atlas repetition '+
   htmlEscape(r063Floor.userData.r063_map_repeat_per_source_ft?.map(x=>x.toFixed(4)).join(' Ã— '))+
   ' cycles per source foot for nominal '+htmlEscape(r063Floor.userData.r063_nominal_tile_size_ft?.join(' Ã— '))+
   ' ft tile; earlier room-size multiplication removed. This is a nominal-size IMAGE layout only; tile start, cut joints, supplier colors and grout approval remain UNSELECTED.</div>':'')+
  (r063Compact.length?'<div><strong>R063 compact source-bounded vanity legibility:</strong> '+
   htmlEscape(r063Compact.length/2)+' neutral study mass(es), two end faces and a floating underside inside each ORIGINAL native Countertop-category AABB. Source IDs '+
   htmlEscape([...new Set(r063Compact.map(x=>x.revit_id))].join(', '))+
   '. No actual cabinet family, support hardware, elevation, door, basin opening or selected cabinet material.</div>':'')+
  (r063FinishedCorners.length?'<div><strong>R063 source-native wet corner lighting:</strong> '+
   htmlEscape(r063FinishedCorners.length)+' VISUAL_ONLY falloff(s) entirely tied to the existing native-wall-backed W2/W3 finish planes. These are light/shadow gradients, not trim, new grout, extra tile faces, partitions, slopes or purchased areas.</div>':'')+
  (registered?.native_ceiling_evidence?'<div><strong>R059 reversible ceiling witness:</strong> height '+htmlEscape(registered.native_ceiling_evidence.underside_height_ft)+
   ' ft from separately matched GWB AABB; optional canopy XZ silhouette comes ONLY from inferred wall-face polygon, NOT a native ceiling trim profile or new tile coverage.</div>':'')+
  (registered?.toilet_proxy_anchor?'<div><strong>WC plumbing insertion anchor:</strong> '+htmlEscape(registered.toilet_proxy_anchor.native_plumbing_id)+
   '; proxy projection '+htmlEscape(registered.toilet_proxy_anchor.offset_from_native_insertion_ft)+
   ' ft is illustrative, not certified plumbing placement.</div>':'')+
  (registered?.native_ceiling_evidence?'<div><strong>Native GWB ceiling underside:</strong> '+htmlEscape(registered.native_ceiling_evidence.underside_height_ft)+
   ' ft above level Â· element '+htmlEscape(registered.native_ceiling_evidence.id)+
   ' Â· receipt '+htmlEscape(registered.native_ceiling_evidence.receipt_id)+
   '; room ceiling outline still drawing-inferred and 9.25ft drawn height not overwritten.</div>':'')+
  '<div><strong>Source drawing walls:</strong> '+claims+'</div>'+
  '<div><strong>Missing:</strong><ul style="padding-left:16px;margin:4px 0">'+
  missing.map(x=>'<li>'+htmlEscape(x)+'</li>').join('')+'</ul></div>';
 fidelity.textContent=modeInfo+(state.mode==='full'?
  (state.interiorReveal?' R057 INTERIOR REVEAL: view-facing wall meshes sectioned at 2.35 ft and, where occluding, W1 tile study hidden; source walls, openings and frozen material quantities untouched. Use Interior reveal OFF to restore the full presentation envelope.':
  ' R057 FULL PRESENTATION ENVELOPE: display-section suppression disabled; pre-existing documented fixed 305/311 cutaways remain.'): '');
 fidelity.title=fidelity.textContent;
 document.getElementById('viewer-mode-full').setAttribute('aria-pressed',String(state.mode==='full'));
 document.getElementById('viewer-mode-study').setAttribute('aria-pressed',String(state.mode==='study'));
 document.getElementById('viewer-mode-context').setAttribute('aria-pressed',String(state.mode==='context'));
 const inserts=document.getElementById('viewer-insertions');
 inserts.hidden=state.mode!=='context';
 inserts.setAttribute('aria-pressed',String(state.insertions));
 inserts.textContent='Native insertions '+(state.insertions?'ON':'OFF');
 applyWallVisibility();applySourceTraceVisibility();applyCeilingPreview();updateMaterials();setCamera(state.preset);updateABCompare();
 updateFocusViewControls();
 if(completionInstalled)updateCompletionPresentation(room,inst);
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
 if(r.id==='PH-BATH4'&&/^311[AB]$/i.test(parts[1]||''))parts[1]='310'+parts[1].slice(-1).toUpperCase();
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
function applyFocusArchitecturalPresentation(){
 // R065: keep ALL native wall and tile meshes. Suppress only analytical
 // outline/grid graphic layers when the owner opens immersive Focus, unless
 // Source lines is explicitly ON. Nothing is deleted or reclassified as a
 // Revit OST_Room. Plan/wet material modes and ordinary three-column review
 // retain their historical source evidence and camera behavior.
 const analytical=state.focusView&&!state.sourceTraces;
 const cues=new Set(['ARCH_FLOOR_FACE_OUTLINE','ARCH_CEILING_EXTENT_DATUM',
   'ARCH_INFERRED_ROOM_VERTICAL_WIRES']);
 for(const o of renderObjects)if(cues.has(o.userData?.category))o.visible=!analytical;
 const sourceWetHosts=new Set(renderObjects.filter(o=>
   o.userData?.category==='FULL_ROOM_WET_WALL'&&o.userData?.native_host_face_id)
  .map(o=>String(o.userData.native_host_face_id)));
 let opticallyRevealed=0;
 for(const wall of renderObjects){
  const u=wall.userData;
  if(u?.category!=='ARCH_REGISTERED_WALL'||!u.revit_id)continue;
  const reveal=analytical&&state.mode==='full'&&
    sourceWetHosts.has(String(u.revit_id));
  // Each matched host gets a separate material copy so OTHER native walls
  // retain their true viewer opacity.  This is only a REVERSIBLE STUDIO
  // TRANSPARENCY to expose existing selected W1/W2/W3 planes. No native
  // wall was shortened, demolished, removed or physically made translucent.
  if(reveal&&!u.r065_source_wall_private_material){
   const mat=wall.material.clone();
   mat.userData={...mat.userData,r065DisplayWallClone:true};
   wall.material=mat;
   u.r065_source_wall_private_material=true;
   u.r065_original_wall_opacity=mat.opacity;
  }
  if(u.r065_source_wall_private_material){
   const original=u.r065_original_wall_opacity;
   wall.material.opacity=reveal?Math.min(.42,original):original;
   u.r065_wet_host_photo_reveal=reveal;
   if(reveal)opticallyRevealed++;
  }
 }
 modelGroup.traverse(o=>{
  if(o.isGridHelper||o.type==='GridHelper')o.visible=!analytical;
 });
 document.body.dataset.viewerFocusArchitectural=String(analytical);
 document.body.dataset.viewerFocusWetHostReveals=String(opticallyRevealed);
 focusCaption.textContent=opticallyRevealed?
  'VIEWER-ONLY Â· Selected wet-host walls optically softened to expose frozen finish; source wall solids/IDs unchanged Â· Room attribution inferred':
  R068_PRIMARY_BATH_SHEET[current()?.id]?
   'VIEWER-ONLY Â· Primary WALK-IN + separately sheet-listed bathtub SKU; both 3D installation locations UNLOCATED Â· No native Room solid':
   'VIEWER-ONLY Â· Drawing-registered room faces; no certified Revit Room solids, source fixture families or owner approvals';
}
function updateLegacyFocusControls(){
 const room=current(),inst=instance();
 stage.classList.toggle('viewer-focus-active',state.focusView);
 document.body.dataset.viewerFocus=String(state.focusView);
 document.getElementById('viewer-focus-title').textContent=(room?.id||'Room')+' Â· '+(inst?.room_number||'?');
 document.getElementById('viewer-focus-level').textContent=
  (state.mode==='full'?'SOURCE WALL-FACE Â· ROOM INFERRED':
   state.mode==='study'?'DRAWING WET STUDY Â· UNLOCATED':'NATIVE AABB Â· NO ROOM ASSIGNMENT');
 const rooms=document.getElementById('viewer-focus-room');
 if(rooms.options.length!==ROOMS.length){
  rooms.replaceChildren();
  for(const r of ROOMS){const o=document.createElement('option');
   o.value=r.id;o.textContent=r.id;rooms.append(o);}
 }
 rooms.value=state.room;
 const units=document.getElementById('viewer-focus-instance');
 const numbers=[...(room?.physical_instances||[])].map(x=>String(x.room_number));
 if(units.options.length!==numbers.length||
   numbers.some((n,i)=>units.options[i]?.value!==n)){
  units.replaceChildren();
  for(const n of numbers){const o=document.createElement('option');
   o.value=n;o.textContent='Instance '+n;units.append(o);}
 }
 units.value=String(inst?.room_number||'');
 document.getElementById('viewer-focus-full').setAttribute('aria-pressed',String(state.mode==='full'));
 document.getElementById('viewer-focus-ab').setAttribute('aria-pressed',String(state.compareAB));
 document.getElementById('viewer-focus-traces').setAttribute('aria-pressed',String(state.sourceTraces));
 document.getElementById('viewer-focus-wet').disabled=state.mode==='context';
 const finish=document.getElementById('viewer-focus-finish');
 finish.hidden=state.mode!=='full'||!R063_FOCUS_BATHS.has(state.room);
 const architecture=document.getElementById('viewer-focus-architectural');
 const sourceAssemblyRooms=new Set(['PH-PRIMARY','TX-PRIMARY','PH-BATH4','TX-BATH4',
  'PH-POWDER','PH-WC','TX-POWDER','TX-POWDER2','TX-WC']);
 architecture.hidden=state.mode!=='full'||!sourceAssemblyRooms.has(state.room)||(nativeAuditInstalled&&state.room==='PH-BATH4');
 architecture.textContent=state.room==='PH-BATH4'?'311 shower':
  state.room==='TX-BATH4'?'Counter AABB':
  R067_COMPACT_FOCUS.has(state.room)?
   (state.room.endsWith('-WC')?'WC room':'Powder room'):'Primary vanity';
 const section=document.getElementById('viewer-focus-cutaway');
 section.hidden=state.mode!=='full';
 section.textContent='Section '+(state.interiorReveal?'ON':'OFF');
 section.setAttribute('aria-pressed',String(state.interiorReveal));
 const ghost=document.getElementById('viewer-focus-gwb');
 ghost.hidden=state.mode!=='full'||!inst?.architecture?.native_ceiling_evidence?.id;
 ghost.textContent='GWB ghost '+(state.ceilingPreview?'ON':'OFF');
 ghost.setAttribute('aria-pressed',String(state.ceilingPreview));
 applyFocusArchitecturalPresentation();
}
function setFocusView(enabled){
 state.focusView=Boolean(enabled);
 updateFocusViewControls();
 // Stage changes from center grid-cell to full viewport only by this explicit
 // user action. Keep the SAME camera pose/orbit, source meshes and picks; only
 // update projection aspect and WebGL pixel buffer for the newly sized stage.
 resize();renderer.render(scene,camera);
}
document.getElementById('viewer-focus-enter').onclick=()=>setFocusView(true);
document.getElementById('viewer-focus-exit').onclick=()=>setFocusView(false);
document.getElementById('viewer-focus-room').onchange=e=>selectRoom(e.target.value);
document.getElementById('viewer-focus-instance').onchange=e=>{
 const i=current()?.physical_instances?.findIndex(x=>String(x.room_number)===e.target.value)??-1;
 if(i<0||i===state.instance)return;
 state.instance=i;state.surface=-1;updateInstanceSelect();rebuild();
};
document.getElementById('viewer-focus-full').onclick=()=>{
 if(state.mode!=='full')setMode('full');else setCamera('isometric');
 updateFocusViewControls();
};
document.getElementById('viewer-focus-wet').onclick=()=>{
 if(state.mode==='context')return;
 setCamera('wet');
};
document.getElementById('viewer-focus-finish').onclick=()=>{
 if(state.mode!=='full'||!R063_FOCUS_BATHS.has(state.room))return;
 setCamera('r063-bath-finish');updateFocusViewControls();
};
document.getElementById('viewer-focus-architectural').onclick=()=>{
 if(state.mode!=='full')return;
 const kind=state.room;
 const preset=kind==='PH-BATH4'?'ph4-311':
  kind==='TX-BATH4'?'r066-tx4-counter':
  kind==='PH-PRIMARY'||kind==='TX-PRIMARY'?'r062-primary-vanity':
  R067_COMPACT_FOCUS.has(kind)?
   (kind.endsWith('-WC')?'r067-wc-survey':'r067-powder-survey'):null;
 if(preset)setCamera(preset);
};
document.getElementById('viewer-focus-plan').onclick=()=>setCamera('top');
document.getElementById('viewer-focus-iso').onclick=()=>setCamera('isometric');
document.getElementById('viewer-focus-cutaway').onclick=()=>{
 if(state.mode!=='full')return;
 document.getElementById('viewer-reveal-interior').click();
 updateFocusViewControls();
};
document.getElementById('viewer-focus-gwb').onclick=()=>{
 if(state.mode!=='full'||!instance()?.architecture?.native_ceiling_evidence?.id)return;
 document.getElementById('viewer-ceiling-preview').click();
 updateFocusViewControls();
};
document.getElementById('viewer-focus-ab').onclick=()=>{
 document.getElementById('viewer-compare-ab').click();updateFocusViewControls();
};
document.getElementById('viewer-focus-traces').onclick=()=>{
 document.getElementById('viewer-toggle-source-traces').click();updateFocusViewControls();
};
document.getElementById('viewer-focus-evidence').onclick=()=>{
 setFocusView(false);document.getElementById('viewer-v2-evidence').open=true;
};
function setMode(mode){
 if(mode!=='study'&&mode!=='context'&&mode!=='full')return;
 state.mode=mode;state.surface=-1;state.preset='isometric';rebuild();
}
function resize(){
 const w=Math.max(200,stage.clientWidth),h=Math.max(200,stage.clientHeight);
 renderer.setSize(w,h,false);
 camera.aspect=w/h;camera.updateProjectionMatrix();
 if(completionInstalled)updateCompletionViewport();
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
document.getElementById('viewer-camera-fixture').onclick=()=>setCamera('fixture');
document.getElementById('viewer-r060-counter-focus').onclick=()=>setCamera('r060-counter');
document.getElementById('viewer-r062-primary-vanity').onclick=()=>setCamera('r062-primary-vanity');
document.getElementById('viewer-r062-primary-shell').onclick=()=>setCamera('r062-primary-shell');
document.getElementById('viewer-r063-bath-finish').onclick=()=>setCamera('r063-bath-finish');
document.getElementById('viewer-r060-wc-focus').onclick=()=>setCamera('r060-wc');
document.getElementById('viewer-camera-wet').onclick=()=>setCamera('wet');
document.getElementById('viewer-ph4-focus-311').onclick=()=>setCamera('ph4-311');
document.getElementById('viewer-ph4-focus-310').onclick=()=>setCamera('ph4-310');
document.getElementById('viewer-ceiling-preview').onclick=()=>{
 state.ceilingPreview=!state.ceilingPreview;applyCeilingPreview();
};
document.getElementById('viewer-camera-front').onclick=()=>setCamera('front');
document.getElementById('viewer-camera-top').onclick=()=>setCamera('top');
document.getElementById('viewer-reveal-interior').onclick=()=>{
 state.interiorReveal=!state.interiorReveal;
 applyWallVisibility();applyInteriorReveal();
 // The complete original/source distinction also remains in Room Evidence
 // and in the visible fidelity note, rather than in geometry alone.
 fidelity.textContent=modeInfo+(state.mode==='full'?
  (state.interiorReveal?' R057 INTERIOR REVEAL: view-facing wall meshes sectioned at 2.35 ft; source geometry and quantities unchanged.':
  ' R057 FULL PRESENTATION ENVELOPE: reversible camera-facing section disabled; source geometry unchanged.'):'');
 fidelity.title=fidelity.textContent;
};
document.getElementById('viewer-toggle-source-traces').onclick=()=>{
 state.sourceTraces=!state.sourceTraces;applySourceTraceVisibility();
};
document.getElementById('viewer-compare-ab').onclick=()=>{
 state.compareAB=!state.compareAB;updateABCompare();
};
document.getElementById('reset').onclick=()=>setCamera('isometric');
document.getElementById('toggle-walls').onclick=()=>{
 state.walls=!state.walls;
 applyWallVisibility();applyInteriorReveal();applyCeilingPreview();
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
 if(e.key==='Escape'&&state.focusView){e.preventDefault();setFocusView(false);return;}
 if(e.target?.matches('input,textarea,select'))return;
 if(e.key==='1')setMode('full');if(e.key==='2')setMode('study');if(e.key==='3')setMode('context');
 if(e.key.toLowerCase()==='f')setCamera('isometric');
 if(e.key.toLowerCase()==='i')setCamera('interior');
 if(e.key.toLowerCase()==='k')setCamera('fixture');
 if(e.key.toLowerCase()==='p')setCamera('top');
 if(e.key.toLowerCase()==='v')document.getElementById('viewer-reveal-interior').click();
 if(e.key.toLowerCase()==='c')document.getElementById('viewer-compare-ab').click();
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
 if(document.getElementById('viewer-gallery'))return;
 const previous={...state};let cancelled=false;
 const display=document.createElement('div');display.id='viewer-gallery';
 display.dataset.status='COLLECTING';
 display.style.cssText='position:fixed;inset:0;z-index:99999;background:#0b1118;color:#e8eff4;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));grid-auto-rows:260px;gap:10px;padding:65px 14px 14px;overflow:auto';
 const status=document.createElement('div');status.id='viewer-gallery-status';
 status.textContent='Collecting source-dimensional views... 0/13';
 status.style.cssText='position:fixed;top:12px;left:145px;right:14px;background:#162537;padding:9px 12px;font:600 11px Segoe UI;border:1px solid #688ba6;z-index:2';
 display.append(status);document.body.append(display);
 const close=document.createElement('button');close.type='button';close.id='viewer-gallery-close';
 close.textContent='Close gallery';close.className='viewer-btn';
 close.style.cssText='position:fixed;top:12px;left:14px;z-index:3;min-height:34px';
 close.onclick=()=>{
  cancelled=true;display.remove();Object.assign(state,previous);
  updateRoomList();updateInstanceSelect();rebuild();
 };
 display.append(close);
 // Capture the same immersive architectural presentation as Focus view:
 // hide analytical grids and reveal only already source-matched wet hosts.
 // The previous presentation state is restored by Close gallery.
 setFocusView(true);
 const cards=[];
 for(const r of ROOMS){
  if(cancelled)return;
  // Do not treat this capture diagnostic as architectural BIM verification.
  selectRoom(r.id);setCamera('isometric');
  const active=[...materialCache.values()].map(x=>x.ready);
  await Promise.race([Promise.all(active),new Promise(resolve=>setTimeout(resolve,2500))]);
  if(cancelled)return;
  // The synchronous path is reliable in local headless Chrome; some
  // SwiftShader builds never resolve compileAsync during virtual-time capture.
  renderer.compile(scene,camera);
  renderer.render(scene,camera);
  renderer.getContext().finish();
  // Virtual-time headless Chrome can stall awaiting RAF, so use a bounded
  // deterministic browser timer and an explicit second GPU render.
  await new Promise(resolve=>setTimeout(resolve,800));
  if(cancelled)return;
  renderer.render(scene,camera);renderer.getContext().finish();
  const src=canvas.toDataURL('image/png');
  if(!src.startsWith('data:image/png;base64,'))throw new Error('Canvas capture did not return PNG: '+r.id);
  cards.push({id:r.id,instance:instance()?.room_number,src,program:r.program?.kind||''});
  status.textContent='Collecting source-dimensional views... '+cards.length+'/13';
 }
 selectRoom('PH-BATH4');
 for(const card of cards){
  const box=document.createElement('button');box.type='button';
  box.className='viewer-gallery-card';box.setAttribute('aria-label','Open '+card.id+' / '+card.instance);
  box.style.cssText='border:1px solid #334c5c;overflow:hidden;background:#18242f;position:relative;min-height:0;padding:0';
  box.onclick=()=>{cancelled=true;display.remove();loadInstanceAddress('#'+card.id+'/'+card.instance);};
  const img=document.createElement('img');img.src=card.src;img.alt=card.id+' '+card.instance+' source-qualified room study';
  img.style.cssText='height:100%;width:100%;object-fit:contain';
  const label=document.createElement('div');label.textContent=card.id+' / '+card.instance;
  label.style.cssText='position:absolute;top:2px;left:2px;background:#0d1724d9;padding:5px;font:600 11px Segoe UI;color:white';
  box.append(img,label);display.append(box);
 }
 status.textContent='13 bathroom types Â· A-instance overview. Select a card to inspect its room; use A/B to review the other physical instance.';
 display.dataset.status='COMPLETE';document.body.dataset.viewerGallery='COMPLETE';
}
window.__viewerDebug={rooms:ROOMS.length,instanceTotal:ROOMS.reduce((a,r)=>a+r.physical_instances.length,0),
 selectRoom,setMode,setCamera,parseInstanceAddress,loadInstanceAddress,updateABCompare,
 getR068PrimarySheetBath:()=>R068_PRIMARY_BATH_SHEET[state.room]||null,
 getState:()=>({...state,objectCount:renderObjects.length}),
 getCameraInfo:()=>({position:camera.position.toArray(),target:orbit.target.toArray(),
  preset:state.preset,fov:camera.fov}),
 getSceneEvidence:()=>renderObjects.map(o=>({category:o.userData?.category,visible:o.visible,
  kind:o.userData?.kind||null,source:o.userData?.source||null,
  r065_neutral_plaster_display_only:o.userData?.r065_neutral_plaster_display_only??null,
  r065_plaster_microtexture:o.userData?.r065_plaster_microtexture??null,
  r065_plaster_uv_ft_per_repeat:o.userData?.r065_plaster_uv_ft_per_repeat??null,
  r065_wall_thickness_geometry_unchanged:o.userData?.r065_wall_thickness_geometry_unchanged??null,
  r065_illustrative_finish_not_revit_material:o.userData?.r065_illustrative_finish_not_revit_material??null,
  r065_wet_host_photo_reveal:o.userData?.r065_wet_host_photo_reveal??null,
  r066_inside_category_aabb_xyz:o.userData?.r066_inside_category_aabb_xyz??null,
  r066_continuous_combined_level_point_pool:o.userData?.r066_continuous_combined_level_point_pool??null,
  r066_no_duplicate_physical_pan_surface:o.userData?.r066_no_duplicate_physical_pan_surface??null,
  r066_visual_shadow_only:o.userData?.r066_visual_shadow_only??null,
  r066_counter_source_extent:o.userData?.local_extent_ft??null,
  r066_world_mesh_aabb:('ARCH_R066_NATIVE_BOUNDED_COUNTER_EDGE ARCH_R066_NATIVE_BOUND_COUNTER_END_VISUAL'.split(' ').includes(o.userData?.category))?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r067_inside_native_category_aabb_xyz:o.userData?.r067_inside_native_category_aabb_xyz??null,
  r067_native_counter_bounds:o.userData?.source_native_bounds??null,
  r067_counter_source_id:o.userData?.revit_id??null,
  r067_visual_part:o.userData?.visual_part??null,
  r067_world_mesh_aabb:('ARCH_R067_NATIVE_BOUNDED_POWDER_FACET ARCH_R067_THIN_COUNTER_LIGHT_EDGE'.split(' ').includes(o.userData?.category))?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r067_dry_source_host:o.userData?.r067_dry_source_host??null,
  r067_dry_native_host_wall_id:o.userData?.native_host_face_id??null,
  r067_selected_preview_not_installed:o.userData?.installed_tile_extent_verified===false??null,
  r067_selected_preview_no_additional_area:o.userData?.additional_purchase_quantity_ft2??null,
  r067_wc_visual_piece:o.userData?.wc_visual_piece??null,
  r070_ceramic_continuous_bowl:o.userData?.r070_ceramic_continuous_bowl??null,
  r070_illustrative_tub_inner:o.userData?.r070_illustrative_tub_inner??null,
  actual_manufacturer_solid:o.userData?.actual_manufacturer_solid??null,
  fixture_coordinate_certified:o.userData?.fixture_coordinate_certified??null,
  r068_inside_native_countertop_xyz:o.userData?.r068_inside_native_countertop_xyz??null,
  r068_world_mesh_aabb:o.userData?.category==='ARCH_R068_SOURCE_COUNTER_LIGHT_REVEAL'?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r068_counter_part:o.userData?.r068_part??null,
  r068_native_wall_depth_light:o.userData?.category==='ARCH_R068_NATIVE_WALL_DEPTH_LIGHT',
  r068_native_wall_id:o.userData?.r068_parent_wall_id||null,
  r068_source_wet_host_id:o.userData?.native_host_face_id??null,
  r068_wet_tub_contact_span_ft:o.userData?.r068_render_span_ft??null,
  r068_wet_tub_contact_gap_ft:o.userData?.r068_study_gap_ft??null,
  r068_selected_bath2_glazed_optical_relief:o.material?.userData?.r068_selected_bath2_glazed_optical_relief??null,
  r068_nominal_tile_ft:o.material?.userData?.r068_nominal_tile_ft??null,
  r069_within_native_aabb:o.userData?.r069_within_native_aabb??null,
  r069_source_native_id:o.userData?.revit_id??null,
  r069_casework_part:o.userData?.r069_part??null,
  r069_world_mesh_aabb:o.userData?.category==='ARCH_R069_BOUNDED_CASEWORK_LIGHT'?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r069_selected_ceramic_relief:o.material?.userData?.r069_selected_ceramic_relief??null,
  r069_nominal_tile_ft:o.material?.userData?.r069_nominal_tile_ft??null,
  r069_wet_native_host:o.userData?.category==='ARCH_R069_SELECTED_WET_HOST_JUNCTION'?
   o.userData?.native_host_face_id:null,
  r069_context_compartment:o.userData?.category==='ARCH_R069_CONTEXT_REGISTERED_LOCATOR'?
   o.userData.compartment:null,
  r070_native_counter_contained:o.userData?.r070_native_counter_contained??null,
  r070_countertop_light_world_aabb:o.userData?.category==='ARCH_R070_NATIVE_COUNTER_SURFACE_STUDY'?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r070_native_lid_world_aabb:o.userData?.category==='ARCH_R070_310B_NATIVE_BOUNDED_LID'?
   (()=>{const bb=new THREE.Box3().setFromObject(o);return [bb.min.toArray(),bb.max.toArray()];})():null,
  r070_retained_wood_grain_normal_study:o.userData?.r070_retained_wood_grain_normal_study??null,
  r070_no_invented_floor_sku:o.userData?.r070_no_invented_floor_sku??null,
  r070_native_wall_id:o.userData?.category==='ARCH_R070_PLASTER_FACE_STUDY'?
   o.userData.native_source_wall_id:null,
  r063_source_floor_uv_kind:o.userData?.r063_source_floor_uv_kind??null,
  r063_nominal_tile_size_ft:o.userData?.r063_nominal_tile_size_ft??null,
  r063_map_repeat_per_source_ft:o.userData?.r063_map_repeat_per_source_ft??null,
  r063_floor_material_selected:o.userData?.r063_floor_material_selected??null,
  r063_material_texture_repeat:o.userData?.category==='ARCH_REGISTERED_FLOOR'&&o.material?.map?.repeat?.toArray?
   o.material.map.repeat.toArray():null,
  r063_tub_part:o.userData?.r063_tub_part??null,
  r063_native_counter_bounds_local_ft:o.userData?.source_bounds_local_ft??null,
  r063_inside_native_category_aabb_xyz:o.userData?.inside_native_category_aabb_xyz??null,
  r063_new_tile_plane:o.userData?.new_tile_plane??null,
  r063_installed_baseboard:o.userData?.installed_baseboard??null,
  r063_actual_floor_area_ft2:o.userData?.actual_floor_area_ft2??null,
  r063_material_quantities_unchanged:o.userData?.material_quantities_unchanged??null,
  r063_native_face_visual_study:o.userData?.native_face_visual_study??null,
  r063_source_bounded_to_actual_wall_run:o.userData?.source_bounded_to_actual_wall_run??null,
  r063_source_wall_face_segment:o.userData?.source_wall_face_segment??null,
  wall:o.userData?.wall??null,
  room_number:o.userData?.room_number||null,
  primary_source_only:o.userData?.primary_source_only??null,
  primary_no_physical_shower_model:o.userData?.primary_no_physical_shower_model??null,
  classification:o.userData?.classification??null,
  candidate_bbox_local_xz_ft:o.userData?.candidate_bbox_local_xz_ft??null,
  counter_overlap_sf:o.userData?.counter_overlap_sf??null,
  native_countertop_conflicts:o.userData?.native_countertop_conflicts??null,
  hosted_entry_conflicts:o.userData?.hosted_entry_conflicts??null,
  polygon_support:o.userData?.polygon_support??null,
  not_installed_shower:o.userData?.not_installed_shower??null,
  selected_48in_drain_center:o.userData?.selected_48in_drain_center??null,
  review_reveal_part:o.userData?.review_reveal_part??null,
  source_bounded_display_only:o.userData?.source_bounded_display_only??null,
  source_bound_height_min_ft:o.userData?.source_bound_height_min_ft??null,
  source_bound_height_max_ft:o.userData?.source_bound_height_max_ft??null,
  not_selected_cabinet_joinery:o.userData?.not_selected_cabinet_joinery??null,
  study_object_bbox_ft:('ARCH_R062_NATIVE_BOUND_VANITY_END_STUDY ARCH_R062_NATIVE_BOUND_VANITY_UNDERSIDE_STUDY ARCH_R062_NATIVE_HOST_REVEAL_VISUAL'.split(' ').includes(o.userData?.category))?
    new THREE.Box3().setFromObject(o).getSize(new THREE.Vector3()).toArray():null,
  native_ceiling_id:o.userData?.native_ceiling_id||null,
  native_ceiling_receipt:o.userData?.native_ceiling_receipt||null,
  height_ft:o.userData?.height_ft??null,
  coordinate_reference_kind:o.userData?.coordinate_reference_kind||null,
  native_insertion_ft:o.userData?.native_insertion_ft??null,
  native_bounds_center_ft:o.userData?.native_bounds_center_ft??null,
  native_aabb_dimensions_ft:o.userData?.native_aabb_dimensions_ft??null,
  not_family_solid:o.userData?.not_family_solid??null,
  not_installed_clearance:o.userData?.not_installed_clearance??null,
  not_exact_native_3d_insertion:o.userData?.not_exact_native_3d_insertion??null,
  source_plumbing_native_xyz_ft:o.userData?.source_plumbing_native_xyz_ft??null,
  source_plumbing_local_y_ft:o.userData?.source_plumbing_local_y_ft??null,
  displayed_locator_y_ft:o.userData?.displayed_locator_y_ft??null,
  visual_y_offset_from_source_ft:o.userData?.visual_y_offset_from_source_ft??null,
  basin_spatial_status:o.userData?.basin_spatial_status??null,
  basin_program_status:o.userData?.basin_program_status??null,
  contained_within_native_category_aabb_xyz:o.userData?.contained_within_native_category_aabb_xyz??null,
  source_native_insertion_xyz_ft:o.userData?.source_native_insertion_xyz_ft??null,
  source_local_y_ft:o.userData?.source_local_y_ft??null,
  displayed_plan_marker_y_ft:o.userData?.displayed_plan_marker_y_ft??null,
  front_source_axis:o.userData?.front_source_axis??null,
  front_dimension_ft:o.userData?.front_dimension_ft??null,
  front_display_height_ft:o.userData?.front_display_height_ft??null,
  front_bottom_ft:o.userData?.front_bottom_ft??null,
  front_top_ft:o.userData?.front_top_ft??null,
  inside_native_aabb_y:o.userData?.inside_native_aabb_y??null,
  cabinet_family_solid:o.userData?.cabinet_family_solid??null,
  installed_face_location_verified:o.userData?.installed_face_location_verified??null,
  fixture_visual_classification:o.userData?.fixture_visual_classification??null,
  fixture_model:o.userData?.fixture_model??null,
  fixture_dimensions:o.userData?.fixture_dimensions??null,
  generic_visual_profile:o.userData?.generic_visual_profile??null,
  nominal_exterior_width_ft:o.userData?.nominal_exterior_width_ft??null,
  nominal_exterior_depth_ft:o.userData?.nominal_exterior_depth_ft??null,
  actual_drain_location:o.userData?.actual_drain_location??null,
  actual_faucet_location:o.userData?.actual_faucet_location??null,
  no_bathtub_drain_or_spout_location:o.userData?.no_bathtub_drain_or_spout_location??null,
  physical_study_bbox_ft:o.userData?.generic_visual_profile?
    new THREE.Box3().setFromObject(o).getSize(new THREE.Vector3()).toArray():null,
  review_compartment:o.userData?.review_compartment??null,
  review_original_y_center_ft:o.userData?.review_original_y_center_ft??null,
  review_original_bottom_ft:o.userData?.review_original_bottom_ft??null,
  review_original_top_ft:o.userData?.review_original_top_ft??null,
  review_rendered_top_ft:o.userData?.review_rendered_top_ft??null,
  review_cutaway_only:o.userData?.review_cutaway_only??null,
  review_source_native_geometry_unchanged:o.userData?.review_source_native_geometry_unchanged??null,
  review_face_midpoint_xz_ft:o.userData?.review_face_midpoint_xz_ft??null,
  review_outward_xz:o.userData?.review_outward_xz??null,
  review_visual_hidden_only:o.userData?.review_visual_hidden_only??null,
  visual_section_only:o.userData?.visual_section_only??null,
  rendered_start_y_ft:o.userData?.rendered_start_y_ft??null,
  rendered_end_y_ft:o.userData?.rendered_end_y_ft??null,
  parent_compartment:o.userData?.parent_compartment??null,
  derived_xy_only:o.userData?.derived_xy_only??null,
  not_native_ceiling_solid:o.userData?.not_native_ceiling_solid??null,
  wc_visual_piece:o.userData?.wc_visual_piece??null,
  generic_wc_envelope_ft:o.userData?.generic_wc_envelope_ft??null,
  actual_wc_family_solid:o.userData?.actual_wc_family_solid??null,
  installed_height_verified:o.userData?.installed_height_verified??null,
  actual_wc_installation_height:o.userData?.actual_wc_installation_height??null,
  view_only:o.userData?.view_only??null,
  no_additional_area:o.userData?.no_additional_area??null,
  full_specification_height_ft:o.userData?.full_specification_height_ft??null,
  rendered_cutaway_height_ft:o.userData?.rendered_cutaway_height_ft??null,
  native_host_face_id:o.userData?.native_host_face_id??null,
  native_host_face_receipt:o.userData?.native_host_face_receipt??null,
  source_return_supported:o.userData?.source_return_supported??null,
  derived_return_not_partition:o.userData?.derived_return_not_partition??null,
  full_height_return_normal_review:o.userData?.full_height_return_normal_review??null,
  review_return_full_height_ft:o.userData?.review_return_full_height_ft??null,
  review_return_rendered_height_ft:o.userData?.review_return_rendered_height_ft??null,
  review_return_section_only:o.userData?.review_return_section_only??null,
  not_swing_or_rough_opening:o.userData?.not_swing_or_rough_opening??null,
  not_glazing_or_rough_opening:o.userData?.not_glazing_or_rough_opening??null,
  host_id:o.userData?.host_id??null,
  receipt_id:o.userData?.receipt_id??null,
  native_host_thickness_ft:o.userData?.native_host_thickness_ft??null,
  nominal_width_ft:o.userData?.nominal_width_ft??null,
  nominal_height_ft:o.userData?.nominal_height_ft??null,
  rendered_width_ft:o.userData?.rendered_width_ft??null,
  rendered_height_ft:o.userData?.rendered_height_ft??null,
  geometry_rendered_width_ft:o.userData?.geometry_rendered_width_ft??null,
  geometry_rendered_height_ft:o.userData?.geometry_rendered_height_ft??null,
  clipped_by_visual_cutaway:o.userData?.clipped_by_visual_cutaway??null,
  clipped_by_inferred_face:o.userData?.clipped_by_inferred_face??null,
  visual_classification:o.userData?.visual_classification??null,
  unresolved_nominal_width_ft:o.userData?.unresolved_nominal_width_ft??null,
  unresolved_nominal_height_ft:o.userData?.unresolved_nominal_height_ft??null,
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
