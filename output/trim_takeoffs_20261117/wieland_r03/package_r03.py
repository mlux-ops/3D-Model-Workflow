
from pathlib import Path
import csv,collections,math,sys,zipfile,json
r=Path('output/trim_takeoffs_20261117/wieland_r03');r2=r.parent/'wieland_r02'
data=lambda p:list(csv.DictReader((r/p).open(encoding='utf-8-sig')))
reg=data('01_room_scope_register.csv');room=data('02_room_takeoff.csv');edges=data('03_wall_face_runs.csv');obs=data('04_openings.csv')
focused=sorted([a for a in room if 'BED' in a['name']or 'LIVING' in a['name']],key=lambda a:a['room'])
def disp(s):return f'{float(s):.2f}' if s not in ['',None] else 'HOLD'
if sys.argv[1]=='pdf':
 import fitz
 d=fitz.open()
 for pos,row in enumerate(focused):
  key=row['room'];p=d.new_page(width=612,height=576)
  def txt(x,y,s,size=10,color=(.12,.17,.18),bold=False):
   p.insert_text((x,y),str(s),fontname='hebo' if bold else 'helv',fontsize=size,color=color)
  p.draw_rect((0,0,612,70),color=None,fill=(.075,.17,.19))
  txt(28,24,'1529 N WIELAND  /  FINISH CARPENTRY  /  R03',9,(.65,.89,.86),True)
  txt(28,51,f"{key}    {row['name']}",20,(1,1,1),True);txt(425,50,row['level'],11,(1,1,1))
  rr=[e for e in edges if e['room']==key];oo=[a for a in obs if a['room']==key]
  x=[float(e[k]) for e in rr for k in ['x_start_ft','x_end_ft']];y=[float(e[k]) for e in rr for k in ['y_start_ft','y_end_ft']]
  f=min(455/max(max(x)-min(x),1),243/max(max(y)-min(y),1));xc=(max(x)+min(x))/2;yc=(max(y)+min(y))/2
  XY=lambda x,y:(306+(x-xc)*f,225-(y-yc)*f)
  for e in rr:
   a,b,c,h=[float(e[k])for k in ['x_start_ft','y_start_ft','x_end_ft','y_end_ft']]
   p.draw_line(XY(a,b),XY(c,h),color=(.12,.42,.42) if e['wall_backed']=='True' else (.71,.71,.71),width=2.5)
   for o in oo:
    if o['edge']!=e['edge']:continue
    l,u=[float(o[k])for k in ['axis_start_ft','axis_end_ft']]
    pt1,pt2=(XY(l,b),XY(u,b)) if e['wall_axis']=='EW' else (XY(a,l),XY(a,u))
    p.draw_line(pt1,pt2,color=(.9,.49,.13) if o['kind']=='Door' else (.23,.48,.81),width=4.4)
   if float(e['face_LF'])>1.5:
    px,py=XY((a+c)/2,(b+h)/2);dx,dy=px-306,py-225;norm=max(1,math.hypot(dx,dy))
    txt(px+8*dx/norm-4,py+8*dy/norm+2,e['edge'],7)
  txt(28,386,'DIRECT WALL FACE',8,(.12,.42,.42),True);txt(146,386,'DOOR ENVELOPE',8,(.72,.33,.02),True);txt(265,386,'WINDOW ENVELOPE',8,(.23,.48,.81),True);txt(407,386,'UNRESOLVED / OPEN LINE',8,(.45,.45,.45),True)
  p.draw_line((28,399),(584,399),color=(.78,.83,.82),width=.7)
  for i,(label,value) in enumerate([('GROSS ROOM LF',row['gross_room_LF']),('8-IN BASE CLEAR LF',row['base_clear_face_candidate_LF']),('3-IN CROWN CLEAR LF',row['crown_clear_face_candidate_LF'])]):
   x0=28+i*193;txt(x0,421,label,8,(.23,.33,.32),True);txt(x0,445,disp(value),21,(.09,.20,.20),True)
  txt(28,477,'Geometry scenario, not fabrication cuts. Opening colors show full family envelopes, not jamb cut widths.',9)
  txt(28,493,'Base/crown clear LF omit conflicting envelopes and unsupported faces. Ceiling/finish conditions need review.',9)
  txt(28,509,'See workbook for casework, individual returns, ceiling IDs and separate opening/casing dimensions.',9)
  txt(28,546,'PRIVATE DRAFT  /  NO WASTE OR ORDER QUANTITY  /  NOT TO SCALE',8,(.3,.38,.37),True);txt(555,546,f'{pos+1}/{len(focused)}',8)
 d.save(r/'1529_Wieland_Focus_Wall_Map_R03.pdf',garbage=4,deflate=True)
 assert d.page_count==15
elif sys.argv[1]=='book':
 from openpyxl import Workbook,load_workbook
 from openpyxl.styles import Font,PatternFill,Alignment
 from openpyxl.utils import get_column_letter
 w=Workbook();w.remove(w.active)
 def tab(title,subtitle,records,fieldlist=None,widths=None):
  s=w.create_sheet(title);cols=fieldlist or list(records[0]);widths=widths or [max(14,min(36,len(c)+4))for c in cols]
  s.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(cols));s.cell(1,1,title.upper()).fill=PatternFill('solid',fgColor='173E40');s.cell(1,1).font=Font(bold=True,size=14,color='FFFFFF');s.row_dimensions[1].height=31
  s.merge_cells(start_row=2,start_column=1,end_row=2,end_column=len(cols));s.cell(2,1,subtitle).font=Font(italic=True,color='40605E',size=10);s.cell(2,1).alignment=Alignment(wrap_text=True,vertical='center');s.row_dimensions[2].height=36
  for i,k in enumerate(cols,1):
   c=s.cell(4,i,k.replace('_',' '));c.fill=PatternFill('solid',fgColor='257270');c.font=Font(bold=True,color='FFFFFF',size=10);c.alignment=Alignment(wrap_text=True,vertical='center');s.column_dimensions[get_column_letter(i)].width=widths[i-1]
  s.row_dimensions[4].height=34
  for j,row in enumerate(records,5):
   for i,k in enumerate(cols,1):
    value=row.get(k)
    if value not in ('',None) and 'chain' not in k and (k.lower().endswith(('_lf','_ft','_sf','fraction')) or k in ('face_LF','room area SF','Rooms','Faces')):value=float(value)
    if value=='':value=None
    cell=s.cell(j,i,value);cell.font=Font(size=10,color='243835');cell.alignment=Alignment(vertical='top',wrap_text=title in ('Read first','Evidence','Decision holds'))
    if isinstance(value,float):cell.number_format='#,##0.00;[Red](#,##0.00);0.00'
    if (j-5)%2==1:cell.fill=PatternFill('solid',fgColor='F1F6F5')
   if title in ('Read first','Evidence','Decision holds'):s.row_dimensions[j].height=44
  s.freeze_panes='B5';s.sheet_view.showGridLines=False;s.auto_filter.ref=f'A4:{get_column_letter(len(cols))}{4+len(records)}';return s
 notes=[
 ('Current direction','8-inch baseboard and 3-inch crown at both jobs, per Max on November 17. No assumption about thickness, projection, stock length or specialty profiles. This workbook contains Wieland only.'),
 ('What R03 adds','71 area/perimeter-matched current model outlines (421 faces) of 101 positive-area indexed rooms. Includes 14 of 15 indexed bedrooms and 1 of 3 living/dining rooms. Results by Revit instance; repeated room marks are not merged.'),
 ('How to use','Start with Bedroom + living. Use Room review to check entries outside feature rooms and Face by face for an auditable opening-by-opening estimate. Marked diagrams accompany all 15 focus lines; R02 retains issued-plan scale check.'),
 ('Clear-face scenario','Base or crown left along wall-backed faces after subtracting the union of modeled full-family door/window/casework envelopes intersecting each vertical band. This is a stated option, not an installed cut length. A jamb, sill notch or return may change it.'),
 ('Blank or zero','Blank crown when there is no verified ceiling candidate; zero is never substituted for a missing room. A displayed 0.00 may indicate no eligible supported face for the stated model scenario, not no finish scope.'),
 ('What is not included','Decorative molding remains separate: no located Wieland elevation confirms frame count, rail layout and cut dimensions. No Belmont design copied here. No casing, stock optimization, waste, short returns or purchases included.'),
 ('Scope','Site-wide register includes stairs/lobbies, baths, closets, kitchen, garage and exterior entries where indexed. A room entry is evidence of a boundary, not an instruction to install wood trim there. Do not sum all room scenarios as a quote or order.'),
 ('Status','Draft for private quantity review. No Revit changes, sync or correspondence. R02 retained; this supersedes R02 only where this workbook provides a newer measurement or approval.')]
 tab('Read first','1529 N WIELAND ST  |  JOB 25-006  |  REVISION R03  |  17 NOV 2026',[{'Item':a,'Basis and use':b}for a,b in notes],widths=[25,115])
 cols=['room','name','level','gross_room_LF','base_clear_face_candidate_LF','crown_clear_face_candidate_LF','wall_face_verification_hold_LF','door_envelope_LF','low_window_envelope_LF','base_cabinet_envelopes_LF','crown_window_envelope_LF','ceiling_id','indexed_room_id','order_QTY']
 tab('Bedroom + living','Conditional clear runs only. Opening widths are full modeled envelopes, not verified field trim stops. Blank = hold. Room 004A plus living/dining 104A, 403A not solved; see inventory.',focused,cols)
 tab('Room review','71 matched outlines, sorted by level and room. Rows outside confirmed finish locations are geometry scenarios only. Do not sum as a project order.',sorted(room,key=lambda a:(a['level'],a['room'])),cols)
 tab('Face by face','421 current-metric-matched faces. Door/window and casework columns can overlap; clear LF subtracts the interval UNION only once. Wall backed means at least 96.5% axis overlap with a current physical wall face. Endpoints are Revit internal feet.',edges)
 tab('Openings','A single family may touch two faces or rooms. Do not sum these as purchased doors/windows. Use clipped face overlap for the individual room face only; blank window type data means no separate parameter receipt for that element.',obs)
 tab('Site inventory','101 indexed live rooms. The 30 unmatched outlines are holds, not assumed similar units. This historical-ID index may omit newly placed rooms; see R02 for unplaced or unavailable IDs.',reg)
 src=[('Identity / scope','25-006 1527 N Wieland.rvt, Autodesk Docs; project address verified as 1529 N Wieland. November 17 open native model, New Construction / Main Model room receipts. No trim sweeps recorded.'),('Live entities','Read-only Revit receipts: 362 current walls, 71 room-separation lines, 62 windows, 127 doors, 72 ceilings, 337 casework inclusions. Window-family patio doors are retained in the opening schedule.'),('Location / validation','September 23 IFC provided historical IDs and candidate topology only. Current walls and separators reconstruct changed rooms. Accept only when current area and perimeter agree (within 0.001 SF and 0.001 LF). Wall IDs and coordinates are shown; diagonal/enclosed/void or unmatched cases held.'),('Openings / ceiling','Uses absolute vertical range of family bounds versus floor + 8in and ceiling - 3in, not room perimeter percentages. Ceiling candidate is smallest bounding rectangle covering centroid and >96% room area, NOT proof of a uniform ceiling at soffits.'),('Drawing crosscheck','A2.1/A2.2 floor plans PDF, Nov 11 digital file; titleblock Aug 7 IFC, Aug 12 zoning revision and Oct 26 basement revision. 3/16in = 1ft crosschecked: 7ft10in is 105.745 points vs 105.750 expected. R02 annotated measured faces are NOT added to R03.'),('Drawing link','https://drive.google.com/file/d/1ejfrqS6XLgML_ZEvZrcfo7cSnRL4WwD7/view')]
 tab('Evidence','Source references, revision and measurement rules.',[{'Source':a,'What was verified':b}for a,b in src],widths=[28,112])
 holds=[('Scope and finish rooms','Project-wide base/crown requested. Exclude or include individual wet, tiled, casework, garage, balcony and stair configurations only after issued finish/casing scope is verified.'),('Window returns','Third-floor rooms 308A/B, 309A/B: F-1 4in sill and 9ft head; GWB underside ~9ft 1 7/8in. Both trim bands conflict. Confirm course at opening: wrap, notch, stop at casing, or continuous chair/rail, with returns if required.'),('Closet detail','Third-floor slider family: 46in nominal, 47.25in overall model envelope, trim width zero. Do not adopt family envelope as installed casing edge without detail. Hard casing quantities intentionally excluded.'),('Reference gaps','Historically indexed 104B, 301A and 301B show zero-area/unplaced; 005A did not resolve. Do not assume mirrored geometries for these or the 30 nonreconciled rooms.'),('Wieland feature moldings','Require approved target walls and an issued dimensioned elevation/spacing rule for bedroom, living and dining treatments. Unit selection or a precedent elevation from a different job is not quantity authorization.'),('Release gate','Confirm modeled openings vs actual return/casing limits, ceiling transitions, cabinets, wet-area/exterior scope, profile and waste/order strategy. Net cuts, waste and purchasing quantities intentionally unissued.')]
 tab('Decision holds','Information that changes quantities. These are private review flags, not issued RFIs.',[{'Issue':a,'Why it matters / next check':b}for a,b in holds],widths=[30,111])
 f=r/'1529_Wieland_Trim_Takeoff_R03.xlsx';w.save(f);v=load_workbook(f,read_only=True,data_only=True);assert len(v.sheetnames)==8 and v['Face by face'].max_row==425 and v['Room review'].max_row==75 and v['Bedroom + living'].max_row==19;print(f,len(v.sheetnames),f.stat().st_size)
elif sys.argv[1]=='zip':
 read='1529 Wieland R03. Start with 1529_Wieland_Trim_Takeoff_R03.xlsx and 1529_Wieland_Focus_Wall_Map_R03.pdf. Private review only, not for purchasing. Rev R02 archived separately; includes source traces from the November 11 drawing. The 421 rows are room faces, not individual pieces of stock. See workbook Evidence and Decision holds for reconciliation scope.'
 (r/'START_HERE.txt').write_text(read)
 f=r.parent/'1529_Wieland_Trim_Takeoff_R03_2026-11-17.zip'
 with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(r.iterdir()):
   if p.is_file():z.write(p,('' if p.suffix in ['.xlsx','.pdf','.txt']else 'R03_evidence/')+p.name)
  for p in sorted(r2.iterdir()):
   if (p.suffix in ('.csv','.json') and (p.name.startswith(('room_','door_')) or p.name in ('ifc_room_index.json','current_doors.json','verified_final_context.json'))) or p.name.endswith('_R02.pdf'):z.write(p,'R02_retained/'+p.name)
  bb=r.parent
  for n in ['wieland_casework.json','wieland_levels.json','wieland_sweeps.json','wieland_phases.json']:z.write(bb/n,'source_evidence/'+n)
 with zipfile.ZipFile(f)as z:assert z.testzip()is None;print(f,f.stat().st_size,len(z.namelist()))


