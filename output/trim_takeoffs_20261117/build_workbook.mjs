
import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const data=JSON.parse(await fs.readFile('workbook_data.json','utf8'));
const w=Workbook.create();
const names=['651 Review','1529 Scope','651 Elements','651 Feature Scope','Sources and Method'];
for(const n of names)w.worksheets.add(n);
const by=n=>w.worksheets.getItem(n);
const navy='#193549',amber='#FFF1D2',gray='#F1F4F6';
function base(s,lastCol,lastRow,widths){
 s.showGridLines=false;
 const r=s.getRange('A1:'+lastCol+lastRow);r.format.font={name:'Arial',size:11,color:'#22313B'};r.format.rowHeight=24;r.format.verticalAlignment='center';
 widths.forEach((v,i)=>s.getRangeByIndexes(0,i,lastRow,1).format.columnWidth=v);
}
function row(s,n,vals){s.getRangeByIndexes(n-1,0,1,vals.length).values=[vals];}
function head(s,n,vals){row(s,n,vals);const r=s.getRangeByIndexes(n-1,0,1,vals.length);r.format.fill=navy;r.format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};r.format.wrapText=true;r.format.rowHeight=36;}
function title(s,t){row(s,2,[t]);s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};s.getRange('A2').format.rowHeight=30;}
let s=by('651 Review');base(s,'F',39,[29,18,21,20,21,25]);title(s,'651 Belmont | Trim takeoff review');
row(s,4,['DRAFT: NOT ORDER-READY']);s.getRange('A4:F4').format.fill=amber;
row(s,5,['Live model snapshot: November 17, 2026. No model edits, save or synchronization.']);
head(s,7,['Scope','Elements','Revit Length (LF)','Verified net (LF)','Waste (LF)','Purchase quantity']);
row(s,8,['Baseboard',null,null,'NOT VERIFIED','NOT SET','HOLD']);
row(s,9,['Crown',null,null,'NOT VERIFIED','NOT SET','HOLD']);
for(const r of [8,9]){
 s.getRange('B'+r).formulas=[[`=COUNTIF('651 Elements'!$B$5:$B$426,A${r})`]];
 s.getRange('C'+r).formulas=[[`=SUMIF('651 Elements'!$B$5:$B$426,A${r},'651 Elements'!$F$5:$F$426)`]];
}
s.getRange('C8:C9').setNumberFormat('#,##0.00');
row(s,11,['Lengths above are native scheduled values, not verified installed or purchasing lengths.']);
row(s,12,['Feature-wall trim and four Casework crown continuations are NOT included above.']);
head(s,14,['Provisional Z band','Baseboard LF','Crown LF','Assignment basis']);
for(let i=0;i<data.bands.length;i++){
 let r=15+i;row(s,r,[data.bands[i][0],null,null,'Element minimum Z']);
 s.getRange('B'+r).formulas=[[`=SUMIFS('651 Elements'!$F$5:$F$426,'651 Elements'!$B$5:$B$426,"Baseboard",'651 Elements'!$D$5:$D$426,A${r})`]];
 s.getRange('C'+r).formulas=[[`=SUMIFS('651 Elements'!$F$5:$F$426,'651 Elements'!$B$5:$B$426,"Crown",'651 Elements'!$D$5:$D$426,A${r})`]];
}
s.getRange('B15:C20').setNumberFormat('#,##0.00');
row(s,22,['Z bands are provisional locations, NOT verified room/floor allocations.']);
row(s,23,['Native levels include GRADE and FOUNDATION on trim physically above those levels.']);
row(s,25,['RELEASE GATES']);s.getRange('A25:F25').format.fill=gray;s.getRange('A25').format.font.bold=true;
const issues=[
'1. Reconcile model 8-inch baseboard against 5-inch callouts on A2.4 and A2.5.',
'2. Profile thickness is 5/8 inch raw; coarse Revit display rounds it to 3/4 inch.',
'3. Deduct openings/voids, verify returns, joins and overlaps at actual cut geometry.',
'4. Measure feature-wall molding separately from slat panels and base/crown.',
'5. Allocate segments to actual rooms/units and verify latest approved design.',
'6. Set waste, stock lengths and cut optimization only after net measurement.',
'All 422 records: New Construction; Phase Demolished=None; Main Model.',
'All stored revision Issued flags are false. Approved document status is unverified.'
];
issues.forEach((t,i)=>row(s,26+i,[t]));
s.tabColor=navy;

s=by('1529 Scope');base(s,'D',26,[29,44,65,20]);title(s,'1529 Wieland | Scope and measurement hold');
row(s,4,['DRAFT: QUANTITIES UNDETERMINED']);s.getRange('A4:D4').format.fill=amber;
head(s,6,['Scope','Verified observation','Required next step','Net / order']);
const hold=[
['Project identity','Live file is named 25-006 1527 N Wieland.','Project Information verifies 1529 N Wieland St., job 25-006.','Confirmed alias'],
['Baseboard','No separate WallSweep instances or baseboard-named types returned.','Verify room finish schedule and embedded/nested geometry; absence is not zero scope.','HOLD'],
['Crown molding','No crown-named types or separate WallSweep instances returned.','Confirm specified profile, coverage by room, and whether trim is modeled or drawing-only.','HOLD'],
['Bedroom feature walls','No verified measurable trim package located in completed queries.','Resolve exact wall elevations/revisions and distinguish slat panels from molding.','HOLD'],
['Dining / living features','Casework exists, but trim identity and linear scope are unverified.','Trace approved elevations to native families or dimensioned drawings.','HOLD'],
['Model coverage','Generic Model inventory fails on unsupported LocationPoint.Rotation.','Use a repaired/supported read-only detailed inspector; do not substitute zero.','INCOMPLETE'],
['Units / phase / options','Bridge coordinates are internal feet; full trim set is not resolved.','Verify all candidate elements, phases, options and duplicates before totaling.','HOLD'],
['Waste / purchasing','No verified net quantity or stock-length schedule.','Keep waste and purchase quantities unset, not 0.','HOLD']
];
hold.forEach((r,i)=>row(s,7+i,r));s.getRange('A7:D14').format.wrapText=true;s.getRange('A7:D14').format.rowHeight=66;
row(s,17,['Latest stored revision: Masonry Revision, November 9, 2026. Issued flag is false.']);
row(s,19,['Do not use Belmont profiles, lengths, room counts, or waste for this project.']);
row(s,21,['Model remained unmodified. No external correspondence or notifications were sent.']);
s.tabColor='#4B6576';

s=by('651 Elements');base(s,'P',426,[15,16,19,21,18,18,16,16,44,34,23,19,20,55,48,65]);
title(s,'651 Belmont | Native wall-sweep records');
row(s,3,['Source: live model read on November 17, 2026. 422 distinct IDs. Length is NOT verified net.']);
head(s,4,['Element ID','Scope','Native level','Provisional Z band','Room','Raw Length (LF)','Minimum Z (ft)','Maximum Z (ft)','Profile','Material','Created phase','Demolished phase','Design option','UniqueId','Source receipt','Quantity limitation']);
s.getRange('A5:P426').values=data.rows;s.getRange('F5:H426').setNumberFormat('#,##0.0000');s.getRange('I5:P426').format.wrapText=true;s.getRange('A5:P426').format.rowHeight=40;
s.freezePanes.freezeRows(4);s.freezePanes.freezeColumns(2);s.tables.add('A4:P426',true,'BelmontNativeSweepRecords');

s=by('651 Feature Scope');base(s,'E',20,[28,24,52,21,55]);title(s,'651 Belmont | Decorative trim and continuations');
row(s,4,['Excluded from wall-sweep totals until separately verified.']);
head(s,6,['Location / feature','Source','Observed scope','Measured LF','Release issue']);
const features=[
['Unit 1 dining wall','A2.4 / detail 4','1 x 1 trim; 5-inch baseboard callout; dimensioned panel layout.','NOT VERIFIED','Resolve 5-inch vs 8-inch baseboard and exact panel-member cut lengths.'],
['Unit 1 living / entry','A2.4 / details 3, 6','Wood-slat door / 1 x 1 wood slat and entry details.','NOT VERIFIED','Separate decorative slats, door work, shelving and molding.'],
['Unit 1 primary bedroom','A2.4 / detail 5','1 x 3 trim; light-oak slat wall; 5-inch baseboard callout.','NOT VERIFIED','Verify approved profile and current geometry before calculating.'],
['Unit 2 primary bedroom','A2.5 / detail 3','1 x 3 trim; light-oak slat wall; 5-inch baseboard callout.','NOT VERIFIED','Sheet layout and modeled panel trim need reconciliation.'],
['Unit 3 master bedroom','A2.65 / detail 5','1 x 3 trim and black slat wall are labeled.','NOT VERIFIED','Reconcile existing elevation with current window adaptation and cut geometry.'],
['Fourth-floor window adaptation','Element 14123409 / Casework 45 13138641','Current adaptation and original panel identities were inspected.','NOT VERIFIED','Do not count source panel plus adaptation as duplicate complete panels.'],
['Crown continuations','Four Casework elements','Crown continuation around preserved reference; two 9672406 sides; first-floor 9194982.','NOT VERIFIED','Outside WallSweep totals; exact run length and overlap must be measured.']
];features.forEach((r,i)=>row(s,7+i,r));s.getRange('A7:E13').format.wrapText=true;s.getRange('A7:E13').format.rowHeight=78;
row(s,16,['No pixel scaling or bounding-box dimensions were used as verified takeoff quantities.']);
row(s,17,['Plan legends combine baseboard/crown; they do not resolve separate net runs by themselves.']);

s=by('Sources and Method');base(s,'F',45,[29,45,24,35,25,19]);title(s,'Sources, scope and verification');
head(s,4,['Source / method','Record','Date / unit','Meaning','Status','ID']);
row(s,5,['651 model','25-012 651 W. Belmont_Issue for Construction_','2026-11-17 live','Project 25-012; 651 W Belmont Ave','Unmodified','']);
row(s,6,['1529 model','25-006 1527 N Wieland','2026-11-17 live','Project 25-006; 1529 N Wieland St','Unmodified','']);
row(s,7,['651 baseboard profile','Baseboard : Baseboard','8 in H x 5/8 in T','Raw parameters, not rounded display','Verified profile','13053460']);
row(s,8,['651 crown profile','Selected 3in x 3-4in','Type-name designation','Dimensional profile not independently measured','Verify profile','13681858']);
row(s,9,['651 finish','BM White Dove - Semi Gloss','Model material','Applies to extracted base/crown types','Model value','13056506']);
row(s,10,['A2.4','UNIT 1 TRIM PLANS','Native export 11/17/26','Basement + 1st; dining / primary-bed details','Visually inspected','8628309']);
row(s,11,['A2.5','UNIT 2 TRIM PLAN','Native export 11/17/26','2nd floor; primary-bed detail','Visually inspected','8632443']);
row(s,12,['A2.65','UNIT 3 TRIM PLANS','Native export 11/17/26','3rd + 4th + roof; master-bed detail','Visually inspected','8835762']);
s.getRange('A5:F12').format.wrapText=true;s.getRange('A5:F12').format.rowHeight=52;
row(s,14,['Measurement basis: raw Revit Length, internal feet. Exact extraction does not establish net scope.']);
row(s,15,['Deduplication: 422 distinct native UniqueIds. Spatial/overlap duplicates remain unverified.']);
row(s,16,['Z band: greatest occupied level elevation <= element minimum Z, with 0.01 ft tolerance.']);
row(s,17,['T/ ROOF. band is provisional; stairs, multi-level elements and room coverage require review.']);
row(s,18,['No waste, procurement rounding, stock allowance, net deductions or purchase quantities assumed.']);
row(s,19,['Snapshot is not an issued-document approval. Stored metadata and cloud-version approval may differ.']);
row(s,20,['Detailed custom inspector is disabled in this Revit session; no configuration was changed.']);
head(s,23,['Project','Revision sequence','Revision date','Description','Issued flag','Element ID']);
data.revisions.forEach((r,i)=>row(s,24+i,r));s.getRange('A24:F36').format.wrapText=true;s.getRange('A24:F36').format.rowHeight=42;
row(s,39,['Models are workshared. Inspection and sheet export did not modify, save or synchronize them.']);
row(s,40,['Retained raw native receipts support every extracted element. No external communications sent.']);
w.recalculate();
for(const name of names){
 const rr=name==='651 Elements'?'A1:H12':name==='651 Review'?'A1:F34':name==='1529 Scope'?'A1:D21':name==='651 Feature Scope'?'A1:E17':'A1:F20';
 const blob=await w.render({sheetName:name,range:rr,scale:1,format:'png'});
 await fs.writeFile('preview_'+name.replaceAll(' ','_')+'.png',new Uint8Array(await blob.arrayBuffer()));
}
console.log((await w.inspect({kind:'table',range:"'651 Review'!A7:F9",include:'values,formulas',tableMaxRows:4,tableMaxCols:6,maxChars:2500})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:2000})).ndjson);
const file=await SpreadsheetFile.exportXlsx(w);await file.save('Trim_Takeoff_Review_651_Belmont_1529_Wieland_2026-11-17.xlsx');
console.log('EXPORTED');

