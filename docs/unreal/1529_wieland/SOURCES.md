# Sources: real-world data proposed for the 1529 N. Wieland scene

All pages were read on 2026-11-10 unless a row says "not read". Companion to [PLAN.md](PLAN.md).

## How to read this file

- **Read** means the page or its metadata record was opened on 2026-11-10. **Snippet** means only a search-result excerpt was seen because the page refused the request. **Not read** means the source is proposed but its page was not opened; its terms must be read before the plan uses it.
- "Looking" means viewing a page in a browser. "More than looking" means saving a copy, measuring or tracing from it, making a texture or model from it, or bringing it into the engine.
- Nothing in this file has been downloaded. Every download is listed in PLAN.md under "Approvals this plan will ask for", with its size.
- None of the public datasets mentions this block by name. What each one shows for this block is known only where this file says a query was run.

## What the two street numbers cover

Read from Cook County and City of Chicago records on 2026-11-10:

| Fact | Value | Source |
|---|---|---|
| 1529 N. Wieland St. | Parcel number (PIN) 17-04-203-010-0000. Centre at latitude 41.9102490, longitude -87.6353897; Illinois State Plane East x 1,174,226.83 ft, y 1,910,657.55 ft. Assessor class 211. | Cook County Assessor, Parcel Addresses and Parcel Universe tables |
| 1527 N. Wieland St. | PIN 17-04-203-011-0000. Centre at latitude 41.9101811, longitude -87.6353878; x 1,174,227.55 ft, y 1,910,632.81 ft. Assessor class 211. | same |
| Relationship | Two adjacent parcels with the same taxpayer of record. Their centres are 24.75 ft apart, so each is about 24.75 ft wide and the pair about 49.5 ft. The owner's site plan (sheet T1.4 of drawing set 25-006) records the combined lot as 49.50 ft by 102.20 ft, which agrees. | computed from the centres; earlier project registration file |
| Neighbours | 1533 N. Wieland is PIN 17-04-203-009-0000 (north). 1525 is PIN 17-04-203-012-0000 and 1523 is PIN 17-04-203-013-0000 (south). | Parcel Addresses table |
| Permits | Demolition permit B101082080 at 1527 (two-story masonry multi-unit residence), issued 2026-06-02, status complete. Demolition permit B101082082 at 1531 (two-story frame multi-unit residence), issued 2026-06-23, status complete. The table gives issue dates and status, not the day the work finished; street imagery shows the lot cleared by August 2026. New-construction permit 101086781 at 1529, issued 2026-09-03, active: a new four-story, four-unit residence with basement, roof decks, pergolas and a two-car garage. | City of Chicago Building Permits table |
| A third number | The city's permit for one of the demolished houses uses 1531, and Google labels its August 2026 street panorama "1531 N Wieland St". Expect records under 1527, 1529 and 1531. | permits table; Street View |

## Sources the plan uses

### The owner's own material (strongest evidence)

| Source | What it proves | What it cannot prove | Terms | Used for |
|---|---|---|---|---|
| Drawing set 25-006: survey sheet T1.1 (fieldwork 2025-08-18) and site plan sheet T1.4. Not in this repository; quoted in the earlier project's registration file at `E:\Games\Claude\1527 Wieland\fbx_walkthrough\01_sources\manifests\registration_r01\registration_basis.json`. | Lot corners and dimensions (measured frontage 50.18 ft, rear 50.50 ft, record 49.50 ft by 102.20 ft), setbacks (front 10 ft 2.5 in, rear 20 ft), north arrow, and whatever spot elevations and existing trees the surveyor recorded. | Anything outside the survey limits. The survey predates the 2026 demolition. | Owner's property. | Placing the building and the lot to survey accuracy; true north. |
| The Revit 2025 model. Location to be given by the owner. | The building: geometry, materials, fixtures, project location and true-north angle. | The surroundings. | Owner's property. | Phase 3. |
| The owner's site photographs and tape or laser measurements, to be taken on a site visit. | Present condition, materials, colours against a grey card, tree species and trunk sizes, positions of poles, signs, hydrants and fences, and the alley. These are the only images that may be saved and laid beside a render. | Leaf-on appearance, if the visit is in November. | Owner's property. | Reference images for every exterior station; material sources; positions. |

### Parcels, buildings and ground

| Source and URL | Read | What it holds | Accuracy stated | Licence or terms, and what they permit | Used for |
|---|---|---|---|---|---|
| Cook County Assessor, Parcel Addresses. https://datacatalog.cookcountyil.gov/Property-Taxation/Assessor-Parcel-Addresses/3723-97qp | Read; queried for this block | PIN, property address, owner and mailing address per tax year. No shapes. | None | No licence stated on the record. County site terms: information is provided "ON AN "AS IS" BASIS". The table holds personal data, so the plan records PINs only. | Identifying the parcels (done). |
| Cook County Assessor, Parcel Universe (current year). https://datacatalog.cookcountyil.gov/resource/pabr-t5kh.json | Read; queried for the two PINs | PIN, class, centre latitude and longitude, State Plane centre coordinates. | None; centres come from the county parcel shapes. | Same as above. | A first position for the site, within about 3 m. |
| Cook County parcel polygons, 2025. https://gis.cookcountyil.gov/traditional/rest/services/parcelHistorical/MapServer/2025 | Read (metadata) | Tax parcel outlines as of 2025. | **None stated.** "While efforts have been made to be as accurate as possible, Cook County provides the data for use “as is”." | Custom county terms; use "as is". The county site also says its content is copyrighted. Reading and private use in a model are not restricted by any clause found; redistribution is unclear. | Lot lines of neighbours; measuring the street's true bearing. |
| Cook County Building Footprints 2022. https://gis.cookcountyil.gov/traditional/rest/services/buildingFootprint_2022/MapServer/0 | Read (metadata) | Building outlines "built from Spring 2022 imagery and Lidar" with ground elevation, highest point and height above ground for each. | None stated. | Same county "as is" terms. | Footprints and heights of neighbours. **Cannot show** anything built or demolished after spring 2022, roof shape, or facade detail. |
| City of Chicago Building Footprints. https://data.cityofchicago.org/d/syp8-uezg | Read (metadata) | Outlines with stories and year built. "Current as of August 2015". No height field. | None stated. | "See Terms of Use". The terms page refused the request; a snippet says the City gives no warranty and may require a user to stop using the data. | Stories and year built as leads only. The earlier site model was built on this layer, which is one reason its heights are estimates. |
| Cook County lidar, 2022 (Illinois State Geological Survey). https://clearinghouse.isgs.illinois.edu/data/elevation/illinois-height-modernization-ilhmp and metadata at https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer/info/metadata | Read | Classified laser point cloud flown 2022-04-05 to 2022-06-29, leaf-off. At least 20 points per square metre; measured spacing 0.224 m. Tiles are 2,500 ft square. | Vertical: root-mean-square error 0.3 ft (9.25 cm); 0.6 ft (18.2 cm) at 95 percent confidence. Horizontal: not stated for 2022. | "No restrictions apply to these data." Use constraints: "None." | Ground levels, kerb and sidewalk grades, building heights and roof forms, tree crown height and spread. **Cannot show** species, trunk diameter, facade detail, or anything changed since spring 2022. |
| Cook County lidar, 2017 (U.S. Geological Survey 3D Elevation Program). https://www.fisheries.noaa.gov/inport/item/59012 | Read | Point cloud flown April to May 2017; spacing 0.35 m. | Vertical 10.1 cm at 95 percent; horizontal root-mean-square error 41 cm east, 35.6 cm north. | "All 3DEP products are available, free of charge and without use restrictions." (https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) | A second date for buildings since demolished or rebuilt, and the only lidar with a stated horizontal accuracy. |
| Cook County elevation model and 1 ft contours, 2022. https://gis.cookcountyil.gov/imagery/rest/services/DEM2022/ImageServer | Read (metadata) | Ground surface at 1 ft cells. | None stated. | County "as is" terms; the 2022 record uses "personal use" wording. | A quick check of grades before lidar tiles are approved. |
| Cook County aerial photography, 6-inch pixels, 2018 to 2025. Pattern https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2019/ImageServer | Read (metadata) | Vertical aerial photographs. | **None stated.** | "Cook County provides the data for personal use “as is”" (2018 to 2023) or "use as is" (2024, 2025). | Plan-view comparison with a top-down render; kerb lines, driveways, tree crowns. Not used as a texture. |

### Streets, zoning and permits

| Source and URL | Read | What it holds | Licence | Used for |
|---|---|---|---|---|
| City of Chicago Building Permits. https://data.cityofchicago.org/d/ydr8-5enu | Read; queried for 1521 to 1537 N. Wieland | Permits since 2006 with work descriptions. | "See Terms of Use". | What was demolished and built, and when (done). Dates for neighbours: 1526 new four-story eight-unit building (2021), 1532 new four-story house (2016), 1534 raised frame house with basement garage (2014 to 2015). |
| City of Chicago Street Center Lines. https://data.cityofchicago.org/d/6imu-meau | Read (metadata) | Centre lines, one-way direction. No right-of-way width. | None stated. | Street name and direction only. |
| City of Chicago Sidewalks. Dataset id 77cn-6x4c | Read (metadata) | Draft sidewalk outlines, "current as of December 2011". | "See Terms of Use". | Lead only; too old to place anything. |
| City of Chicago Zoning Districts. https://data.cityofchicago.org/d/dj47-wfun | Read (metadata) | Zoning class, updated 2026-11-04. | "See Terms of Use". | Context only. |
| Chicago Landmark Districts. Dataset ids zidz-sdfj and t8pq-wu86 | Read (metadata) | District outlines, 2011. | "See Terms of Use". | Whether the block lies in the Old Town Triangle district is **not established**. The district is described as bounded on the south by North Avenue, which would put the 1500 block outside it; that is inference. |

### Street-level and overhead imagery from Google

| Product and terms page | Terms date | What the terms say | Used for |
|---|---|---|---|
| Street View. Permissions page: https://about.google/brand-resource-center/products-and-services/geo-guidelines/ | Page shows no date; server header 2025-08-08 | "You may not screenshot Street View imagery or remove it from embedded sources for any purpose." Prohibited: "Creating data from Street View images, such as digitizing or tracing information from the imagery", "Using applications to analyze and extract information", "Downloading Street View images to use separately from Google services (such as an offline copy)", and stitching. "These restrictions apply to all academic, nonprofit, and commercial projects." Measuring by eye in the browser is not addressed. | **Looking only**, in a browser, cited by link and capture date. No saved copies, no tracing of positions, no textures, no measurements entered as data. Observations made by looking are recorded as leads to confirm on site. |
| Google Maps and Google Earth, end-user terms. https://www.google.com/help/terms_maps/ | "Last Modified: January 27, 2026" | May not "copy the content" except as the permissions page or fair use allows; may not "mass download"; may not use it to build a substitute mapping dataset. The permissions page allows capturing "a screenshot from Google Maps" for annotation with attribution kept, and bars using Google Earth output "to reconstruct 3D models or create similar content". | Looking only. |
| Google Photorealistic 3D Tiles (the 3D city mesh). Policies: https://developers.google.com/maps/documentation/tile/policies ; platform terms: https://cloud.google.com/maps-platform/terms | Policies "Last updated 2026-11-09 UTC"; terms "Last modified August 26, 2026" | For "map visualizations" only. No caching or offline use. "Don't create content based on Google Maps Content." "You may overlay your own 3D objects on Photorealistic 3D Tiles as long as the 3D objects aren't extracted, traced, or otherwise derived by hand or machine from Photorealistic 3D Tiles." Attribution and the Google Maps logo must stay on screen. Promotional video is limited to 30 seconds. Stills and non-promotional video are not addressed. Needs a billing account and key from Google, or a Cesium ion account. Cesium's own schedule bars including the content "in any electronic or printed documents", and Cesium's free plan is for "Personal and non-commercial use". The streaming plugin supports engine 5.6 to 5.8, not 5.9. | **Not used by default.** Offered as an owner's choice for the distant city in OPEN_DECISIONS.md. If chosen, it may only be streamed live as a backdrop with attribution shown; nothing may be baked, traced or kept. |

Views looked at on 2026-11-10, each a live link with Google's stated capture month:

| View | Capture | Link |
|---|---|---|
| From the roadway in front of the site, looking east at the lot | August 2026 | https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,90h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| Same position, looking south-east | August 2026 | https://www.google.com/maps/@41.910283,-87.6356719,3a,75y,125h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| Same position, looking west at the houses opposite | August 2026 | https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,270h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| Same position, looking north along Wieland | August 2026 | https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,0h,92t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| Same position, looking south along Wieland | August 2026 | https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,180h,92t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| A few metres south, looking south-east, before demolition | November 2025 | https://www.google.com/maps/@41.9102539,-87.6356797,3a,75y,125h,95t/data=!3m6!1e1!3m4!1sO-GLxn-B8NqXRQZBi26Kgg!2e0!7i16384!8i8192 |

Earlier captures at this position are offered by Google for November 2021, August 2019 and October 2018. The alley was not seen: the one attempt opened a shop's interior panorama on Wells Street instead.

### Open street-level imagery

| Source | Read | Terms | Used for |
|---|---|---|---|
| Mapillary. https://www.mapillary.com/terms ("Effective date: February 15, 2024") | Read | Other users' images are under "the Creative Commons Share Alike (CC BY-SA) license". The same terms bar "any derivative works based upon the Mapillary Services" and limit commercial use to listed purposes. Whether textures or measurements from an image are allowed is **unresolved**. | Looking only until the owner decides otherwise. Whether Mapillary has any images of this block was not checked; the map is at https://www.mapillary.com/app/?lat=41.9102&lng=-87.6356&z=18 |
| KartaView | Snippet | Reported as CC BY-SA 4.0 by the OpenStreetMap wiki; its own terms were not read. | Not used. |

### Trees and street furniture

| Subject | Finding |
|---|---|
| Street trees | **No public record of individual street trees with species and trunk size was found for Chicago.** The city's data portal holds only tree-trim and debris requests. A full inventory was promised in 2019 and recommended again in the 2023 urban forest plan; no published inventory was found. Lidar gives crown height and spread. Species and trunk diameter have to come from the site visit. |
| Light poles, hydrants, signs, kerbs, alleys | **No open dataset found** for any of them. The city's street-lighting and public-way standards documents refused the request, so pole types and standard sidewalk dimensions are unread. Positions and types come from the site visit. |

### Materials, light fixtures and sun

| Source and URL | Read | Licence | Used for |
|---|---|---|---|
| Poly Haven, ambientCG and ShareTextures texture libraries. https://polyhaven.com , https://ambientcg.com , https://www.sharetextures.com | Not read on 2026-11-10. The earlier project's records call their textures CC0 (public-domain dedication). | To be read before any new download. | Base maps for surroundings where the owner's photographs do not suffice. |
| Fab and Megascans assets already inside the existing project (tree library, one worn-brick surface) | Not read. No licence record was kept with the project. | To be read; the earlier work recorded "No paid asset purchase was made". | Kept only after the licence is recorded. |
| Fixture manufacturers' photometric files for the fixtures in this repository's families | Not read. | Each manufacturer's download terms, to be read per file. | Interior and exterior light fixtures, Phase 8. |
| NOAA Solar Calculator. https://gml.noaa.gov/grad/solcalc/ | Not read on 2026-11-10. | Terms not read. It is a United States government web tool; that it may be used freely is an expectation to confirm on the page in Phase 1. | Independent check of the engine's sun position. It is looked at in a browser; nothing is downloaded. |
| A regional tree identification key | Not chosen and not read. | To be read when chosen. | Naming tree species from the owner's photographs in Phase 2. Candidates are a Morton Arboretum or Illinois Extension guide; the choice and its terms are recorded here before use. |
| Fab, Epic's asset store, for new tree models and interior furniture. https://www.fab.com | Not read on 2026-11-10. | Licence to be read per item before each request to the owner. | Only items the owner approves one by one. |
| Prices quoted for Google's 3D city tiles in OPEN_DECISIONS.md | Read on 2026-11-10 by a research helper | Cesium: https://cesium.com/platform/cesium-ion/pricing/ (no date shown). Google: https://developers.google.com/maps/billing-and-pricing/pricing ("Last updated 2026-11-09 UTC"); the table's column headings were garbled in the text read, so Google's figures need checking on the live page. | Decision 6 only. |
| This repository's material packages (colour and 16-bit height maps under `output\`) | Read (repository) | Owner's property; sources recorded per package. | Interior finishes, Phase 5 and Phase 6. |

## Coordinate systems

- County and city data are in Illinois State Plane East, US survey feet. Older layers use the 1983 datum; the 2022 lidar, elevation model and footprints use the 2011 adjustment. In the international registry of coordinate systems (EPSG) these are codes 3435 and 6455. The shift between the two was not sourced. Phase 2 reads the system from each file's header and never assumes it.
- Heights in the 2022 lidar are in feet above the North American Vertical Datum of 1988 (NAVD88), using the Geoid 18 model. The 2017 record contradicts itself on geoid and units; its file headers decide.
- Grid north in this projection is about 0.47 degrees east of true north at the site (computed from the projection's central meridian, -88.3333 degrees). Chicago's street grid is separately reported to lie "a little more than one degree west of true north" (Chicago Public Library, snippet). The two parcel centres give roughly 1.2 degrees west of true north for this block, which is a rough figure from two points. Phase 2 measures it from the parcel outlines and the survey.

## Could not be read

- City of Chicago data terms of use, street-lighting standards, public-way rules, urban forest plan and landmark district documents (all refused the request).
- Cook County's map viewer (connection refused).
- Mapillary's licence help page (refused).
- Positional accuracy of county parcels, 2022 footprints and aerial photography: none is published.
