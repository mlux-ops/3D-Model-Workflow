# R44 executable jig synthetic tests (not actual 1529 conditions)

Create a scratch copy of any one blank unit input, set hypothetical W3=30.48in, H=93in, N=24in, NH=12in, C=15.24in, Z=40in, tile long=10in, short=2in, grout=.125in, niche depth=4in, actual valve rough finished depth=2.5in, backer+membrane+mortar+tile=22mm and all signed flags FALSE, obstruction NONE.

Case 1: left/right projection=0 and execution tolerance=0. Computed finished piers=3.24/3.24in. Jig returns GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE; purchase_authorized false.

Case 2: left/right projection=.25in, tolerance=0. Finished piers=2.99/2.99in. REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION; purchase_authorized false.

Case 3: use 16in centered aperture and projections .25. Finished piers=6.99/6.99in. GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE; purchase_authorized false.

Case 4: same as case 3 but obstruction 10:20 means niche overlaps an actual *synthetic* pipe/service exclusion. REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION regardless of pier size.

Case 5: leave obstruction field empty. HOLD_MISSING_PHYSICAL_OBSTRUCTION_SURVEY even if piers pass.

These are deliberately mathematical tests; actual 1529 measurements, manufacturer approvals and owner releases remain absent.
