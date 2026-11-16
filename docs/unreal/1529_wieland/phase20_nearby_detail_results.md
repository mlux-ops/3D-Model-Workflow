# Nearby building detail extension

Status: IN PROGRESS, owner scope added 2026-11-15 17:33 during crash recovery. Earlier detailed coverage restored and saved; measured extension staged. Two obsolete project-lot footprints excluded, leaving 682 extension targets. Owner approved inferred facade detail at 18:49; three geometry pilots ready for native visual review. Streets and immediate-neighbour checks underway. No owner videos or r3 made yet.

Owner direction: use the earlier detailed buildings on Wieland and Wells within two blocks, then bring all other buildings in a further two-block band to the same level of quality. Preserve the updated skyline. Finish this model work before the seven walking-path videos and r3 delivery.

Standing rules: preserve L_R15_Production and Datasmith assets; use named new assets and reversible overrides; clean built forms only; measured positions and heights remain authoritative; no Google content; no fabricated factual facade claims. Owner removed all memory guards at 17:19; passive memory logging continues.

Owner update 2026-11-15 18:49: YES to inferred facade windows, trim and colours, with assumptions recorded. Extend built roads and sidewalks to the same four-block refinement boundary. Pay special attention to the two immediate neighbours, 1525 and 1533 N Wieland. This resolves the pending facade choice; no further approval for that work is needed.

## Journal

| No. | Time | Step | Outcome |
|---|---|---|---|
| N1 | 2026-11-15 17:34 | Map the requested inner streets and outer two-block band; inspect the earlier assets, measured outlines and photographic evidence; identify which buildings can be restored and which need new work. | DONE 17:43, provisional street-bounded interpretation: inner Wieland/Wells from Evergreen to Eugenie; outer band Scott to Menomonee, Orleans to Clark. 736 county footprints, 698 higher than 4 m, including rear buildings/garages; 52 have earlier detail, 238 have cached 1 ft DSM. Map scope_map.png and building_scope.csv. Source: existing Cook County outlines and new public OSM roads cache (ODbL), no Google data. Owner asked whether plausible facade detail may be inferred where sources are missing; until answered, only measured/source-supported extension proceeds. |
| N3 | 2026-11-15 17:44 | Extend measured building coverage across the mapped area: reuse existing clean forms, fetch missing 1 ft surface measurements within the authorized data cap, join existing city/OSM/assessor evidence, retain source-supported roof forms. All facade inferences remain pending the owner's answer. | DONE measured preparation: 498 new clean forms plus 186 reused clean forms; 684 staged native objects. Two 2022 buildings on the project lot (781075, 781331) are historical and explicitly excluded, kept hidden without deletion; active extension targets 682. City footprints match 697 of 736 raw footprints, OSM 703, storey counts available for 487, wall-material records 94, verified wall colours 0. Sources and exclusions recorded per building. This is measured massing preparation, not completed facade detail. |

| N2 | 2026-11-15 17:36 | Restore the 57 fitted earlier detailed pieces while retaining Phase 17 skyline and ground; hide the 52 local Phase 17 replacements identified by the existing measured overlap table. Preserve prior variant choices and write a new hybrid option. Save named copy levels and variant only after readback. | DONE 17:38. Earlier pieces 57/57 visible; 52 overlapping P17Z buildings hidden; all remaining 522 Phase 17 objects visible, including the updated skyline and ground. Phase 4 blocks and generic far-city stand-in remain hidden. New additive option Earlier local buildings + updated skyline captures all 776 objects; existing options retained. Saved variant and L_Surroundings_R15, L_Surroundings_P17 by name. S2_hybrid.0000.png checked: detailed front windows, siding, stoops and trim restored, no warning text. |

| N4 | 2026-11-15 17:50 | Native staging of the measured extension in a separate new sublevel and new mesh assets; three pilot forms first, validate triangle count/UV/Nanite and position, then batches. Keep these staging objects hidden until facade decisions and overlap checks are resolved. | DONE 17:55: 684/684 native meshes and placed objects in L_Nearby_Detail, triangle counts match, one UV channel each, Nanite on, all hidden. New assets and this level saved by name. N3 geometry preparation: 498 new clean measured forms plus 186 reused clean forms, 684/684, no build failures, 67145 triangles; 52 earlier detailed buildings excluded from replacement. New source DSM 27.3 MB. |

| N5 | 2026-11-15 18:49 | Owner-approved inferred facade detail: real recessed glazing, frames, sills/lintels, plinths and cornices on the measured forms; source materials/storeys where available, visual assumptions recorded elsewhere. Three native pilots and visual review before the batch. | PENDING. |
| N6 | 2026-11-15 18:49 | Extend built streets, sidewalks and kerbs to the same refinement boundary; preserve existing near-site works and match their levels/materials. Actual road centre lines, inferred widths labelled, safe intersections and no overlap with building footprints/project lot. | PENDING. |
| N7 | 2026-11-15 18:49 | Separate immediate-neighbour review of 1525 and 1533 N Wieland: close street, lot-facing side and raised roof views; geometry/ground/lot-line checks; repair concrete faults on copies only. | PENDING. |
| N8 | 2026-11-15 19:16 | Owner explicitly requested a safe pause. Stop offline work and passive logger, restore temporary pilot visibility to the saved hybrid, save named working assets, confirm no render/camera/task remains, and commit a resume checkpoint. | PENDING. |

## Resume from the current state

- Editor remains open in L_Site_M4; no unsaved packages at 18:12. Earlier-local/updated-skyline hybrid is saved. The original L_R15_Production file still has its 2026-11-10 19:00:15 save time.
- Do not run old crash-recovery commands again: clean D1, profile and grazing checks are complete. Phase 20 stays IN PROGRESS because of the added nearby-detail scope.
- Owner approved inferred windows, trim and colours at 18:49, with assumptions recorded. Complete this work without requesting that approval again; keep the distinction from source-verified architecture.
- Active extension list: E:/Wieland1529_site_data/phase20/nearby_detail/active_targets.csv (682). Source records in review/phase20/nearby_detail/building_evidence.csv. Never activate historical project-lot objects ND_781075 or ND_781331.
- All 684 measured staging objects are hidden in L_Nearby_Detail. Meshes are in /Game/Wieland1529/Surroundings/NearbyDetail/Meshes. Their hidden state is intentional; full facade detail is not complete.
- Native helper nearby_detail_import.py validates geometry and writes import_records.jsonl. The new hybrid option is additive in LVS_W1529_Surroundings; do not use wieland_p17.build_surroundings_list(), which would replace the option list and lose the new combination.
- Once the facade approach is settled, finish the extension, remove visual overlaps through visibility only, refresh the hybrid option to cover the extension, and repeat views, grazing checks and profile for the actual final model. Only then render Grade Level, inspect it, render the other requested paths one at a time, make r3 and verify its Drive metadata. RENDER_REQUEST remains pending and r2 is not marked superseded.
- Owner 17:19 removed all memory guards. Do not reinstate thresholds or automatic cancellation. Passive logging and routine cleanup are permitted. Nanite ray tracing stays 0; no editor close/restart; named asset saves only; no Datasmith asset edits; no Google content.

## Review artifacts

Owner-readable interim report: D:/Unreal_Engine_Projects/Wieland1527 5.9/Saved/Wieland1529Review/RECOVERY_AND_NEARBY_DETAIL.md. Its companion FILES_WRITTEN.csv lists full absolute paths, sizes and SHA-256 hashes of authored artifacts and native files (incidental engine caches are excluded). Preview images are beside the report. The report makes clear that the facade extension, seven owner videos and r3 are unfinished.

The passive memory logger was stopped at 18:15; restart it for the resumed renders and profile. No memory guard is running. Current readback 19:01: L_Site_M4 open, only that working level dirty from temporary review cameras; no active render. Saved render settings remain Nanite mode 0, append 10000, cached-lighting pre-exposure 4.

## Order

1. Map coverage and supported detail.
2. Restore the geographically correct earlier buildings as a hybrid with the updated skyline, without overlaps.
3. Improve the remaining area to comparable supported detail, recording unknown details and source limitations per building.
4. Check street views, roof-deck views, grazing light, performance and memory; finish Phase 20 records.
5. Render the owner's requested paths and make verified r3 delivery.
