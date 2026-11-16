// Runs at the end of the viewer module, so it shares its scope: ROOMS, state,
// renderer, scene, camera, selectRoom, selectMaterial, setMode, setFocusView,
// gallery, productVendor, htmlEscape, rebuild, updateInstanceSelect.
// Presentation and convenience only: no pick, quantity, geometry or Revit
// record is created or changed here.
{
 const $=id=>document.getElementById(id);
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;};

 // ---- owner direction recorded 2026-11-09; deliberately NOT applied to any room
 // reviewer layout choices: per room type and per pick, kept in this browser
 const LAYOUT_KEY='wieland1529.tileLayout.v1';
 let layouts={};
 try{layouts=JSON.parse(localStorage.getItem(LAYOUT_KEY)||'{}')||{};}catch(e){layouts={};}
 const layoutId=index=>state.room+'|'+(state.alt?'alt':'pick')+'|'+index;
 const layoutOf=index=>layouts[layoutId(index)]||{turn:0,dx:0,dy:0};
 function setLayout(index,next){
  if(!next.turn&&!next.dx&&!next.dy)delete layouts[layoutId(index)];else layouts[layoutId(index)]=next;
  try{localStorage.setItem(LAYOUT_KEY,JSON.stringify(layouts));}catch(e){}
 }
 // ---- owner direction 2026-11-09: Penthouse Bath 3 uses the Triplex Bath 3
 // picks. Applied here at run time, surface for surface; the embedded frozen
 // record is not edited and frozen quantities are not recalculated.
 const OWNER_PICK_COPY=[{to:'PH-BATH3',from:'TX-BATH3'}];
 for(const {to,from} of OWNER_PICK_COPY){
  try{
   const a=ROOMS.find(r=>r.id===to),b=ROOMS.find(r=>r.id===from);
   if(a&&b)a.products.forEach((p,i)=>{
    const q=b.products.find(x=>x.surface===p.surface)||b.products[i];if(!q)return;
    Object.assign(p,{name:q.name,size:q.size,price:q.price,url:q.url,image:q.image,owner_pick_copy_from:from,
     source:'Owner direction 2026-11-09: use the Triplex Bath 3 picks in Penthouse Bath 3. Frozen quantities not recalculated.'});
   });
  }catch(e){runtimeErrors.push('OWNER PICK COPY: '+e.message);}
 }
 // ---- owner direction 2026-11-09: tile textures must show the INDIVIDUAL
 // tile as installed, not the vendor preview photo (which may be a room scene
 // or a mixed layout). Each sheet below is generated (tools/gen_tile_textures.py):
 // a small field of separately generated tiles, one tile per cell. The vendor
 // photos are no longer blended into any tile.
 const TILE_SHEETS=/*MC_TILE_SHEETS*/[];
 const sheetImages=new Map();
 await Promise.all(TILE_SHEETS.flatMap(sh=>['color','normal'].map(field=>new Promise(resolve=>{
  const img=new Image();
  img.onload=()=>{sheetImages.set(sh.key+'|'+field,img);resolve();};
  img.onerror=()=>{runtimeErrors.push('TILE SHEET: could not decode '+sh.key+' '+field);resolve();};
  img.src=sh[field];
 }))));
 const sheetFor=(p,pair)=>{
  const name=(p?.name||'').toLowerCase(),inches=pair.map(v=>Math.round(v*12*100)/100);
  const mine=TILE_SHEETS.filter(sh=>name.includes(sh.match)&&sheetImages.has(sh.key+'|color')&&sheetImages.has(sh.key+'|normal'));
  return mine.find(sh=>Math.abs(sh.size[0]-inches[0])<.01&&Math.abs(sh.size[1]-inches[1])<.01)||null;
 };
 const sheetPixels=img=>{
  const c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;
  const ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0);
  return {canvas:c,rgba:new Uint8Array(ctx.getImageData(0,0,c.width,c.height).data),width:c.width,height:c.height};
 };
 const baseTileAtlas=tileAtlas;
 tileAtlas=function(p,orientation){
  let pair=normalizeSize(p?.size);
  if(orientation==='floor'&&pair[0]<pair[1])pair=pair.slice().reverse();
  const sheet=sheetFor(p,pair);
  if(!sheet)return baseTileAtlas(p,orientation);
  const id=(p?.name||'neutral')+'|'+pair.join(',')+'|'+orientation;
  if(materialCache.has(id)&&materialCache.get(id).mcSheet)return materialCache.get(id);
  const color=sheetPixels(sheetImages.get(sheet.key+'|color')),normal=sheetPixels(sheetImages.get(sheet.key+'|normal'));
  const map=new THREE.CanvasTexture(color.canvas);map.wrapS=map.wrapT=THREE.RepeatWrapping;map.colorSpace=THREE.SRGBColorSpace;map.anisotropy=8;
  const nmap=new THREE.CanvasTexture(normal.canvas);nmap.wrapS=nmap.wrapT=THREE.RepeatWrapping;
  const val={map,normal:nmap,units:[pair[0]*sheet.grid[0],pair[1]*sheet.grid[1]],tile:pair,grid:sheet.grid,
   roughness:sheet.glossy?.2:.8,glossy:!!sheet.glossy,relief:!!sheet.relief,children:new Set(),surfaceTextures:new Map(),ready:Promise.resolve(),
   mcSheet:sheet.key,mcNote:sheet.note,pixels:color,normalPixels:normal};
  materialCache.set(id,val);
  return val;
 };
 const baseTileMaterial=tileMaterial;
 tileMaterial=function(p,width,height,orientation){
  const mat=baseTileMaterial.apply(this,arguments),atlas=mat?.userData?.atlas;
  if(!atlas?.mcSheet||!mat.map)return mat;
  // the stock full-room path copies the atlas at no more than 512 px; give
  // each material the sheet at its own resolution instead
  const own=(pix,srgb,from)=>{
   const t=new THREE.DataTexture(pix.rgba,pix.width,pix.height,THREE.RGBAFormat,THREE.UnsignedByteType);
   t.flipY=true;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.magFilter=THREE.LinearFilter;t.minFilter=THREE.LinearMipmapLinearFilter;
   t.generateMipmaps=true;t.anisotropy=8;if(srgb)t.colorSpace=THREE.SRGBColorSpace;
   t.repeat.copy(from.repeat);t.offset.copy(from.offset);t.needsUpdate=true;return t;
  };
  if(mat.map.isDataTexture){
   const old=[mat.map,mat.normalMap];
   mat.map=own(atlas.pixels,true,old[0]);mat.normalMap=own(atlas.normalPixels,false,old[0]);
   for(const t of old)t?.dispose();
  }
  const k=atlas.relief?.9:atlas.glossy?.55:.3;
  mat.normalScale.set(k,k);
  mat.roughness=atlas.glossy?.2:.78;mat.clearcoat=atlas.glossy?.55:.03;mat.clearcoatRoughness=atlas.glossy?.16:.8;
  if(mat.emissive&&!mat.map.isDataTexture)mat.emissiveIntensity=0;
  mat.userData.sourceStudy='GENERATED SINGLE-TILE TEXTURE from vendor facts and measured body colour; vendor photo not used as the tile. '+(atlas.mcNote||'');
  mat.userData.typedSourcePhoto=false;
  mat.needsUpdate=true;
  return mat;
 };
 materialCache.clear();
 // niche: owner direction 2026-11-09 - the niche runs the FULL LENGTH of the
 // wall it is on, its bottom is 4 ft above the floor and it is 1 ft 6 in tall.
 // Which wall, the 3 1/2 in depth and the sill stone are still placeholders.
 // The tile opening starts one sill thickness lower so the finished bottom
 // (top of the stone sill) sits at 48 in and the clear height is 18 in.
 const NICHE={h:18,d:3.5,sill:.75,overhang:.75,sillTop:48};
 const NICHE_KEY='wieland1529.niche.v1';
 let niches={};
 try{niches=JSON.parse(localStorage.getItem(NICHE_KEY)||'{}')||{};}catch(e){niches={};}
 const nicheOf=()=>({wall:0,...(niches[state.room+'|'+state.instance]||{})});
 function setNiche(next){
  niches[state.room+'|'+state.instance]=next;
  try{localStorage.setItem(NICHE_KEY,JSON.stringify(niches));}catch(e){}
 }
 let nicheState=null;
 const PENDING_SUBSTITUTION={
  name:'Luxe Dune Linear Porcelain Tile',vendor:'Floor & Decor / Vetta',sku:'101492288',
  size:'18×36 nominal (17.73×35.96 in actual), 8 mm',finish:'Beige, textured',use:'Wall only; vendor lists shower-wall suitability',
  price:'$5.99/SF observed 2026-11-09, before tax/freight; not a quote or reserved stock',
  url:'https://www.flooranddecor.com/porcelain-tile/luxe-dune-linear-porcelain-tile-101492288.html',
  replaces:'Serenity Sands Textured Tile, SKU 101306496, 14×39'};
 const FD_SKU_LIST=[
  '101492288 — Luxe Dune Linear — 18×36 (replaces Serenity Sands)',
  '101317949 — Luxe Sand Matte — 24×24',
  '101317865 — Luxe Sand Matte — 24×48',
  '110850387 — Pienza Terra Matte — 24×48',
  '100996800 — De Rossi Ivory Matte — 24×24',
  '100507722 — La Belle Purity High Gloss — 3×12',
  '100507706 — La Belle Antique Blue High Gloss — 3×12'].join('\n');

 // ---- helpers over the frozen record
 const skuOf=p=>(String(p?.name||'').match(/\b(\d{9})\b/)||[])[1]||'';
 const cleanName=p=>String(p?.name||'').replace(/\s*\b\d{9}\b/,'').replace(/^F&D\s+/,'').trim();
 const nominal=p=>String(p?.size||'').split(',')[0].replace(/\s*(wet wall|wet tub WALL|relief|glossy ceramic)$/i,'').replace(/x/i,'×').trim();
 const unitPrice=p=>(String(p?.price||'').match(/\$[\d.,]+\s*\/\s*SF/i)||[''])[0].replace(/\s/g,'');
 const areaOf=inst=>Number(inst?.architecture?.floor_polygon_area_ft2);
 const areaText=room=>{
  const a=room.physical_instances.map(areaOf).filter(Number.isFinite);
  if(!a.length)return '';
  const f=v=>v.toFixed(1);
  return (a.length>1&&Math.abs(a[0]-a[1])>.05?f(a[0])+' / '+f(a[1]):f(a[0]))+' SF';
 };
 const shortTitle=room=>room.title.replace('Primary Bathroom','Primary bath').replace('Powder Room','Powder');
 const uniqueSwatches=room=>{const seen=new Set(),out=[];
  for(const p of room.products||[]){if(p.image&&!seen.has(p.name)){seen.add(p.name);out.push(p);}}return out;};

 // ---- toast
 const toastNode=el('div','mc-toast');toastNode.setAttribute('role','status');document.body.append(toastNode);
 let toastTimer=0;
 function toast(message){toastNode.textContent=message;toastNode.classList.add('show');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>toastNode.classList.remove('show'),2600);}
 async function copyText(text,label){
  try{await navigator.clipboard.writeText(text);}
  catch(e){const t=el('textarea');t.value=text;t.style.cssText='position:fixed;opacity:0';document.body.append(t);t.select();
   let ok=false;try{ok=document.execCommand('copy');}catch(_){}t.remove();if(!ok){toast('Copy was blocked by the browser');return;}}
  toast(label+' copied');
 }

 // ---- room schedule: grouped by unit, room numbers + native area + swatches
 const baseUpdateRoomList=updateRoomList;
 updateRoomList=function(){
  baseUpdateRoomList();
  const list=$('room-list');const buttons=[...list.querySelectorAll('.room-btn')];
  let unit=null;
  ROOMS.forEach((room,i)=>{
   const b=buttons[i];if(!b)return;
   if(room.unit_type!==unit){unit=room.unit_type;
    const g=el('div','mc-room-group');
    const n=ROOMS.filter(r=>r.unit_type===unit);
    g.append(el('span',null,unit),el('span',null,n.filter(r=>r.has_pick).length+' of '+n.length+' with picks'));
    b.before(g);}
   b.querySelector('.room-code').textContent=shortTitle(room);
   b.querySelector('.room-meta').textContent=[room.numbers.join(' · '),areaText(room)].filter(Boolean).join('   ');
   b.title=room.id+' — '+(room.has_pick?'frozen provisional tile picks':'no tile pick yet');
   b.dataset.room=room.id;
   const sw=uniqueSwatches(room);
   if(sw.length){const wrap=el('span','mc-room-swatches');wrap.setAttribute('aria-hidden','true');
    for(const p of sw.slice(0,4)){const im=el('img');im.src=p.image;im.alt='';wrap.append(im);}b.append(wrap);}
   if(room.id===state.room)b.scrollIntoView({block:'nearest'});
  });
  syncStatus();
 };
 function syncStatus(){
  const room=ROOMS.find(r=>r.id===state.room),pill=$('mc-status-pill');if(!room||!pill)return;
  pill.className='status-pill'+(room.has_pick?'':' none');
  pill.textContent=room.has_pick?'Frozen provisional picks · not owner-approved':'No tile pick for this room';
 }
 // ---- stage heading: plain-language room name, with the native room number
 // (and the viewer-label alias where the two differ, e.g. PH WC 314 = native 313)
 const baseRebuild=rebuild;
 function syncHeading(){
  const room=ROOMS.find(r=>r.id===state.room),inst=room?.physical_instances?.[state.instance];if(!inst)return;
  const h=$('room-title');if(h)h.textContent=room.unit_type+' · '+room.title;
  const kicker=document.querySelector('#stage .stage-top .eyebrow');
  if(kicker){
   const native=inst.live_native_room_number&&String(inst.live_native_room_number)!==String(inst.room_number)
    ?' (native room '+inst.live_native_room_number+')':'';
   const a=areaOf(inst);
   kicker.textContent=[room.id,'Room '+inst.room_number+native,Number.isFinite(a)?a.toFixed(2)+' SF native boundary':null,
    state.mode==='full'?'Full bathroom':state.mode==='study'?'Wet-zone detail':'Native room'].filter(Boolean).join(' · ');
  }
  document.title=room.unit_type+' '+room.title+' '+inst.room_number+' — 1529 Wieland';
 }
 rebuild=function(){const out=baseRebuild.apply(this,arguments);
  try{buildNiche();keepTileScale();}catch(e){runtimeErrors.push('NICHE: '+e.message);}
  try{syncHeading();syncStatus();annotatePicks();}catch(e){runtimeErrors.push('HEADING: '+e.message);}return out;};
 const eyebrow=document.querySelector('aside.left>.eyebrow');
 if(eyebrow)eyebrow.textContent='Bathroom schedule · 13 types · 26 rooms';

 // ---- modal shell
 let openModal=null;
 function closeModal(){
  if(!openModal)return;const {scrim,restore}=openModal;openModal=null;
  scrim.classList.remove('open');document.body.classList.remove('mc-printing');
  setTimeout(()=>scrim.remove(),160);restore?.focus?.();
  $('mc-nav-viewer')?.classList.add('active');
  document.querySelectorAll('.site-navigation nav button:not(#mc-nav-viewer)').forEach(b=>b.classList.remove('active'));
 }
 function showModal({kicker,title,actions=[],body,narrow=false,navId}){
  closeModal();
  const scrim=el('div','mc-scrim'),modal=el('section','mc-modal'+(narrow?' narrow':''));
  modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-label',title);
  const head=el('div','mc-modal-head'),left=el('div');
  left.append(el('div','eyebrow',kicker),el('h2',null,title));
  const act=el('div','mc-modal-actions');
  for(const a of actions){const b=el('button','mc-btn'+(a.kind?' '+a.kind:''),a.label);b.type='button';b.onclick=a.run;act.append(b);}
  const close=el('button','mc-btn ink','Close');close.type='button';close.onclick=closeModal;act.append(close);
  head.append(left,act);
  const wrap=el('div','mc-modal-body');wrap.append(body);
  modal.append(head,wrap);scrim.append(modal);document.body.append(scrim);
  scrim.addEventListener('pointerdown',e=>{if(e.target===scrim)closeModal();});
  scrim.addEventListener('keydown',e=>{
   if(e.key!=='Tab')return;
   const f=[...modal.querySelectorAll('button,a[href],[tabindex="0"]')].filter(n=>n.offsetParent!==null);
   if(!f.length)return;const first=f[0],last=f[f.length-1];
   if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
   else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
  });
  openModal={scrim,restore:document.activeElement};
  requestAnimationFrame(()=>scrim.classList.add('open'));close.focus();
  if(navId){$('mc-nav-viewer')?.classList.remove('active');$(navId)?.classList.add('active');}
 }

 // ---- material board
 function goTo(roomId,productIndex){
  closeModal();
  if(state.focusView)setFocusView(false);
  if(state.room!==roomId)selectRoom(roomId);
  if(productIndex>=0)selectMaterial(productIndex);
  $('material-info')?.scrollIntoView({block:'nearest',behavior:'smooth'});
 }
 function scheduleRows(){
  const rows=[];
  for(const room of ROOMS){
   if(!room.products?.length){rows.push({room,index:-1});continue;}
   room.products.forEach((p,index)=>rows.push({room,p,index}));
  }
  return rows;
 }
 function scheduleTSV(){
  const head=['Unit','Room type','Room numbers','Native area SF (A / B)','Surface','Product','Nominal size','Vendor','SKU','Observed price','Status','URL'];
  const lines=[head.join('\t')];
  for(const {room,p} of scheduleRows()){
   lines.push([room.unit_type,room.title,room.numbers.join(' / '),areaText(room).replace(' SF',''),
    p?p.surface:'—',p?cleanName(p):'No tile pick',p?nominal(p):'',p?productVendor(p):'',p?skuOf(p):'',p?unitPrice(p):'',
    p?'Frozen provisional; not owner-approved':'No pick',p?p.url:''].join('\t'));
  }
  lines.push(['—','Unassigned','—','','Wall (placement not established)',PENDING_SUBSTITUTION.name,'18×36',
   'Floor & Decor',PENDING_SUBSTITUTION.sku,'$5.99/SF','Owner-directed substitution for Serenity Sands; pending placement; not rendered',PENDING_SUBSTITUTION.url].join('\t'));
  return lines.join('\n');
 }
 function buildBoard(){
  const body=el('div');
  const withPicks=ROOMS.filter(r=>r.has_pick);
  const distinct=new Map();
  for(const room of ROOMS)for(const p of room.products||[]){
   if(!distinct.has(p.name))distinct.set(p.name,{p,rooms:new Set(),surfaces:new Set(),first:{room:room.id,index:room.products.indexOf(p)}});
   const d=distinct.get(p.name);d.rooms.add(room.id);d.surfaces.add(/wall/i.test(p.surface)?'wall':/niche/i.test(p.surface)?'niche':'floor / pan');
  }
  const metrics=el('div','mc-metrics');
  for(const [n,l] of [[ROOMS.length,'Bathroom types'],[ROOMS.reduce((a,r)=>a+r.physical_instances.length,0),'Physical A/B rooms'],
   [withPicks.length+' / '+ROOMS.length,'Types with frozen picks'],[distinct.size,'Distinct products in use']]){
   const d=el('div');d.append(el('strong',null,String(n)),el('span',null,l));metrics.append(d);}
  body.append(metrics);

  // palette
  const pal=el('section','mc-section');
  pal.append(el('h3',null,'Palette'),el('p',null,'Every product currently applied in the viewer. Maker imagery is a digital stand-in, not a physical sample. Select a tile to open the first room that uses it.'));
  const grid=el('div','mc-palette');
  for(const d of distinct.values()){
   const c=el('button','mc-chip');c.type='button';
   if(d.p.image){const im=el('img');im.src=d.p.image;im.alt=cleanName(d.p)+' maker image';im.loading='lazy';c.append(im);}
   else c.append(el('div','mc-noimg','No maker image'));
   const b=el('div','mc-chip-body');
   b.append(el('b',null,cleanName(d.p)),el('span',null,[productVendor(d.p),nominal(d.p)].filter(Boolean).join(' · ')));
   if(skuOf(d.p))b.append(el('span','mc-sku',skuOf(d.p)));
   b.append(el('span',null,[...d.surfaces].join(', ')+' — '+[...d.rooms].join(', ')));
   c.append(b);c.onclick=()=>goTo(d.first.room,d.first.index);grid.append(c);
  }
  const pend=el('div','mc-chip pending');
  pend.append(el('div','mc-noimg','Not in image set'));
  const pb=el('div','mc-chip-body');
  pb.append(el('span','mc-tag','Pending placement'),el('b',null,'Luxe Dune Linear'),el('span',null,'Floor & Decor · 18×36'),
   el('span','mc-sku',PENDING_SUBSTITUTION.sku),el('span',null,'Replaces Serenity Sands; no room assigned'));
  pend.append(pb);grid.append(pend);
  pal.append(grid);body.append(pal);

  // schedule
  const sch=el('section','mc-section');
  sch.append(el('h3',null,'Room schedule'),el('p',null,'A and B rooms of a type share one material program. Areas are native Revit Room boundaries from the November 9 audit; frozen procurement quantities were not recalculated from them. Select a row to inspect that surface in 3D.'));
  const wrap=el('div','mc-table-wrap'),table=el('table','mc-table');
  table.innerHTML='<thead><tr><th>Room</th><th class="num">Area A / B</th><th>Surface</th><th></th><th>Product</th><th>Size</th><th>Vendor</th><th>SKU</th><th class="num">Observed</th><th></th></tr></thead>';
  const tb=el('tbody');let unit=null,lastRoom=null;
  for(const {room,p,index} of scheduleRows()){
   if(room.unit_type!==unit){unit=room.unit_type;const tr=el('tr','mc-unit');const td=el('td',null,unit);td.colSpan=10;tr.append(td);tb.append(tr);}
   const tr=el('tr','mc-row');tr.tabIndex=0;
   const first=room!==lastRoom;lastRoom=room;
   const tdRoom=el('td','room');
   if(first){tdRoom.append(el('b',null,shortTitle(room)),el('small',null,room.numbers.join(' · ')));}
   const tdArea=el('td','num',first?areaText(room).replace(' SF',''):'');
   tr.append(tdRoom,tdArea);
   if(!p){const td=el('td','nopick','No tile pick — surfaces stay neutral');td.colSpan=8;tr.append(td);}
   else{
    const tdImg=el('td');if(p.image){const im=el('img');im.src=p.image;im.alt='';im.loading='lazy';tdImg.append(im);}
    const tdLink=el('td');const a=el('a',null,'Product page');a.href=p.url;a.target='_blank';a.rel='noopener noreferrer';
    a.onclick=e=>e.stopPropagation();tdLink.append(a);
    tr.append(el('td',null,p.surface),tdImg,el('td',null,cleanName(p)),el('td',null,nominal(p)),
     el('td',null,productVendor(p)),el('td','sku',skuOf(p)||'—'),el('td','num',unitPrice(p)||'—'),tdLink);
   }
   const open=()=>goTo(room.id,index);
   tr.onclick=open;tr.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}};
   tb.append(tr);
  }
  table.append(tb);wrap.append(table);sch.append(wrap);body.append(sch);

  // F&D list + pending substitution
  const sku=el('section','mc-section');
  sku.append(el('h3',null,'Floor & Decor SKU list'),el('p',null,'The owner’s current list, verbatim, including the November 9 substitution. Prices seen on vendor pages are observations, not a Chicago quote or reserved stock.'));
  const g=el('div','mc-skugrid');
  const left=el('div');const pre=el('pre','mc-pre',FD_SKU_LIST);left.append(pre);
  const note=el('div','mc-note');
  note.innerHTML='<b>Luxe Dune Linear replaces Serenity Sands — placement pending.</b> The substitution is recorded on the list, but neither tile appears in the frozen room picks, so the room and wall it belongs to has not been established. It is not rendered anywhere in the viewer and is not merged with Luxe Sand Matte.'+
   '<dl><dt>SKU</dt><dd>'+PENDING_SUBSTITUTION.sku+'</dd><dt>Size</dt><dd>'+htmlEscape(PENDING_SUBSTITUTION.size)+'</dd>'+
   '<dt>Finish</dt><dd>'+htmlEscape(PENDING_SUBSTITUTION.finish)+'</dd><dt>Use</dt><dd>'+htmlEscape(PENDING_SUBSTITUTION.use)+'</dd>'+
   '<dt>Price</dt><dd>'+htmlEscape(PENDING_SUBSTITUTION.price)+'</dd><dt>Replaces</dt><dd>'+htmlEscape(PENDING_SUBSTITUTION.replaces)+'</dd>'+
   '<dt>Source</dt><dd><a href="'+PENDING_SUBSTITUTION.url+'" target="_blank" rel="noopener noreferrer">Vendor product page</a></dd></dl>';
  g.append(left,note);sku.append(g);body.append(sku);
  return body;
 }
 function openBoard(){
  showModal({kicker:'1529 Wieland · frozen provisional selections',title:'Material board',navId:'mc-nav-board',body:buildBoard(),actions:[
   {label:'Copy F&D SKU list',kind:'primary',run:()=>copyText(FD_SKU_LIST,'F&D SKU list')},
   {label:'Copy schedule for Sheets',run:()=>copyText(scheduleTSV(),'Schedule (tab-separated)')},
   {label:'Print',run:()=>{document.body.classList.add('mc-printing');window.print();}}]});
 }
 window.addEventListener('afterprint',()=>document.body.classList.remove('mc-printing'));

 // ---- shortcuts sheet
 function openHelp(){
  const body=el('div');const dl=el('dl','mc-keys');
  const rows=[[['↑','↓'],'Previous / next bathroom type'],[['A','B'],'Switch to the A or B room'],[['1','2','3'],'Full bathroom · wet-zone detail · native room'],
   [['F'],'Isometric camera'],[['P'],'Plan camera'],[['I'],'Cutaway camera'],[['K'],'Fixture focus camera'],[['V'],'Interior reveal on / off'],
   [['C'],'Compare A and B plans'],[['R'],'Reset view'],[['Enter'],'Focus view (Esc to leave)'],[['M'],'Material board'],[['G'],'Room gallery'],
   [['S'],'Save the current view as a PNG'],[['?'],'This sheet']];
  for(const [keys,label] of rows){const dt=el('dt');for(const k of keys)dt.append(el('kbd',null,k));dl.append(dt,el('dd',null,label));}
  body.append(dl);
  const p=el('p','muted','Drag to orbit, Shift + drag to pan, scroll to zoom, double-click to reset. Click any tiled surface to inspect its product.');
  p.style.marginTop='14px';body.append(p);
  showModal({kicker:'Viewer',title:'Keyboard shortcuts',navId:'mc-nav-help',body,narrow:true});
 }

 // ---- captioned PNG of the current view
 function saveView(){
  renderer.render(scene,camera);
  const src=renderer.domElement,scale=src.width/Math.max(1,src.clientWidth);
  const bar=Math.round(64*scale),c=document.createElement('canvas');c.width=src.width;c.height=src.height+bar;
  const g=c.getContext('2d');
  g.fillStyle='#f1f2ef';g.fillRect(0,0,c.width,src.height);
  g.strokeStyle='rgba(0,0,0,.035)';g.lineWidth=1;const step=48*scale;
  for(let x=.5;x<c.width;x+=step){g.beginPath();g.moveTo(x,0);g.lineTo(x,src.height);g.stroke();}
  for(let y=.5;y<src.height;y+=step){g.beginPath();g.moveTo(0,y);g.lineTo(c.width,y);g.stroke();}
  g.drawImage(src,0,0);
  g.fillStyle='#ffffff';g.fillRect(0,src.height,c.width,bar);
  g.fillStyle='#000000';g.fillRect(0,src.height,c.width,Math.max(1,Math.round(scale)));
  const room=ROOMS.find(r=>r.id===state.room),inst=room.physical_instances[state.instance];
  const pad=18*scale;g.textBaseline='alphabetic';
  g.fillStyle='#000';g.font='500 '+Math.round(15*scale)+'px Inter, Arial, sans-serif';
  g.fillText(room.unit_type+' '+room.title+' — room '+inst.room_number,pad,src.height+27*scale);
  g.fillStyle='#68706b';g.font='500 '+Math.round(9.5*scale)+'px Inter, Arial, sans-serif';
  const picks=(room.products||[]).filter(p=>!/niche|conditional/i.test(p.surface)).map(p=>cleanName(p)+' '+nominal(p)).join('  ·  ')||'No tile pick';
  g.fillText(('1529 WIELAND  ·  '+picks).toUpperCase(),pad,src.height+46*scale,c.width-pad*2-190*scale);
  g.textAlign='right';
  g.fillText(('Provisional study · not for construction · '+new Date().toISOString().slice(0,10)).toUpperCase(),c.width-pad,src.height+27*scale);
  c.toBlob(blob=>{
   if(!blob){toast('The view could not be exported');return;}
   const a=el('a');a.href=URL.createObjectURL(blob);a.download='1529-Wieland_'+room.id+'_'+inst.room_number+'.png';
   document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);
   toast('Saved '+a.download);
  },'image/png');
 }

 // ---- wiring
 $('mc-nav-board').onclick=openBoard;
 $('mc-nav-help').onclick=openHelp;
 $('mc-nav-save').onclick=saveView;
 $('mc-nav-viewer').onclick=()=>{closeModal();$('viewer-gallery-close')?.click();};
 $('mc-nav-gallery').onclick=()=>{closeModal();gallery().catch(e=>runtimeErrors.push('GALLERY: '+e.message));};
 function stepRoom(delta){
  const i=ROOMS.findIndex(r=>r.id===state.room);
  selectRoom(ROOMS[(i+delta+ROOMS.length)%ROOMS.length].id);
 }
 document.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&openModal){e.preventDefault();e.stopImmediatePropagation();closeModal();return;}
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  if(e.target?.matches?.('input,textarea,select'))return;
  if(openModal){if(/^[a-z0-9]$/i.test(e.key))e.stopImmediatePropagation();return;}
  if($('viewer-gallery'))return;
  const k=e.key.toLowerCase();
  if(e.key==='ArrowDown'||k===']'){e.preventDefault();stepRoom(1);}
  else if(e.key==='ArrowUp'||k==='['){e.preventDefault();stepRoom(-1);}
  else if(k==='m')openBoard();
  else if(k==='g')$('mc-nav-gallery').click();
  else if(k==='s')saveView();
  else if(k==='r')$('reset')?.click();
  else if(e.key==='?')openHelp();
  else if(e.key==='Enter'&&e.target===document.body&&!state.focusView)setFocusView(true);
 },true);

 // ---- tile audit: measures what is actually in the scene, independent of
 // camera, cutaway and wall-hide state. Read-only.
 function auditTiles(){
  const room=ROOMS.find(r=>r.id===state.room),inst=room.physical_instances[state.instance];
  const products=room.products||[],source=nativeCase(room,inst);
  const atlasName=new Map();for(const [key,val] of materialCache)atlasName.set(val,key.split('|')[0]);
  modelGroup.updateMatrixWorld(true);
  const surfaces=[],fixtures=[];
  for(const o of renderObjects){
   const u=o.userData||{};
   if(o.isMesh&&u.native_geometry&&(u.fixture_kind||/plumbing|specialty|casework|generic/i.test(u.source_category||''))){
    const b=new THREE.Box3().setFromObject(o);
    fixtures.push({id:u.revit_id,kind:u.fixture_kind,category:u.source_category,family:u.family_name,
     min:b.min.toArray().map(v=>+v.toFixed(3)),max:b.max.toArray().map(v=>+v.toFixed(3))});
   }
   const m=o.material;if(!o.isMesh||!m?.userData?.pooledTile)continue;
   const g=o.geometry;g.computeBoundingBox();
   const box=new THREE.Box3().setFromObject(o),size=box.getSize(new THREE.Vector3());
   const n=new THREE.Vector3(0,0,1).applyQuaternion(o.getWorldQuaternion(new THREE.Quaternion()));
   const horizontal=Math.abs(n.y)>.9;
   const pos=g.attributes.position,uv=g.attributes.uv;
   // texture cycles per foot, from two vertices' position and UV deltas
   let perFt=null;
   if(pos&&uv){
    let uMin=1e9,uMax=-1e9,vMin=1e9,vMax=-1e9,xMin=1e9,xMax=-1e9,yMin=1e9,yMax=-1e9;
    for(let i=0;i<pos.count;i++){const x=pos.getX(i),y=pos.getY(i),a=uv.getX(i),b=uv.getY(i);
     uMin=Math.min(uMin,a);uMax=Math.max(uMax,a);vMin=Math.min(vMin,b);vMax=Math.max(vMax,b);
     xMin=Math.min(xMin,x);xMax=Math.max(xMax,x);yMin=Math.min(yMin,y);yMax=Math.max(yMax,y);}
    const sx=o.getWorldScale(new THREE.Vector3());
    perFt=Math.abs(m.map.rotation)>.1
     ?[(uMax-uMin)*m.map.repeat.y/((xMax-xMin)*sx.x),(vMax-vMin)*m.map.repeat.x/((yMax-yMin)*sx.y)]
     :[(uMax-uMin)*m.map.repeat.x/((xMax-xMin)*sx.x),(vMax-vMin)*m.map.repeat.y/((yMax-yMin)*sx.y)];
   }
   const grid=m.userData.atlas?.grid||[1,1],turnedGrid=Math.abs(m.map.rotation)>.1?[grid[1],grid[0]]:grid;
   const drawnIn=perFt?perFt.map((c,k)=>+(12/(c*turnedGrid[k])).toFixed(2)):null;
   const indexed=products[u.surfaceIndex];
   surfaces.push({category:u.category,surfaceIndex:u.surfaceIndex,recordSurface:indexed?.surface||null,recordProduct:indexed?.name||null,
    materialProduct:atlasName.get(m.userData.atlas)||null,nominalIn:(m.userData.atlas?.tile||m.userData.atlas?.units||[]).map(v=>+(v*12).toFixed(2)),drawnIn,
    texture:m.userData.atlas?.mcSheet||'vendor photo blend',
    turned:Math.abs(m.map.rotation)>.1,shiftIn:[layoutOf(u.surfaceIndex).dx,layoutOf(u.surfaceIndex).dy],
    horizontal,normal:n.toArray().map(v=>+v.toFixed(2)),hostWall:u.native_host_face_id||null,aligned:u.native_finish_face_aligned||false,
    clipped:u.native_finish_face_clip??null,visible:o.visible&&o.parent?.visible!==false,
    min:box.min.toArray().map(v=>+v.toFixed(3)),max:box.max.toArray().map(v=>+v.toFixed(3)),
    areaSf:+(horizontal?size.x*size.z:Math.hypot(size.x,size.z)*size.y).toFixed(2)});
  }
  return {niche:nicheState?{wall:nicheState.wallIndex,walls:nicheState.walls,widthIn:nicheState.widthIn,heightIn:nicheState.heightIn,depthIn:nicheState.depthIn,
    sillTopIn:nicheState.sillTopIn,offsetIn:nicheState.offsetIn,product:nicheState.product,usesWallTile:nicheState.usesWallTile,hostWall:nicheState.hostWall,
    visible:nicheState.group.visible,cutsNativeWall:!!nicheState.wallMesh,sill:nicheState.group.children.some(c=>c.userData.category==='OWNER_NICHE_SILL')}:null,
   room:room.id,instance:inst.room_number,mode:state.mode,program:room.program?.kind||null,
   wetSide:{shower:inst.plan_shower_side??null,entry:inst.plan_entry_side??null,handed:inst.plan_handedness??null},
   products:products.map(p=>({surface:p.surface,name:p.name,size:p.size})),surfaces,fixtures,
   holds:source?(nativeFinishHolds.get(source.key)||[]):null,native:!!source,
   polygon:source?.rings_local_xz_ft?.[0]||null};
 }

 // ---- owner direction 2026-11-09: Triplex Bath 3 and Penthouse Bath 4 are
 // tiled on THREE walls (back wall plus both side walls of the shower end).
 // The back wall the viewer already draws is kept as the reference; it is
 // widened to the full native room width where it stopped short, and a side
 // return is added on each native side wall for the frozen wet-zone depth.
 // Display only: the frozen quantity pools are not recalculated here.
 const OWNER_THREE_WALL=new Set(['TX-BATH3','PH-BATH4']);
 const baseBuildFullRoom=buildFullRoom;
 function completeThreeWalls(room){
  const source=nativeCase(room,instance());if(!source)return;
  const wp=productFor('wall');if(!wp)return;
  const index=productList().indexOf(wp);
  const poly=source.rings_local_xz_ft?.[0];if(!poly)return;
  const lo=[Math.min(...poly.map(p=>p[0])),Math.min(...poly.map(p=>p[1]))];
  const hi=[Math.max(...poly.map(p=>p[0])),Math.max(...poly.map(p=>p[1]))];
  modelGroup.updateMatrixWorld(true);
  const tiled=renderObjects.filter(o=>o.isMesh&&o.userData?.category==='FULL_ROOM_WET_WALL'&&o.material?.userData?.pooledTile)
   .map(o=>{const b=new THREE.Box3().setFromObject(o),s=b.getSize(new THREE.Vector3());
    return {o,b,alongX:s.x>s.z,span:Math.max(s.x,s.z),height:o.geometry.parameters?.height||s.y};});
  if(!tiled.length)return;
  const back=tiled.reduce((a,c)=>c.span*c.height>a.span*a.height?c:a);
  const ax=back.alongX?0:1,nx=1-ax;                      // ax: axis the back wall runs along; nx: its normal axis
  const center=[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2];
  const backMid=back.b.getCenter(new THREE.Vector3()),plane=nx===0?backMid.x:backMid.z;
  const inward=Math.sign(center[nx]-plane)||1;
  const height=back.height;
  const depth=Math.min(Number(room.wet_zone_schematic?.depth?.value)||2.5,Math.abs((inward>0?hi[nx]:lo[nx])-plane));
  const note={owner_directed_three_wall:true,source:'Owner direction 2026-11-09: tile on three walls. Position follows the native room boundary; depth is the frozen wet-zone depth. Display only; frozen quantities unchanged.'};
  const hostFor=(axis,value)=>source.elements.find(e=>e.category==='Walls'&&(e.outward_faces||[]).some(f=>
   Math.abs(f.normal_xz[axis])>.9&&Math.abs(f.mid_xz[axis]-value)<.12))?.id||null;
  const place=(width,along,normalAxis,normalValue,facing,extra)=>{
   const pos=[0,height/2,0];pos[normalAxis===0?0:2]=normalValue+facing*.006;pos[normalAxis===0?2:0]=along;
   const ry=normalAxis===1?(facing>0?0:Math.PI):(facing>0?Math.PI/2:-Math.PI/2);
   return addPlane(width,height,pos,[0,ry,0],tileMaterial(wp,width,height,'wall'),'FULL_ROOM_WET_WALL',index,
    {...note,native_host_face_id:hostFor(normalAxis,normalValue),...extra});
  };
  // back wall: full room width
  const bLo=ax===0?back.b.min.x:back.b.min.z,bHi=ax===0?back.b.max.x:back.b.max.z;
  if(bLo-lo[ax]>.05||hi[ax]-bHi>.05){
   const old=back.o;old.removeFromParent();old.geometry?.dispose();
   renderObjects=renderObjects.filter(o=>o!==old);materialObjects=materialObjects.filter(o=>o!==old);
   place(hi[ax]-lo[ax],(lo[ax]+hi[ax])/2,nx,plane-inward*.006,inward,{three_wall_role:'back'});
  }
  // side returns on both native side walls
  for(const [edge,facing] of [[lo[ax],1],[hi[ax],-1]]){
   const has=tiled.some(t=>t.o!==back.o&&t.alongX!==back.alongX&&
    Math.abs((ax===0?t.b.getCenter(new THREE.Vector3()).x:t.b.getCenter(new THREE.Vector3()).z)-edge)<.3);
   if(has)continue;
   place(depth,plane+inward*depth/2,ax,edge,facing,{three_wall_role:'return',three_wall_inward:[ax===0?facing:0,ax===0?0:facing],three_wall_full_height:height});
  }
 }
 // ---- owner direction 2026-11-09: Triplex Bath 4 has NO tub; it has a
 // 3' 5 1/4" x 3' 1 3/4" shower. Neither the plan nor the model draws it. The
 // only place in the native room boundary those dimensions fit is the corner
 // between the chase, the exterior end wall and the opposite side wall, so the
 // frozen wall tile is drawn on those three native faces. The dimension that
 // matches the native wall-to-wall span runs across; the other runs along.
 // Display only: frozen picks and quantities are unchanged.
 const OWNER_SHOWER={'TX-BATH4':{dims:[3+5.25/12,3+1.75/12]}};
 function tileOwnerShower(room){
  const spec=OWNER_SHOWER[room.id],source=nativeCase(room,instance());if(!source)return;
  const wp=productFor('wall');if(!wp)return;
  const index=productList().indexOf(wp);
  const poly=source.rings_local_xz_ft?.[0];if(!poly)return;
  const lo=[Math.min(...poly.map(p=>p[0])),Math.min(...poly.map(p=>p[1]))];
  const hi=[Math.max(...poly.map(p=>p[0])),Math.max(...poly.map(p=>p[1]))];
  const near=(a,b)=>Math.abs(a-b)<.03;
  const corner=[[lo[0],lo[1]],[lo[0],hi[1]],[hi[0],lo[1]],[hi[0],hi[1]]].find(c=>!poly.some(p=>near(p[0],c[0])&&near(p[1],c[1])));
  const inner=poly.find(p=>!near(p[0],lo[0])&&!near(p[0],hi[0])&&!near(p[1],lo[1])&&!near(p[1],hi[1]));
  if(!corner||!inner)return;
  const zFar=near(corner[1],lo[1])?hi[1]:lo[1];
  const xs=Math.sign(inner[0]-corner[0]),zs=Math.sign(zFar-inner[1]);
  const span=Math.abs(zFar-inner[1]),chase=Math.abs(inner[0]-corner[0]);
  const [a,b]=spec.dims,along=Math.abs(a-span)<=Math.abs(b-span)?b:a;
  const height=Number(instance()?.architecture?.native_ceiling_evidence?.underside_height_ft)||
   Math.min(...source.elements.filter(e=>e.category==='Walls').map(e=>Number(e.height_ft)||0).filter(h=>h>6),9.25);   // lowest native wall bounding the room
  const note={owner_directed_three_wall:true,owner_shower:true,three_wall_role:'return',three_wall_full_height:height,
   source:'Owner direction 2026-11-09: Triplex Bath 4 has a 3 ft 5 1/4 in x 3 ft 1 3/4 in shower, no tub. Placed in the only corner of the native room boundary where it fits. Display only; frozen quantities unchanged.'};
  const hostFor=(axis,value)=>source.elements.find(e=>e.category==='Walls'&&(e.outward_faces||[]).some(f=>
   Math.abs(f.normal_xz[axis])>.9&&Math.abs(f.mid_xz[axis]-value)<.12))?.id||null;
  const place=(width,center,normalAxis,normalValue,facing)=>{
   const pos=[0,height/2,0];pos[normalAxis===0?0:2]=normalValue+facing*.006;pos[normalAxis===0?2:0]=center;
   const ry=normalAxis===1?(facing>0?0:Math.PI):(facing>0?Math.PI/2:-Math.PI/2);
   return addPlane(width,height,pos,[0,ry,0],tileMaterial(wp,width,height,'wall'),'FULL_ROOM_WET_WALL',index,
    {...note,native_host_face_id:hostFor(normalAxis,normalValue),three_wall_inward:normalAxis===0?[facing,0]:[0,facing]});
  };
  place(span,(inner[1]+zFar)/2,0,corner[0],xs);                                   // exterior end wall
  const cw=Math.min(along,chase);place(cw,corner[0]+xs*cw/2,1,inner[1],zs);       // chase face
  place(along,corner[0]+xs*along/2,1,zFar,-zs);                                   // opposite side wall
 }
 buildFullRoom=function(room){
  const out=baseBuildFullRoom.apply(this,arguments);
  if(OWNER_THREE_WALL.has(room.id)){try{completeThreeWalls(room);}catch(e){runtimeErrors.push('THREE WALL: '+e.message);}}
  if(OWNER_SHOWER[room.id]){try{tileOwnerShower(room);}catch(e){runtimeErrors.push('OWNER SHOWER: '+e.message);}}
  return out;
 };
 // an added return that stands between the camera and the room is sectioned
 // to the same 2.35 ft the viewer uses for its own camera-facing walls
 function sectionAddedReturns(){
  const active=state.mode==='full'&&state.walls&&state.interiorReveal&&state.preset!=='wet';
  for(const o of renderObjects){
   const u=o.userData||{};if(!u.owner_directed_three_wall||u.three_wall_role!=='return')continue;
   const full=u.three_wall_full_height,n=u.three_wall_inward;
   const behind=(camera.position.x-o.position.x)*n[0]+(camera.position.z-o.position.z)*n[1]<0;
   const shown=active&&behind?Math.min(full,2.35):full;
   o.scale.y=shown/full;o.position.y=shown/2;o.visible=state.walls;
  }
 }

 // ---- owner direction 2026-11-09: a niche in every tub/shower room. The
 // niche is a real recess: the wall tile gets an opening, the native wall is
 // cut back with a clip box, the back, both sides and the top carry the niche
 // tile (the wall tile where no niche tile is picked) and the bottom is a
 // stone sill that projects 3/4 in past the tile face.
 // triangles of a flat tile plane as [x,y,u,v] corners (null if not flat)
 function planeTris(geo){
  const pos=geo?.attributes?.position,uv=geo?.attributes?.uv,idx=geo?.index;if(!pos||!uv)return null;
  const n=idx?idx.count:pos.count,tris=[];
  const at=i=>{const k=idx?idx.getX(i):i;return [pos.getX(k),pos.getY(k),uv.getX(k),uv.getY(k),pos.getZ(k)];};
  for(let i=0;i+2<n;i+=3){const t=[at(i),at(i+1),at(i+2)];if(t.some(v=>Math.abs(v[4])>1e-3))return null;tris.push(t);}
  return tris;
 }
 function splitPoly(poly,axis,value){
  const less=[],more=[];
  for(let i=0;i<poly.length;i++){
   const p=poly[i],q=poly[(i+1)%poly.length],dp=p[axis]-value,dq=q[axis]-value;
   if(dp<=0)less.push(p);if(dp>=0)more.push(p);
   if((dp<0&&dq>0)||(dp>0&&dq<0)){const t=dp/(dp-dq),m=p.map((v,k)=>v+(q[k]-v)*t);less.push(m);more.push(m);}
  }
  return [less,more];
 }
 const polyArea=p=>{let s=0;for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length];s+=a[0]*b[1]-b[0]*a[1];}return Math.abs(s)/2;};
 // cut a rectangular opening out of any flat tile plane, keeping its UV layout;
 // also reports how much of the rectangle the plane actually covered
 function cutRect(geo,rect){
  const tris=planeTris(geo);if(!tris)return null;
  const [hx0,hx1,hy0,hy1]=rect,keep=[];let inside=0;
  for(const tri of tris){
   let rest=tri,part;
   [part,rest]=splitPoly(rest,0,hx0);if(part.length>2)keep.push(part);
   [rest,part]=splitPoly(rest,0,hx1);if(part.length>2)keep.push(part);
   [part,rest]=splitPoly(rest,1,hy0);if(part.length>2)keep.push(part);
   [rest,part]=splitPoly(rest,1,hy1);if(part.length>2)keep.push(part);
   if(rest.length>2)inside+=polyArea(rest);
  }
  const P=[],U=[],N=[];
  const nz=geo.attributes.normal&&geo.attributes.normal.getZ(0)<0?-1:1;
  for(const poly of keep){
   if(polyArea(poly)<1e-8)continue;
   for(let i=1;i+1<poly.length;i++)for(const v of [poly[0],poly[i],poly[i+1]]){P.push(v[0],v[1],0);U.push(v[2],v[3]);N.push(0,0,nz);}
  }
  const out=new THREE.BufferGeometry();
  out.setAttribute('position',new THREE.Float32BufferAttribute(P,3));
  out.setAttribute('uv',new THREE.Float32BufferAttribute(U,2));
  out.setAttribute('normal',new THREE.Float32BufferAttribute(N,3));
  if(geo.parameters)out.parameters=geo.parameters;
  out.computeBoundingBox();out.computeBoundingSphere();
  return {geometry:out,inside};
 }
 function planeBox(geo){
  const pos=geo?.attributes?.position;if(!pos||!geo.attributes.uv)return null;
  let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  for(let i=0;i<pos.count;i++){x0=Math.min(x0,pos.getX(i));x1=Math.max(x1,pos.getX(i));y0=Math.min(y0,pos.getY(i));y1=Math.max(y1,pos.getY(i));}
  return {x0,x1,y0,y1,w:x1-x0,h:y1-y0};
 }
 const NICHE_CATS=['FULL_ROOM_WET_WALL','ARCH_R059_FULL_HEIGHT_FINISH_REVIEW'];
 // a sectioned wall is scaled about its base; work from the unscaled origin
 const originOf=(o,r)=>new THREE.Vector3(o.position.x,o.position.y+r.y0*o.scale.y-r.y0,o.position.z);
 function nicheWalls(){
  modelGroup.updateMatrixWorld(true);
  const walls=[];
  for(const o of renderObjects){
   if(!o.isMesh||!NICHE_CATS.includes(o.userData?.category)||!o.material?.userData?.pooledTile)continue;
   const r=planeBox(o.geometry);if(!r||r.w<1||r.h<(NICHE.sillTop+NICHE.h+2)/12)continue;
   const normal=new THREE.Vector3(0,0,1).applyEuler(o.rotation);
   const wall={o,r,w:r.w,h:r.h,area:r.w*r.h,normal};
   const k=walls.findIndex(q=>Math.abs(q.normal.dot(normal))>.99&&Math.hypot(q.o.position.x-o.position.x,q.o.position.z-o.position.z)<.05);
   if(k<0)walls.push(wall);else if(wall.h>walls[k].h)walls[k]=wall;
  }
  return walls.sort((a,b)=>b.area-a.area);
 }
 // try to put the niche on one wall; null when the wall cannot take it
 function nicheOn(pick,cfg,minDepth){
  const host=pick.o,t=NICHE.sill/12,W=pick.w,H=NICHE.h/12+t;
  const b=physicalBounds(),roomC=b&&!b.isEmpty()?b.getCenter(new THREE.Vector3()):new THREE.Vector3();
  const origin=originOf(host,pick.r);
  const flip=pick.normal.dot(new THREE.Vector3(roomC.x-host.position.x,0,roomC.z-host.position.z))<0;   // plane drawn facing the wall
  const group=new THREE.Group();group.position.copy(origin);group.quaternion.copy(host.quaternion);
  if(flip)group.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI));
  modelGroup.add(group);group.updateMatrixWorld(true);
  const alongG=new THREE.Vector3(1,0,0).applyQuaternion(group.quaternion);
  const midHost=(pick.r.x0+pick.r.x1)/2,mid=flip?-midHost:midHost;        // wall centre in the group frame
  const bottom=NICHE.sillTop/12-t;                                        // tile opening bottom; sill top lands on 48 in
  const cy=pick.r.y0+bottom+H/2;
  // host-local rectangle for a mesh on this wall face (a hair wider than the
  // face so the opening runs cleanly out of both ends)
  const rectFor=(o,r,gx)=>{
   const rel=origin.clone().addScaledVector(alongG,gx).sub(originOf(o,r));
   if(Math.abs(rel.dot(new THREE.Vector3(0,0,1).applyEuler(o.rotation)))>.03)return null;
   const x=rel.dot(new THREE.Vector3(1,0,0).applyEuler(o.rotation)),y=cy+rel.y;
   return [x-W/2-.02,x+W/2+.02,y-H/2,y+H/2];
  };
  // the tile face must cover the whole strip: a wall with a door, window or
  // other gap in that band cannot carry a full-length niche
  const gx=mid,strip=cutRect(host.geometry,rectFor(host,pick.r,gx));
  const fail=()=>{group.removeFromParent();return null;};
  if(!strip||strip.inside<W*H*.985)return fail();
  // native wall behind the opening, and how deep it lets the recess go
  const probe=new THREE.Vector3(gx,cy,-.12).applyMatrix4(group.matrixWorld);
  const axis=Math.abs(pick.normal.x)>Math.abs(pick.normal.z)?'x':'z';
  let wallMesh=null,thickness=null;
  for(const m of nativeRendered){
   if(!m.parent||m.userData.source_category!=='Walls')continue;
   const box=new THREE.Box3().setFromObject(m);
   if(box.containsPoint(probe)&&box.max[axis]-box.min[axis]>(thickness||0)){wallMesh=m;thickness=box.max[axis]-box.min[axis];}
  }
  const D=wallMesh?Math.min(NICHE.d/12,Math.max(0,thickness-1/12)):NICHE.d/12;
  if(D<minDepth||(!wallMesh&&minDepth>2/12))return fail();
  const hosts=[];
  for(const o of renderObjects){
   if(!o.isMesh||!NICHE_CATS.includes(o.userData?.category)||!o.material?.userData?.pooledTile)continue;
   const r=planeBox(o.geometry);if(!r)continue;
   const rect=rectFor(o,r,gx);if(!rect)continue;
   const cut=cutRect(o.geometry,rect);
   if(cut&&cut.inside>1e-4)hosts.push({mesh:o,orig:o.geometry,holed:cut.geometry});
  }
  if(!hosts.some(h=>h.mesh===host))return fail();
  return {group,hosts,host,gx,cy,D,bottom,wallMesh,W,H};
 }
 function buildNiche(){
  nicheState=null;
  if(state.mode!=='full')return;
  const products=productList(),wallP=productFor('wall');if(!wallP)return;
  const nicheP=products.find(p=>/niche/i.test(p.surface))||wallP,index=products.indexOf(nicheP);
  const walls=nicheWalls();if(!walls.length)return;
  const cfg=nicheOf(),first=((cfg.wall%walls.length)+walls.length)%walls.length;
  // the chosen wall first; if it cannot take a full-depth recess, the next one
  let made=null,pick=null;
  for(const minDepth of [NICHE.d/12-1e-6,2/12]){
   for(let k=0;k<walls.length&&!made;k++){pick=walls[(first+k)%walls.length];made=nicheOn(pick,cfg,minDepth);}
   if(made)break;
  }
  if(!made){runtimeErrors.push('NICHE: no tiled wall in '+state.room+' can take the niche');return;}
  const {group,hosts,host,gx:cx,cy,D,bottom,wallMesh,W,H}=made;
  const note={owner_niche:true,native_host_face_id:host.userData.native_host_face_id||null,
   source:'Owner direction 2026-11-09: niche with niche tile on back, sides and top and a stone sill. Size and position are placeholders, not from the Revit model or the plans. Display only.'};
  const face=(w,h,position,rotation,role)=>{
   const m=addPlane(w,h,[0,0,0],[0,0,0],tileMaterial(nicheP,w,h,'wall'),'OWNER_NICHE',index,{...note,niche_role:role});
   group.add(m);m.position.set(...position);m.rotation.set(...rotation);return m;
  };
  const t=NICHE.sill/12,ov=NICHE.overhang/12;
  face(W,H,[cx,cy,-D],[0,0,0],'back');
  face(D,H,[cx-W/2,cy,-D/2],[0,Math.PI/2,0],'side');
  face(D,H,[cx+W/2,cy,-D/2],[0,-Math.PI/2,0],'side');
  face(W,D,[cx,cy+H/2,-D/2],[Math.PI/2,0,0],'top');
  const sill=new THREE.Mesh(new THREE.BoxGeometry(W,t,D+ov),new THREE.MeshStandardMaterial({color:0xe9e5dd,roughness:.32,metalness:0}));
  sill.position.set(cx,cy-H/2+t/2,(ov-D)/2);
  sill.userData={category:'OWNER_NICHE_SILL',surfaceIndex:-1,...note,sill_thickness_in:NICHE.sill,sill_overhang_in:NICHE.overhang,
   sill_material:'Stone, not yet specified (shown neutral)'};
  group.add(sill);
  // clip box (world space) that cuts the native wall back to the recess
  group.updateMatrixWorld(true);
  const planes=[[1,0,0,cx+W/2,cy,0],[-1,0,0,cx-W/2,cy,0],[0,1,0,cx,cy+H/2,0],[0,-1,0,cx,cy-H/2,0],[0,0,1,cx,cy,.06],[0,0,-1,cx,cy,-D]].map(([nx,ny,nz,px,py,pz])=>
   new THREE.Plane().setFromNormalAndCoplanarPoint(new THREE.Vector3(nx,ny,nz).transformDirection(group.matrixWorld),
    new THREE.Vector3(px,py,pz).applyMatrix4(group.matrixWorld)));
  nicheState={group,hosts,host,planes,wallMesh,walls:walls.length,wallIndex:walls.indexOf(pick),
   widthIn:+(W*12).toFixed(2),heightIn:NICHE.h,depthIn:+(D*12).toFixed(2),sillTopIn:+((bottom+t)*12).toFixed(2),
   offsetIn:0,product:nicheP.name,usesWallTile:nicheP===wallP,hostWall:note.native_host_face_id};
  applyNiche();
 }
 function applyNiche(){
  const n=nicheState;if(!n||!n.group.parent)return;
  const whole=o=>Math.abs(o.scale.y-1)<1e-3;
  for(const h of n.hosts)h.mesh.geometry=whole(h.mesh)?h.holed:h.orig;
  const active=state.walls&&n.hosts.some(h=>h.mesh.visible&&whole(h.mesh));
  n.group.visible=active;
  const m=n.wallMesh?.material;if(!m)return;
  const sectioned=(m.clippingPlanes||[]).length>0&&m.clippingPlanes!==n.planes;
  const box=active&&!sectioned;
  if(box){m.clippingPlanes=n.planes;m.clipIntersection=true;}
  else{m.clipIntersection=false;if(m.clippingPlanes===n.planes)m.clippingPlanes=[];}
  if(n.wallMesh.userData.mcNicheBox!==box){m.needsUpdate=true;n.wallMesh.userData.mcNicheBox=box;}
  for(const child of n.wallMesh.children)if(child.material){child.material.clippingPlanes=m.clippingPlanes;child.material.clipIntersection=m.clipIntersection;child.material.needsUpdate=true;}
 }

 // ---- cutaway crops tile instead of squashing it. The viewer shortens a
 // camera-facing tiled wall by scaling the mesh; without this the texture is
 // compressed with it (a 20 in tile drawn 6 in tall). Scale the texture repeat
 // by the same factor so each tile keeps its nominal size and the top is cut.
 const baseApplyInteriorReveal=applyInteriorReveal;
 // The same pass applies the reviewer's layout choices per room and per pick:
 // tile turned 90 degrees, and the pattern shifted (inches) to set where the
 // grout lines land. These are display aids kept in this browser only; they do
 // not edit the frozen picks.
 const TILE_MAPS=['map','normalMap','roughnessMap','bumpMap','aoMap','metalnessMap'];
 function keepTileScale(){
  for(const o of renderObjects){
   const m=o.material;if(!o.isMesh||!m?.userData?.pooledTile||!m.map)continue;
   const u=o.userData;
   if(u.mcBaseMap!==m.map){u.mcBaseMap=m.map;u.mcBase=[m.map.repeat.x,m.map.repeat.y,m.map.offset.x,m.map.offset.y];}
   const L=layoutOf(u.surfaceIndex),[tw,th]=m.userData.atlas?.units||[1,1];
   const bx=u.mcBase[0],by=u.mcBase[1]*o.scale.y,dx=L.dx/12,dy=L.dy/12;
   const rx=L.turn?by*th/tw:bx,ry=L.turn?bx*tw/th:by,rot=L.turn?Math.PI/2:0;
   const ox=u.mcBase[2]+(L.turn?-dy/tw:-dx/tw),oy=u.mcBase[3]+(L.turn?dx/th:-dy/th);
   for(const k of TILE_MAPS){const t=m[k];if(!t||!t.isTexture)continue;
    t.center.set(0,0);t.rotation=rot;t.repeat.set(rx,ry);t.offset.set(ox,oy);}
  }
 }
 // Some walls carry two coincident tile planes: a sectioned one and a
 // full-height "review" twin that the viewer only showed in the Wet wall
 // camera. Show the full-height twin whenever the camera is on the room side
 // of that wall, and the sectioned one when looking from behind it.
 function showFullHeightWhenFacing(){
  if(state.mode!=='full'||!state.walls||state.preset==='wet')return;
  const b=physicalBounds();if(!b||b.isEmpty())return;
  const center=b.getCenter(new THREE.Vector3());
  const twins=renderObjects.filter(o=>o.userData?.category==='ARCH_R059_FULL_HEIGHT_FINISH_REVIEW');
  for(const review of twins){
   const c=new THREE.Box3().setFromObject(review).getCenter(new THREE.Vector3());
   const inward=new THREE.Vector3(center.x-c.x,0,center.z-c.z).normalize();
   const facing=new THREE.Vector3(camera.position.x-c.x,0,camera.position.z-c.z).normalize().dot(inward)>.12;
   review.visible=facing;
   for(const o of renderObjects){
    if(o===review||o.userData?.category!=='FULL_ROOM_WET_WALL'||o.userData.native_host_face_id!==review.userData.native_host_face_id)continue;
    if(o.position.distanceToSquared(new THREE.Vector3(review.position.x,o.position.y,review.position.z))>.01)continue;
    if(facing)o.visible=false;
   }
  }
 }
 applyInteriorReveal=function(){const out=baseApplyInteriorReveal.apply(this,arguments);showFullHeightWhenFacing();sectionAddedReturns();applyNiche();keepTileScale();return out;};

 // ---- default 3D view looks AT the tiled walls. The stock isometric often
 // sat behind the wet wall, so the cutaway removed the very tile on review.
 const finishCats=new Set(['FULL_ROOM_WET_WALL','ARCH_R067_SOURCE_HOSTED_DRY_FINISH_PREVIEW']);
 function tileFacingDirection(){
  const b=physicalBounds();if(!b||b.isEmpty())return null;
  const center=b.getCenter(new THREE.Vector3()),sum=new THREE.Vector3();
  for(const o of renderObjects){
   if(!o.isMesh||!o.material?.userData?.pooledTile||!finishCats.has(o.userData?.category))continue;
   const g=o.geometry.parameters||{},area=(g.width||1)*(g.height||1);
   const c=new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3());
   const d=new THREE.Vector3(center.x-c.x,0,center.z-c.z);if(d.lengthSq()<1e-6)continue;
   sum.addScaledVector(d.normalize(),area);
  }
  return sum.lengthSq()>1e-6?sum.normalize():null;
 }
 function faceTiledWalls(){
  if(state.mode!=='full'||state.preset!=='isometric')return false;
  const dir=tileFacingDirection();if(!dir)return false;
  const offset=camera.position.clone().sub(orbit.target),dist=offset.length();
  const elevation=Math.asin(THREE.MathUtils.clamp(offset.y/dist,-1,1));
  const current=Math.atan2(offset.x,offset.z),base=Math.atan2(dir.x,dir.z);
  const delta=a=>Math.abs(Math.atan2(Math.sin(a-current),Math.cos(a-current)));
  const swing=THREE.MathUtils.degToRad(32);
  const azimuth=delta(base+swing)<=delta(base-swing)?base+swing:base-swing;
  const tilt=THREE.MathUtils.clamp(elevation,THREE.MathUtils.degToRad(28),THREE.MathUtils.degToRad(48));
  camera.position.copy(orbit.target).add(new THREE.Vector3(Math.sin(azimuth)*Math.cos(tilt),Math.sin(tilt),Math.cos(azimuth)*Math.cos(tilt)).multiplyScalar(dist));
  camera.up.set(0,1,0);orbit.update();
  frameCompletionCamera();applyInteriorReveal();
  return true;
 }
 const baseSetCamera=setCamera;
 setCamera=function(preset,force=true){
  const out=baseSetCamera.call(this,preset,false);
  try{faceTiledWalls();}catch(e){runtimeErrors.push('TILE CAMERA: '+e.message);}
  if(force)renderer.render(scene,camera);
  return out;
 };

 // ---- every frozen pick says whether it is actually drawn, and where
 function pickStatus(audit){
  const live=audit.surfaces.filter(s=>s.category!=='ARCH_R059_FULL_HEIGHT_FINISH_REVIEW');
  return audit.products.map((p,i)=>{
   const mine=live.filter(s=>s.surfaceIndex===i&&s.category!=='OWNER_NICHE');
   const inNiche=live.filter(s=>s.surfaceIndex===i&&s.category==='OWNER_NICHE');
   if(inNiche.length&&!mine.length){
    const f=inNiche[0];
    return {drawn:true,niche:true,walls:1,turned:f.turned,nominalIn:f.nominalIn,
     text:'Drawn in the niche (back, sides, top) at '+(f.turned?[...f.nominalIn].reverse():f.nominalIn).join('×')+' in'+(f.turned?', turned 90°':'')};
   }
   if(mine.length){
    const walls=mine.filter(s=>!s.horizontal).length;
    const size=(mine[0].turned?[...mine[0].nominalIn].reverse():mine[0].nominalIn).join('×')+' in'+(mine[0].turned?', turned 90°':'');
    return {drawn:true,walls,turned:mine[0].turned,nominalIn:mine[0].nominalIn,text:(walls?'Drawn on '+walls+' wall face'+(walls>1?'s':''):'Drawn on the floor')+' at '+size};
   }
   if(audit.mode==='context')return {drawn:false,text:'Tile finishes are not drawn in Native room mode'};
   if(/niche/i.test(p.surface))return {drawn:false,text:'Not drawn: niche size and position are not in the model'};
   if(/conditional/i.test(p.surface))return {drawn:false,text:'Not drawn separately: applies only if the walk-in option is chosen'};
   if(/wall/i.test(p.surface))return {drawn:false,text:audit.mode==='full'?'Not drawn: the model has no tub or shower to locate this wall':'Not drawn in this view'};
   return {drawn:false,text:'Not drawn in this view'};
  });
 }
 // layout controls under each drawn pick: turn the tile, and slide the
 // pattern to choose where grout lines and cuts land
 const trimIn=v=>String(+v.toFixed(2));
 function layoutControls(index,st){
  const L=layoutOf(index),nom=st.nominalIn||[12,12];
  const across=L.turn?nom[1]:nom[0],up=L.turn?nom[0]:nom[1];
  const box=el('div','mc-layout');
  const head=el('div','mc-layout-row');
  head.append(el('span','mc-layout-label','Layout'),el('span','mc-layout-value',trimIn(across)+' across × '+trimIn(up)+(st.walls?' up':' deep')+' in'));
  const turn=el('button','mc-layout-btn'+(L.turn?' on':''),'Turn 90°');turn.type='button';
  turn.title='Run this tile the other way in this room';
  head.append(turn);
  const move=el('div','mc-layout-row');
  move.append(el('span','mc-layout-label','Shift'));
  const change=next=>{setLayout(index,next);keepTileScale();renderer.render(scene,camera);annotatePicks();};
  turn.onclick=()=>change({...L,turn:L.turn?0:1,dx:0,dy:0});
  const wrap=(v,size)=>{const r=((v%size)+size)%size;return +r.toFixed(3);};
  for(const [glyph,ax,sign,name] of [['←','dx',-1,'left'],['→','dx',1,'right'],['↑','dy',1,'up'],['↓','dy',-1,'down']]){
   const b=el('button','mc-layout-btn mc-layout-arrow',glyph);b.type='button';
   b.title='Move the pattern '+name+' 1 in (Shift-click: half a tile)';b.setAttribute('aria-label','Move pattern '+name);
   b.onclick=e=>{const size=ax==='dx'?across:up,step=e.shiftKey?size/2:1;change({...L,[ax]:wrap(L[ax]+sign*step,size)});};
   move.append(b);
  }
  move.append(el('span','mc-layout-value',(L.dx||L.dy)?trimIn(L.dx)+' in right, '+trimIn(L.dy)+' in up':'none'));
  if(L.turn||L.dx||L.dy){const reset=el('button','mc-layout-btn','Reset');reset.type='button';reset.onclick=()=>change({turn:0,dx:0,dy:0});move.append(reset);}
  box.append(head,move);
  return box;
 }
 function nicheControls(){
  const n=nicheState,cfg=nicheOf(),box=el('div','mc-layout');
  const head=el('div','mc-layout-row');
  head.append(el('span','mc-layout-label','Niche'),el('span','mc-layout-value',trimIn(n.widthIn)+' long × '+n.heightIn+' high × '+trimIn(n.depthIn)+' in deep'));
  const change=next=>{setNiche(next);rebuild();applyInteriorReveal();renderer.render(scene,camera);};
  if(n.walls>1){const b=el('button','mc-layout-btn','Next wall');b.type='button';b.title='Move the niche to the next tiled wall';
   b.onclick=()=>change({wall:(n.wallIndex+1)%n.walls});head.append(b);}
  box.append(head,el('div','mc-layout-note','Runs the full length of this wall, bottom 4 ft above the floor, 1 ft 6 in tall. Wall and depth are placeholders; 3/4 in stone sill with 3/4 in overhang, stone not yet chosen.'));
  return box;
 }
 function annotatePicks(){
  document.querySelectorAll('#surfaces .mc-layout').forEach(n=>n.remove());
  const cards=[...document.querySelectorAll('#surfaces .surface')];if(!cards.length)return;
  let status;try{status=pickStatus(auditTiles());}catch(e){runtimeErrors.push('PICK STATUS: '+e.message);return;}
  cards.forEach((card,i)=>{
   card.querySelector('.mc-pick-status')?.remove();
   const st=status[i];if(!st)return;
   const line=el('div','mc-pick-status'+(st.drawn?' drawn':''),st.text);
   (card.querySelector('.surface-row>div')||card).append(line);
   if(st.drawn)card.after(layoutControls(i,st));
   const sub=card.querySelector('.surface-sub');
   if(st.niche&&sub)sub.textContent=sub.textContent.replace(' · location unknown',' · placeholder position');
   if(st.niche&&nicheState)card.after(nicheControls());
  });
 }
 // the stock caption says no niche is drawn; that is no longer true
 const baseSelectMaterial=selectMaterial;
 selectMaterial=function(index){
  const out=baseSelectMaterial.apply(this,arguments);
  try{
   const node=document.getElementById('material-info');
   if(node&&nicheState)for(const d of node.querySelectorAll('div'))if(/no niche mesh or cutout fabricated/i.test(d.textContent))
    d.textContent='Niche by owner direction: full length of its wall, bottom at 4 ft, 1 ft 6 in tall. Which wall and the depth are placeholders; not from the Revit model or the plans.';
  }catch(e){runtimeErrors.push('NICHE CAPTION: '+e.message);}
  return out;
 };
 const baseUpdateMaterials=updateMaterials;
 updateMaterials=function(){const out=baseUpdateMaterials.apply(this,arguments);annotatePicks();return out;};

 // ---- whole-building tile audit (open the viewer with ?audit=1)
 async function auditAll(){
  const keep={room:state.room,instance:state.instance};
  const rows=[];
  for(const room of ROOMS.filter(r=>r.products?.length))for(let i=0;i<room.physical_instances.length;i++){
   selectRoom(room.id);if(i){state.instance=i;updateInstanceSelect();rebuild();}
   await new Promise(r=>setTimeout(r,450));
   const a=auditTiles(),status=pickStatus(a);
   const live=a.surfaces.filter(s=>s.category!=='ARCH_R059_FULL_HEIGHT_FINISH_REVIEW');
   const problems=[];
   for(const s of live){
    const tag=s.category+' ['+s.normal.join(',')+']';
    if(s.materialProduct!==s.recordProduct)problems.push(tag+': draws '+s.materialProduct+' but the record says '+s.recordProduct);
    if(s.texture==='vendor photo blend')problems.push(tag+': still uses the vendor photo, no generated tile texture for '+s.recordProduct);
    const wallPick=/wall/i.test(s.recordSurface||'');
    if(s.category!=='OWNER_NICHE'&&wallPick===s.horizontal)problems.push(tag+': '+(s.horizontal?'wall pick on a horizontal surface':'floor pick on a vertical surface'));
    const nominal=s.turned?[...s.nominalIn].reverse():s.nominalIn;
    if(!s.drawnIn||s.drawnIn.some((v,k)=>Math.abs(v-nominal[k])/nominal[k]>.02))
     problems.push(tag+': drawn '+(s.drawnIn||[]).join('×')+' in, nominal '+nominal.join('×')+' in');
    if(!s.horizontal&&a.native&&!s.hostWall&&s.category!=='OWNER_NICHE')problems.push(tag+': not hosted on a native wall');
   }
   rows.push({key:a.room+' / '+a.instance,surfaces:live.length,
    picks:a.products.map((p,k)=>({surface:p.surface,name:cleanName(p),...status[k]})),problems,holds:(a.holds||[]).length});
  }
  selectRoom(keep.room);if(keep.instance){state.instance=keep.instance;updateInstanceSelect();rebuild();}
  return {rows,surfaces:rows.reduce((n,r)=>n+r.surfaces,0),problems:rows.reduce((n,r)=>n+r.problems.length,0),
   undrawn:rows.reduce((n,r)=>n+r.picks.filter(p=>!p.drawn).length,0)};
 }
 async function openAudit(){
  toast('Auditing every tiled room…');
  const result=await auditAll();
  const body=el('div');
  const metrics=el('div','mc-metrics');
  for(const [n,l] of [[result.rows.length,'Rooms checked'],[result.surfaces,'Tiled surfaces measured'],[result.problems,'Mismatches'],[result.undrawn,'Picks not drawn']]){
   const d=el('div');d.append(el('strong',null,String(n)),el('span',null,l));metrics.append(d);}
  body.append(metrics);
  const sec=el('section','mc-section');
  sec.append(el('h3',null,'Result by room'),el('p',null,'Each tiled surface in the 3D scene is checked against the frozen record: the product on it, whether it is a wall or a floor, the tile size actually drawn, and that wall tile sits on a native Revit wall face. A pick that is not drawn is listed with the reason.'));
  const wrap=el('div','mc-table-wrap'),table=el('table','mc-table');
  table.innerHTML='<thead><tr><th>Room</th><th class="num">Surfaces</th><th>Pick</th><th>Product</th><th>In the 3D view</th></tr></thead>';
  const tb=el('tbody');
  for(const r of result.rows){
   r.picks.forEach((p,k)=>{const tr=el('tr');
    const td=el('td','room');if(!k)td.append(el('b',null,r.key));
    const cell=el('td');cell.append(el('span','mc-tag '+(p.drawn?'ok':'none'),p.drawn?'Drawn':'Not drawn'),document.createTextNode(' '+p.text));
    tr.append(td,el('td','num',k?'':String(r.surfaces)),el('td',null,p.surface),el('td',null,p.name),cell);tb.append(tr);});
   for(const problem of r.problems){const tr=el('tr');const td=el('td',null,problem);td.colSpan=4;td.style.color='var(--danger)';
    tr.append(el('td'),td);tb.append(tr);}
  }
  table.append(tb);wrap.append(table);sec.append(wrap);body.append(sec);
  showModal({kicker:'Measured from the live 3D scene',title:result.problems?result.problems+' tile mismatch'+(result.problems>1?'es':''):'Tile audit: no mismatches',body});
  document.body.dataset.tileAudit=result.problems?'FAIL':'PASS';
  return result;
 }

 // ---- first paint on-system
 updateRoomList();syncHeading();
 // the first room was built before this layer loaded: bring it on-system too
 try{if(state.mode==='full'){rebuild();setCamera(state.preset);}annotatePicks();}catch(e){runtimeErrors.push('FIRST VIEW: '+e.message);}
 Object.assign(window.__viewerDebug,{collagerTheme:{version:'2026-11-09',pendingSubstitution:PENDING_SUBSTITUTION,
  nicheDebug:()=>({walls:renderObjects.filter(o=>o.isMesh&&/WET_WALL|R059/.test(o.userData?.category||'')&&o.material?.userData?.pooledTile).map(o=>{
    const p=o.geometry.attributes.position,b=new THREE.Box3().setFromBufferAttribute(p);
    return {cat:o.userData.category,type:o.geometry.type,count:p.count,size:b.getSize(new THREE.Vector3()).toArray().map(v=>+v.toFixed(3)),
     zmin:+b.min.z.toFixed(4),scaleY:+o.scale.y.toFixed(3),pos:o.position.toArray().map(v=>+v.toFixed(3)),ry:+o.rotation.y.toFixed(3),rot:[+o.rotation.x.toFixed(3),+o.rotation.z.toFixed(3)],vis:o.visible,host:o.userData.native_host_face_id||null};}),
   native:nativeRendered.filter(m=>m.parent&&m.userData.source_category==='Walls').map(m=>{const b=new THREE.Box3().setFromObject(m);return {id:m.userData.revit_id,min:b.min.toArray().map(v=>+v.toFixed(2)),max:b.max.toArray().map(v=>+v.toFixed(2))};})}),
  openBoard,openHelp,saveView,scheduleTSV,auditTiles,auditAll,openAudit,selectInstance:(id,i)=>{selectRoom(id);if(i){state.instance=i;updateInstanceSelect();rebuild();}},rooms:()=>ROOMS.map(r=>({id:r.id,numbers:r.numbers,area:areaText(r),picks:(r.products||[]).length}))}});
 const veil=$('mc-loading');
 const reveal=()=>{veil?.classList.add('done');setTimeout(()=>veil?.remove(),450);};
 (document.fonts?.ready||Promise.resolve()).then(reveal,reveal);
 if(new URLSearchParams(location.search).has('audit'))setTimeout(()=>openAudit().catch(e=>runtimeErrors.push('AUDIT: '+e.message)),900);
}
