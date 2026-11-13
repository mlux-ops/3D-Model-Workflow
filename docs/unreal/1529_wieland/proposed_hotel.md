# The proposed hotel at 1520-1528 N. Wells ("The Duke of Wells"): what is known, with sources

Written 2026-11-13 for Phase 13. Everything modelled from this file is **proposed, modelled from published
renderings and records, not a survey**.

## Words used here

- **Site feet**: feet north and feet east of the south-west corner of the project lot (1527-1529 N. Wieland),
  along the level's axes (the level's north is -X, its east is -Y; 1 ft = 30.48006096 cm). The project lot is
  north 0 to 49.5, east 0 to 102.2.
- **The PD**: City of Chicago Residential-Business Planned Development No. 1335, as amended. A planned
  development is a site-specific zoning ordinance with its own drawings and limits.
- **The development land**: the land the PD covers.
- **Sub-area**: one of the three parts (A, B, C) the PD divides the land into.
- **a, b, z**: for the hotel, feet east of sub-area A's west line, feet south of sub-area A's north line, and
  feet above the hotel's first floor.
- **Scaled**: measured on a drawing with no written dimension, by counting pixels against a written dimension
  on the same drawing. Every scaled number is an estimate; its uncertainty is given.

## Sources

| Short name | What it is | Where |
| --- | --- | --- |
| PD | PD 1335 as amended: Journal of the Proceedings of the City Council, 9 Sept 2020, pp. 20742-20760 (application 20436, ordinance SO2020-3754, applicant Wellstel LLC, drawings by Pappageorge Haymes Partners, Plan Commission 20 Aug 2020). The same file opens with a letter of 8 Oct 2026 from the Department of Planning and Development and ends with the superseded 2016 version | https://gisapps.chicago.gov/gisimages/zoning_pds/PD1335.pdf, read 2026-11-13; copy `E:\Wieland1529_site_data\proposed_hotel\PD1335.pdf` (file pages 8-26 are the 2020 text and drawings) |
| County parcels | Cook County parcel outlines 2025 and building footprints 2022 (Phase 2 data) | `E:\Wieland1529_site_data\county_parcels_2025.json`, `county_footprints_2022.json`; drawn in `review/phase13/parcels_block.png`, listed in `review/phase13/parcels_block.csv` |
| Assessor addresses | Cook County Assessor "Parcel Addresses", block 17-04-203 | https://datacatalog.cookcountyil.gov/resource/3723-97qp.json, read 2026-11-13; copy kept outside the repository because it holds owner names |
| Permits | City of Chicago building permits, 1518-1530 N. Wells | https://data.cityofchicago.org/resource/ydr8-5enu.json, read 2026-11-13; copy `permits_1518_1530_N_Wells.json` |
| YIMBY 2024 | Chicago YIMBY, 11 Feb 2024, "Demolition permit issued for 1528 N. Wells hotel project in Old Town" | https://chicagoyimby.com/2024/02/demolition-permit-issued-for-1528-n-wells-hotel-project-in-old-town.html |
| Renderings | Ten pictures published with Chicago YIMBY's 2022 and 2024 articles (six exterior renderings, one flat Wells Street elevation, the site plan, a typical floor plan), one lead picture from Urbanize Chicago (Oct 2022), one from the architect's page | `E:\Wieland1529_site_data\proposed_hotel\yimby_1528NWells-1.jpg` to `-10.jpg`, `urbanize_lead_1528NWells_2022-10.jpg`, `pappageorgehaymes_152331_medium-1.jpg`; addresses in `manifest.csv` in that folder |
| Other press | Block Club Chicago 31 Aug 2020; Urbanize Chicago Oct 2022; The Real Deal 24 Apr 2025; Plan Commission hearing page Aug 2020 | read through the research step, not downloaded; addresses in `phase13_results.md` |

The reference pictures are the copyright of their publishers. They were read for shape and colour only; none
is in the Unreal project, none is a texture, none is in the repository.

## 1. Where it stands

### 1.1 The kickoff's premise about an alley is wrong: there is no alley

County parcels show block 17-04-203 without an alley. The lots on Wieland Street (east 0 to about 102-112)
back straight onto the lots on Wells Street (east about 102-112 to about 206). The PD's boundary map agrees:
the development land runs from the Wieland right-of-way to the Wells right-of-way with nothing between.
Wieland's right-of-way is 50 ft wide and Wells's is 80 ft wide (PD site plan).

### 1.2 The development land

PD statement 1 and boundary map (journal p. 20750): common address 1520-1532 N. Wells / 1513-1525 N. Wieland,
about 30,604 sq ft, between a line 313.23 ft and a line 462.78 ft south of North Avenue, from Wieland to Wells:
**149.55 ft north-south by 204.50 ft east-west**.

In site feet the development land is **north -149.55 to 0, east 0 to 204.5**. Its north line is the project
lot's south line. This placement follows from the county parcels: the parcel directly south of the project
lot is 17-04-203-012 (1525 N. Wieland), the PD's northernmost Wieland address. The county map puts the Wells
Street line at about east 206, the PD at 204.5: a disagreement of about 1.3 ft. The model is anchored on the
Wieland line, so anything on Wells Street may be about 1.3 ft off in the east-west direction.

| Sub-area | What the PD puts there | Size (PD) | Site feet |
| --- | --- | --- | --- |
| A | The 12-storey hotel with its 3-storey garage | 21,934 sq ft; 175.75 ft east-west by 124.80 ft north-south | north -149.55 to -24.75, east 28.75 to 204.5 |
| B | Three single-family homes on Lots 1, 2, 3 | 6,119 sq ft; Lots 1 and 2 are 1,795 sq ft each, Lot 3 is 2,531 sq ft | Lots 1 and 2: north -149.55 to -24.75, east 0 to 28.75 (Lot 1 the southern half, Lot 2 the northern). Lot 3: north -24.75 to 0, east 0 to 102.25 |
| C | The existing 2-storey building 1532 N. Wells, which stays | 2,530 sq ft | north -24.75 to 0, east 102.25 to 204.5 |

County parcels on the development land (parcel number, Assessor's address, outline in site feet from the county map):

| Parcel | Address | North | East | In the PD as |
| --- | --- | --- | --- | --- |
| 17-04-203-012 | 1525 N. Wieland | -25.0 to -0.1 | 0 to 102 | Lot 3 (Home 3) |
| 17-04-203-013 | 1523 N. Wieland | -49.6 to -25.0 | 0 to 102 | Lot 2 west end, garage |
| 17-04-203-086 | 1521 N. Wieland | -74.4 to -49.5 | 0 to 112.2 | Lot 2 west end, garage |
| 17-04-203-015 | 1515 N. Wieland | -123.9 to -74.2 | 0 to 102 | Lots 2 and 1 west end, garage |
| 17-04-203-016 | 1513 N. Wieland | -148.4 to -123.8 | 0 to 102 | Lot 1 west end, garage |
| 17-04-203-029 | 1532 N. Wells | -25.0 to -0.1 | 102 to 206 | Sub-area C (stays) |
| 17-04-203-030 | 1530 N. Wells | -49.7 to -24.9 | 102 to 206 | hotel |
| 17-04-203-087 | 1528 N. Wells | -74.5 to -49.6 | 112.2 to 206 | hotel |
| 17-04-203-032 | 1524 N. Wells | -99.2 to -74.4 | 102 to 206 | hotel |
| 17-04-203-033 | 1522 N. Wells | -124.0 to -99.1 | 102 to 206 | hotel |
| 17-04-203-034 | 1520 N. Wells | -148.5 to -123.9 | 102 to 206 | hotel |

The hotel therefore uses more parcels than the kickoff's "1520-1528 N. Wells": it also uses 1530 N. Wells and
the rear parts of 1513-1523 N. Wieland.

### 1.3 What the present site model has on that land

Found by asking the editor for every object whose bounds overlap the land (`review/phase13/objects_on_site.json`)
and by reading the triangles of the two earlier detailed parts (`review/phase13/scripts/r15_parts_by_north.py`).

| Object in the model | Level | What it is | In the option "Duke of Wells (proposed)" |
| --- | --- | --- | --- |
| `SB_782868` | L_Surroundings | Plain block of the existing 3-storey building 1520 N. Wells (north -148 to -121.7, east 102.9 to 202.7, 44.7 ft high) | hidden |
| `R15_PART_opaque_xm04_yp01_part01`, `R15_PART_glass_xm04_yp01_part01` | L_Surroundings_R15 | The existing house 1525 N. Wieland in detail (north -25.3 to -0.2, east 0 to 63, 29.4 ft high) | hidden (Home 3 stands here) |
| `R15_PART_opaque_xm04_yp02_part01`, `R15_PART_glass_xm04_yp02_part01` | L_Surroundings_R15 | 1534 and 1532 N. Wells in detail. South of north -25.1 this part holds only kerb-height objects in the Wells Street pavement (east 208 and beyond, up to 1.9 ft) | stays (1532 stays in the PD; 1534 is outside it) |
| `SB_781577` (1532 N. Wells), `SB_781632` (1525 N. Wieland) | L_Surroundings | Plain blocks already hidden since Phase 7, replaced by the detailed parts | untouched (already hidden) |
| ground tiles `SW_ground_3_2`, `3_3`, `4_2`, `4_3` | L_SiteWorks | modelled ground | stay |

The lots 1522-1530 N. Wells and 1513-1523 N. Wieland are empty in the 2022 county footprints and in the model.
The modelled ground on the land lies between -0.5 ft and +1.5 ft of the level's zero; about +1.0 ft at the
Wells Street pavement and about 0 ft at the Wieland Street pavement (`review/phase13/scripts/ground_heights.py`).

### 1.4 State of the real project (2026-11-13)

- The Department's letter of 8 Oct 2026 (first pages of the PD file) extends the PD by one year, to
  9 Sept 2027, and allows a temporary public parking lot at 1520-1524 N. Wells until the development is
  pursued. So the hotel was not under construction in October 2026.
- Permits: 100966661 (4 Oct 2022, 1524 N. Wells, foundation and basement only for a new 12-storey hotel with
  3 levels of parking), reinstated 18 Apr 2023 and 25 Jun 2026; B101080797 (1 May 2026, 1520 N. Wells,
  wrecking of the 3-storey masonry building). The existing building 1520 N. Wells may therefore already be
  gone in reality; the option "Existing buildings (as surveyed)" shows it as the 2022 county footprints do.
- The Real Deal, 24 Apr 2025, reports a foreclosure suit against the developer over this land.

## 2. The hotel (sub-area A)

### 2.1 Numbers written in the PD

| Item | Value | Source |
| --- | --- | --- |
| Storeys | 12, plus a mechanical penthouse | PD site plan "Proposed 12 Story Hotel"; elevations |
| Height | **151 ft 4 in** to the roof of the mechanical penthouse (the press rounds it to 151 ft) | PD bulk table (p. 20747) and elevations |
| Hotel rooms | 203 | PD bulk table |
| Parking | 47 spaces in sub-area A on three levels, 1 loading berth | PD bulk table, plans |
| Setbacks from the land's lines | 0 ft north and south (written on the site plan and elevations) | PD |
| Floor levels | 1st 0; parking level 2 +8 ft 8 in; 2nd +17 ft 0 in; 3rd +32 ft 4 in; 7th +72 ft 8 in; 9th +93 ft 8 in; 11th +114 ft 8 in; 12th +127 ft 8 in; mechanical penthouse +142 ft 0 in; roof +151 ft 4 in | PD elevations (pp. 20756-20759) |
| Materials named | face brick; recessed face brick of contrasting colour; stone base; stone sill; pre-finished aluminium window system; metal canopy; gas lanterns; blade signage; painted metal railing; glass guard rail (12th floor); metal panel and architectural louvre (mechanical penthouse) | PD elevations |
| Colours | red and dark grey brick; loft-style windows about 8 ft | YIMBY 2024; renderings |

Floor levels not written (4th-6th, 8th, 10th) are **estimates** by equal division between the written ones:
4th +42.42, 5th +52.50, 6th +62.58, 8th +83.17, 10th +104.17 ft (uncertainty 0.5 ft).

### 2.2 The massing (all scaled; estimates)

Scaled from the PD roof plan (journal p. 20755, about 7.5 pixels per foot at 250 dpi) and checked against the
published typical floor plan and the flat Wells Street elevation (both scaled against the 124.80 ft width).
The two readings agree within 1.5 ft. **Uncertainty: 2 ft on every number in this table** unless said.

| Part | a (ft east of sub-area A's west line) | b (ft south of its north line) | z (ft above the first floor) | Notes |
| --- | --- | --- | --- | --- |
| Garage, 3 storeys, green roof | 0 to 48.4 | 0 to 124.8 | 0 to 32.33 (roof level assumed equal to the 3rd floor; uncertainty 3 ft) | "3 Story Parking Garage ... 4th Floor Green Roof" (roof plan) |
| Base, floors 1 and 2 | 48.4 to 175.75 | 0 to 124.8 | 0 to 32.33 | covers the whole lot width |
| Tower, floors 3 to 11 | 48.4 to 149.3 | 12.0 to 112.4 | 32.33 to 127.67 | 100.9 ft by 100.4 ft; 12 ft "3rd floor terrace" strips north and south |
| West face, middle bay | set back 2 ft (uncertainty 1.5 ft) | 42.9 to 80.9 | as tower | dark grey brick, three window columns (floor plan, renderings) |
| North wing on Wells | 149.3 to 175.75 | 0 to 41.0 | 0 to 93.67 | roof is the "9th floor terrace" |
| South wing on Wells | 149.3 to 175.75 | 84.5 to 124.8 | 0 to 72.67 | roof is the "7th floor terrace"; garage entrance at its foot |
| Middle of the Wells front | 149.3 to 175.75 | 41.0 to 84.5 | 0 to 17.0 | one storey with the entrance and canopy; "2nd floor terrace" on top |
| Dark grey projecting part | 149.3 to 158.3 (depth 9 ft, uncertainty 1.5 ft) | 68.3 to 112.4 | 17.0 to 114.67 | roof is the "11th floor terrace" |
| 12th floor | 64 to 132.5 | 24.6 to 88.5, with a leg to 103.8 over a 64 to 100 (leg: uncertainty 4 ft) | 127.67 to 142.0 | dark grey brick; terrace with glass guard around it; steel pergola on the east side |
| Mechanical penthouse | 66 to 114.2 | 42.6 to 82.5 | 142.0 to 151.33 | metal panel with louvres |

In site feet the tower (floors 3 to 11) stands at **north -137.15 to -36.75, east 77.15 to 178.05**. Its north
face is about 37 ft south of the project lot's south line. The garage's west wall is at east 28.75.

### 2.3 The faces (from the renderings; estimates)

- Windows: about 7.5 ft wide and 7.5 ft high (uncertainty 1 ft), gridded into small panes, set back in the
  brick, stone sill. Wells front: three columns on each wing, three in the middle (the southern one in the
  dark grey part); above the wings seven columns across the tower. North and south faces: seven columns.
  West face: three large columns in the dark middle bay; on each red side bay one column of small windows and
  one column of recessed panels of dark brick ("recessed face brick of contrasting colour").
- Bands: stone band at the 3rd floor level on the Wells front; light stone cornice at the 12th floor level;
  stone copings on the parapets.
- Ground floor on Wells: garage door at the south end, glazed entrance with a metal canopy in the middle,
  glazed shopfront in the north wing, dark surround.
- Not modelled: the existing street clock, gas lanterns, blade signs, street trees, furniture on the terraces.

## 3. The homes (sub-area B)

**Three homes, not two.** The PD (bulk table: 3 dwelling units; north and south elevations: "(3) Single-Family
Homes"; site plan: three outlines marked "3 Story SFH") has three. The press (Block Club 2020, Urbanize 2022,
YIMBY 2024) writes "two" or "a pair", counting only the two that screen the garage on Wieland. The PD is the
legal record, so three are modelled. The PD says the homes' final design is subject to the Department's
review; only outlines are drawn. Height limit 47 ft (PD); the renderings show three storeys with flat roofs.

All outlines scaled from the PD site plan (about 7.56 pixels per foot). **Uncertainty 2 ft; heights 4 ft.**

| Home | Lot | Site feet (north; east) | Height modelled | Look (renderings) |
| --- | --- | --- | --- | --- |
| Home 1 (south) | Lot 1 | north -146.15 to -97.65; east 5.5 to 27.3 | 40 ft | light limestone front, five window columns |
| Home 2 (north) | Lot 2 | north -76.35 to -27.15; east 5.5 to 27.3 | 40 ft | dark grey brick with light stone bands, five window columns |
| Home 3 | Lot 3 = 1525 N. Wieland | north -22.3 to -1.7; east 2.6 to 59.8 | 38 ft | narrow red brick front with a garage door |

Home 3 stands on the lot that adjoins the project lot's south line: its north wall is about 1.7 ft from that
line. Between Homes 1 and 2 are two 10 ft driveways (PD site plan).

## 4. What is not settled by published material (for the owner)

1. Every number in sections 2.2, 2.3 and 3 is scaled from small drawings or read off renderings.
   Dimensioned permit drawings would replace them; none is public.
2. The homes' design is not final in the PD.
3. The garage's roof level and its outside walls are not dimensioned or rendered clearly.
4. The Wells Street line: PD 204.5 ft from Wieland, county map about 206 ft.
5. Whether the hotel will be built as drawn in 2020: the PD is extended to 9 Sept 2027, the land is in a
   foreclosure dispute (The Real Deal, 2025), and The Real Deal says the plan "was altered in 2024 to add a
   few more rooms". No drawing of a 2024 change is public.
6. Published facts that disagree: storeys 12 (PD drawings, permits, press) or 13 (Plan Commission hearing
   page 2020, architect's page); height 151 ft 4 in (PD) or 152 ft (hearing page); rooms 203 (PD 2020) or 190
   (2016 version, architect's page).
