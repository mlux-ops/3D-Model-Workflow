TRIM TAKEOFF REVIEW - DRAFT, NOT ORDER-READY
651 Belmont and 1529 Wieland | Live model inspection: November 17, 2026

This package includes a workbook and three native Belmont sheet exports.
It is a traceable model inventory and scope-gap review, NOT a completed exact trim order.

651 BELMONT
201 baseboard WallSweep instances: raw Revit Length sum 2,014.2822793757216 LF.
221 crown WallSweep instances: raw Revit Length sum 1,914.477152902145 LF.
These are scheduled parameter values, not verified net cut lengths. Openings,
void cuts, joins, returns, overlaps and nested family trim are unresolved.
Four Casework crown continuations and decorative feature-wall trim are excluded.
The workbook retains all 422 element IDs, UniqueIds and source-receipt references.

Critical conflict: live baseboard profile is 8 inches high x 5/8 inch thick;
A2.4 and A2.5 label 5-inch baseboard. Revit's coarse formatted thickness
rounds 5/8 inch to 3/4 inch; raw numeric parameters were used.
Confirm the current approved design before quantity release.

The per-floor table uses provisional minimum-Z bands. It is not verified
room/unit allocation. Native levels are unreliable for some trim elements.
All extracted sweeps are New Construction, Main Model, not demolished.
Spatial duplicates have not been ruled out.

1529 WIELAND
The open file is named 25-006 1527 N Wieland, but Project Information explicitly
identifies 1529 N Wieland St and job 25-006. This alias is verified.
No standalone WallSweep instances or baseboard/crown-named types were returned.
That does not mean no trim is required. Generic-model queries fail and nested or
drawing-only scope remains unresolved. All net and purchasing quantities HOLD.

SOURCE STATUS
Belmont latest stored revision: Unit 3 Buyer Revision, October 16, 2026.
Wieland latest stored revision: Masonry Revision, November 9, 2026.
Stored revision Issued flags are false. Actual approved/issued status has not
been established from these flags alone.
Native sheet exports: A2.4 Unit 1, A2.5 Unit 2, A2.65 Unit 3.
No pixel-scaled measurements were used.

NEXT RELEASE CHECKS
1. Confirm applicable approved model/drawing revision and baseboard profile.
2. Obtain complete read-only geometry access, including rooms, nested Casework,
   generic model forms, voids and per-segment paths.
3. Reconcile feature-wall elevations with current window/trim adaptations.
4. Compute net runs and allocate by room/floor; check overlap and openings.
5. Select waste and stock lengths separately after net quantities are verified.

Both live workshared models remained unmodified. No save, synchronization,
configuration change, external correspondence or order was made.
