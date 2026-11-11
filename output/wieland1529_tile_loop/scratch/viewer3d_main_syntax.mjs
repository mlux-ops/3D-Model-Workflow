
import * as THREE from 'three';
import { OrbitControls } from 'orbit-controls';
const payload=JSON.parse(document.getElementById('data').textContent),rooms=payload.rooms;
const canvas=document.getElementById('render'),stage=document.getElementById('stage');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x19222b);scene.fog=new THREE.FogExp2(0x1d2933,.012);
const camera=new THREE.PerspectiveCamera(47,1,.035,800);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.dampingFactor=.085;orbit.maxPolarAngle=Math.PI*.89;orbit.minDistance=2;orbit.maxDistance=160;orbit.enablePan=true;
scene.add(new THREE.HemisphereLight(0xd6e8ff,0x554c43,2.0));const sun=new THREE.DirectionalLight(0xffe8ce,4.4);sun.position.set(-13,25,18);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.near=.1;sun.shadow.camera.far=120;sun.shadow.bias=-.00035;scene.add(sun);
const fill=new THREE.DirectionalLight(0xe1efff,2);fill.position.set(12,6,-12);scene.add(fill);
const pmrem=new THREE.PMREMGenerator(renderer);const envscene=new THREE.Scene();envscene.background=new THREE.Color(0x6f8291);
const hemi=new THREE.HemisphereLight(0xe9f6ff,0x75634e,3);envscene.add(hemi);scene.environment=pmrem.fromScene(envscene,.02).texture;
const mats={
 wall:new THREE.MeshStandardMaterial({color:0xd7d6d0,roughness:.78,metalness:0}),
 glass:new THREE.MeshPhysicalMaterial({color:0x92bfdd,roughness:.07,metalness:.02,transmission:.65,transparent:true,opacity:.38,side:THREE.DoubleSide}),
 metal:new THREE.MeshStandardMaterial({color:0x26282b,metalness:.84,roughness:.19}),
 porcelain:new THREE.MeshPhysicalMaterial({color:0xe6e2dc,roughness:.2,metalness:.02,clearcoat:.55,clearcoatRoughness:.2}),
 wood:new THREE.MeshStandardMaterial({color:0x85725e,roughness:.48,metalness:0}),
 neutral:new THREE.MeshStandardMaterial({color:0x777f83,roughness:.86,metalness:0}),
 floor:new THREE.MeshStandardMaterial({color:0xc5bdae,roughness:.7,metalness:0})
};
let modelGroup=new THREE.Group();scene.add(modelGroup);
let currentRoom=null,highlight=-1,edgeVisible=false,wallVisible=true,altActive=false,textureCache=new Map(),parts=[];
function activeProducts(){return (altActive&&currentRoom?.alternative?.products)||currentRoom?.products||[];}
const loader=new THREE.TextureLoader();
function makeTileMaterial(p){
 const name=(p?.name||'').toLowerCase(),size=p?.size||'',gloss=/gloss|purity|sapphire|sandstone|indigo/.test(name);
 const matte=/matte|pienza|luxe|riviera|cortar/.test(name);
 const texCanvas=document.createElement('canvas');texCanvas.width=512;texCanvas.height=512;
 const cx=texCanvas.getContext('2d');
 const light=gloss?'#ddd8cb':'#d6d1c4';cx.fillStyle=light;cx.fillRect(0,0,512,512);
 let w=/2.?x.?20/i.test(size)?90:/3.?x.?12/i.test(size)?110:/6.?x.?6/i.test(size)?170:235;
 let h=/2.?x.?20/i.test(size)?225:/3.?x.?12/i.test(size)?170:/6.?x.?6/i.test(size)?170:230;
 const n=(name.match(/sandstone|beige|terra|cortar/)?.[0]||'');
 if(n)cx.fillStyle=/sandstone|terra/.test(n)?'#b6a38d':'#b6b7b3';else if(/indigo|antique|sapphire/.test(name))cx.fillStyle='#455d73';else cx.fillStyle='#d3ccc3';
 const tileColor=cx.fillStyle;cx.fillStyle='#8c8a82';cx.fillRect(0,0,512,512);
 for(let y=0;y<512;y+=h)for(let x=0;x<512;x+=w){
  cx.fillStyle=tileColor;cx.fillRect(x+2,y+2,w-4,h-4);
  cx.strokeStyle='rgba(255,255,255,.11)';cx.lineWidth=2;cx.strokeRect(x+7,y+7,w-14,h-14);
  for(let j=0;j<8;j++){cx.fillStyle='rgba(250,250,242,.014)';cx.fillRect(x+Math.random()*w,y+Math.random()*h,4+Math.random()*w/8,1);}
 }
 const tex=new THREE.CanvasTexture(texCanvas);tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=8;
 const mat=new THREE.MeshPhysicalMaterial({map:tex,roughness:gloss?.2:(matte?.83:.52),metalness:0,clearcoat:gloss?.48:.05,clearcoatRoughness:gloss?.13:.6});
 if(p?.image){const img=new Image();img.onload=()=>{
  const c=document.createElement('canvas');c.width=c.height=512;const g=c.getContext('2d');g.drawImage(texCanvas,0,0);
  g.globalAlpha=.28;const ratio=Math.max(512/img.width,512/img.height),sw=img.width*ratio,sh=img.height*ratio;
  g.drawImage(img,(512-sw)/2,(512-sh)/2,sw,sh);g.globalAlpha=1;
  const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;t.repeat.set(2.5,1.9);mat.map=t;mat.needsUpdate=true;
 };img.src=p.image;}
 return mat;
}
function boxGeom(bounds,anchor){const lo=bounds.min,hi=bounds.max,dx=Math.max(.025,hi[0]-lo[0]),dy=Math.max(.025,hi[1]-lo[1]),dz=Math.max(.025,hi[2]-lo[2]);
 return {size:[dx,dz,dy],center:[(lo[0]+hi[0])/2-anchor[0],(lo[2]+hi[2])/2-anchor[2],(lo[1]+hi[1])/2-anchor[1]]};}
function meshFromBounds(o,anchor,material,kind,surfaceIndex=-1){
 const d=boxGeom(o.bounds,anchor),maxDim=Math.max(...d.size);if(maxDim>32)return;
 const geo=new THREE.BoxGeometry(...d.size);
 const mesh=new THREE.Mesh(geo,material);mesh.position.set(...d.center);
 mesh.castShadow=kind!=='floor'&&kind!=='wall';mesh.receiveShadow=true;mesh.userData={id:o.id,name:o.name,category:kind,receipt:o.receipt_id,surfaceIndex,dimensionsFeet:d.size.map(x=>+x.toFixed(3))};
 if(kind==='wall'){mesh.material=material.clone();mesh.material.transparent=true;mesh.material.opacity=wallVisible?.91:.03;}
 if(kind==='window'){mesh.material=mats.glass;mesh.castShadow=false;}
 if(kind==='door'){mesh.material=mats.wood;}
 modelGroup.add(mesh);parts.push(mesh);
 if(edgeVisible){const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geo),new THREE.LineBasicMaterial({color:0x8ca1b2,transparent:true,opacity:.55}));mesh.add(edges);}
 return mesh;
}
function findSurface(room,which){
 const r=room.products||[];
 const f=which==='wall'?r.find(p=>/wall|tub|wet/i.test(p.surface)):
 which==='floor'?r.find(p=>/level|floor|pan/i.test(p.surface)):r.find(p=>/niche/i.test(p.surface));
 return f||null;
}
function frame(){
 const bounds=new THREE.Box3().setFromObject(modelGroup);
 let center=bounds.isEmpty()?new THREE.Vector3():bounds.getCenter(new THREE.Vector3());
 // Camera centers on visible subset (bounded Revit elements only), not an inferred room centroid.
 let size=bounds.isEmpty()?new THREE.Vector3(12,9,12):bounds.getSize(new THREE.Vector3());
 const radius=Math.min(35,Math.max(8,size.length()*.64));
 orbit.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(radius*.8,radius*.62,radius*1.1));camera.near=.03;camera.far=800;camera.updateProjectionMatrix();orbit.update();
}
function materialInspector(index){highlight=index;const p=activeProducts()[index];const info=document.getElementById('material-info');
 if(!p){info.hidden=true;return}info.hidden=false;
 const esc=s=>String(s??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
 info.innerHTML='<b>'+esc(p.name)+'</b><div style="margin-top:4px">'+esc(p.surface)+'</div><div>Nominal size: '+esc(p.size)+'</div><div>Price/source: '+esc(p.price)+'</div><div>'+(/niche/i.test(p.surface)?'Niche location/geometry unavailable from the native Revit bridge; no actual niche mesh is displayed.':'Preview applied to model-derived context bounds; exact room face attribution is unverified.')+'</div>'+(p.image?.includes('sandstone')?'<div>Sandstone thumbnail is a Sandstone/Copper MIXED maker installation, not Sandstone-only appearance.</div>':'')+'<div>Maker image is not a verified sample.</div><a href="'+esc(p.url)+'" rel="noopener noreferrer" target="_blank">Official product page ↗</a>';
 document.querySelectorAll('.surface').forEach((x,i)=>x.classList.toggle('selected',i===index));
 parts.forEach(part=>{
  const hit=part.userData.surfaceIndex===index;
  if(part.material?.emissive){part.material.emissive.set(hit?0x55412a:0x000000);part.material.emissiveIntensity=hit?.22:0;}
 });
}
function buildRoom(rid){
 const r=rooms.find(q=>q.id===rid);if(!r)return;if(!r.alternative)altActive=false;currentRoom=r;
 const old=modelGroup;modelGroup=new THREE.Group();scene.add(modelGroup);scene.remove(old);
 old.traverse(o=>{if(o.geometry)o.geometry.dispose()});parts=[];
 const ctx=r.model_context,anchor=ctx.anchor_ft;
 let surfaces=activeProducts(),wall=surfaces.find(p=>/wall|tub|wet/i.test(p.surface))||null,floor=surfaces.find(p=>/level|floor|pan/i.test(p.surface))||null,niche=surfaces.find(p=>/niche/i.test(p.surface))||null;
 const wallMaterial=wall?makeTileMaterial(wall):mats.neutral,floorMaterial=floor?makeTileMaterial(floor):mats.floor;
 const floorObjects=ctx.floors||[];const localFloors=floorObjects.filter(o=>Math.abs(o.bounds.min[2]-anchor[2])<4);
 for(const o of localFloors){
  const b=o.bounds,cut={min:[Math.max(b.min[0],anchor[0]-11),Math.max(b.min[1],anchor[1]-11),b.min[2]],max:[Math.min(b.max[0],anchor[0]+11),Math.min(b.max[1],anchor[1]+11),Math.min(b.max[2],anchor[2]+.5)]};
  if(cut.max[0]>cut.min[0]&&cut.max[1]>cut.min[1])meshFromBounds({...o,bounds:cut},anchor,floorMaterial,'floor',surfaces.indexOf(floor));
 }
 for(const o of ctx.walls||[]){
  const b=o.bounds;
  if(b.min[2]>=anchor[2]+11||b.max[2]<=anchor[2]-2)continue;
  meshFromBounds(o,anchor,wallMaterial,'wall',surfaces.indexOf(wall));
 }
 for(const o of ctx.windows||[])meshFromBounds(o,anchor,mats.glass,'window');
 for(const o of ctx.doors||[])meshFromBounds(o,anchor,mats.wood,'door');
 for(const o of ctx.casework||[])meshFromBounds(o,anchor,mats.wood,'casework');
 for(const o of ctx.fixtures||[])meshFromBounds(o,anchor,mats.porcelain,'fixture');
 // Neutral scene base is purely visual context, not a Revit floor or measured slab.
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(120,120),new THREE.MeshStandardMaterial({color:0x1f2a33,roughness:.91}));
 ground.rotation.x=-Math.PI/2;ground.position.y=-2.05;ground.receiveShadow=true;modelGroup.add(ground);
 const grid=new THREE.GridHelper(80,40,0x637381,0x354552);grid.position.y=-2.02;grid.material.opacity=.16;grid.material.transparent=true;modelGroup.add(grid);
 const ui=document.getElementById('room-list');ui.querySelectorAll('.room-btn').forEach(b=>b.classList.toggle('active',b.dataset.room===r.id));
 document.getElementById('room-title').textContent=r.id+' / '+r.title;
 document.getElementById('room-description').textContent=(r.has_pick?(altActive?'Unselected historical alternative preview; frozen picks unchanged. ':'Frozen tile scheme shown on model-derived context bounding boxes. '):'NO PICK YET — all tile surfaces neutral. ')+'Room-to-element attribution unverified.';
 document.getElementById('confidence').textContent=r.has_pick?'Context proxy':'No selected tile';
 document.getElementById('model-count').textContent=parts.length+' actual Revit element bounds · room association unverified';
 document.getElementById('spec-title').textContent=r.id+' · '+(altActive?'Historical alternative preview':r.has_pick?'Frozen current picks':'No pick yet');
 const alt=document.getElementById('alternative');alt.disabled=!r.alternative;alt.checked=!!(r.alternative&&altActive);
 document.getElementById('alternative-label').textContent=r.alternative?(altActive?'Unselected preview':'Compare unselected'):'Not available';
 const list=document.getElementById('surfaces');list.innerHTML='';
 if(!surfaces.length){list.innerHTML='<div class="muted" style="padding:12px;background:#26313d;border-radius:5px;margin-top:11px">NO PICK YET<br>Neutral materials only. Do not infer owner approval.</div>';}
 for(let i=0;i<surfaces.length;i++){const p=surfaces[i],btn=document.createElement('button');btn.className='surface';
  const sw=document.createElement('div');sw.className='surface-row';const img=document.createElement('img');img.className='swatch';
  if(p.image)img.src=p.image;else img.alt='No verified tile thumbnail';
  const text=document.createElement('div');const title=document.createElement('div');title.className='surface-name';title.textContent=p.surface;const s=document.createElement('div');s.className='surface-sub';s.textContent=p.name+(/niche/i.test(p.surface)?' · geometry unavailable':'');
  text.append(title,s);sw.append(img,text);btn.append(sw);btn.addEventListener('click',()=>materialInspector(i));list.append(btn);}
 document.getElementById('material-info').hidden=true;frame();
 history.replaceState(null,'','#'+encodeURIComponent(rid));
}
const list=document.getElementById('room-list');for(const r of rooms){const b=document.createElement('button');b.className='room-btn';b.dataset.room=r.id;const dot=document.createElement('span');dot.className='room-dot'+(r.has_pick?'':' empty');const t=document.createElement('span');t.className='room-text';const code=document.createElement('div');code.className='room-code';code.textContent=r.id;const meta=document.createElement('div');meta.className='room-meta';meta.textContent=r.has_pick?'Provisional material palette':'No pick yet';t.append(code,meta);b.append(dot,t);b.addEventListener('click',()=>buildRoom(r.id));list.append(b);}
document.getElementById('reset').onclick=()=>frame();document.getElementById('alternative').onchange=e=>{altActive=!!e.target.checked&&!!currentRoom.alternative;buildRoom(currentRoom.id);};
document.getElementById('toggle-walls').onclick=()=>{wallVisible=!wallVisible;for(const p of parts)if(p.userData.category==='wall')p.visible=wallVisible;document.getElementById('toggle-walls').textContent=wallVisible?'Hide walls':'Show walls';};
document.getElementById('toggle-bounds').onclick=()=>{edgeVisible=!edgeVisible;document.getElementById('toggle-bounds').textContent=edgeVisible?'Hide edges':'Show edges';buildRoom(currentRoom.id);};
canvas.addEventListener('dblclick',frame);
document.getElementById('open-accuracy').onclick=()=>window.open('ACCURACY.md','_blank');
document.getElementById('copy-room').onclick=()=>navigator.clipboard?.writeText(currentRoom?.id||'');
const observer=new ResizeObserver(()=>{const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=Math.max(.1,w/h);camera.updateProjectionMatrix()});observer.observe(stage);
function animate(){requestAnimationFrame(animate);orbit.update();renderer.render(scene,camera)}animate();
buildRoom(rooms.some(r=>r.id===decodeURIComponent(location.hash.slice(1)))?decodeURIComponent(location.hash.slice(1)):'PH-BATH4');
