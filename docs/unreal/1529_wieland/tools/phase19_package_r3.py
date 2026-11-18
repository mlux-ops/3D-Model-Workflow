"""Delivery revision r3 (2026-11-15): the owner's walking-path videos, the Phase 20 round-2 stills and panoramas,
and updated notes, on D: and on Google Drive, checked by size and SHA-256; r2 marked superseded in both places.

Usage: python -B phase19_package_r3.py [--dry-run]

Uses tools/phase19_package.py (copy, manifest, Drive read-back, no overwrite, no deletion) with this revision's
file list and superseded note.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase19_package as P  # noqa: E402
from wieland_paths import safe_name

NAME = "1529_Wieland_UE5.9_Delivery_2026-11-15_r3"
P.EARLIER = "1529_Wieland_UE5.9_Delivery_2026-11-14_r2"
DOCS = P.DOCS
R2 = DOCS + "/review/phase20/round2"
MEDIA = DOCS + "/review/phase20/final_extension"


def files():
    out = [(DOCS + "/delivery/DELIVERY_NOTES_2026-11-15_r3.md", "DELIVERY_NOTES.md"),
           (DOCS + "/owner_review/paths/RENDER_HOW.md", "RENDER_HOW.md"),
           (P.D_ROOT + "/" + P.EARLIER + "/LICENCES.csv", "LICENCES.csv"),
           (R2 + "/landmarks.csv", "skyline/landmarks_sheet_vs_model.csv")]
    for v in P.VIEWS:
        out.append((MEDIA + "/stills/%s_realtime.0000.png" % v, "stills/%s_realtime.png" % v))
        out.append((MEDIA + "/stills/compare_%s_realtime.jpg" % v, "comparison/r2_vs_r3_%s.jpg" % v))
    out.append((MEDIA + "/stills/D1_pathtraced.0000.png", "stills/D1_pathtraced.png"))
    out.append((MEDIA + "/stills/compare_D1_pathtraced.jpg", "comparison/r2_vs_r3_D1_pathtraced.jpg"))
    for deck in ("D1S", "D1"):
        out.append((MEDIA + "/panorama/%s_panorama_sheet_r2.png" % deck, "skyline/%s_skyline_27_landmarks.png" % deck))
        out.append((MEDIA + "/panorama/%s_panorama_sheet_r2_labels.json" % deck, "skyline/%s_skyline_labels.json" % deck))
        out.append((MEDIA + "/panorama/%s_landmark_crops_r2.png" % deck, "skyline/%s_landmark_closeups.png" % deck))
        out.append((MEDIA + "/panorama/compare_%s_r1_r2.jpg" % deck, "comparison/skyline_r2_vs_r3_%s.jpg" % deck))
    result_file=DOCS+'/delivery/owner_videos_result.json'
    with open(result_file,encoding='utf-8') as stream:results=json.load(stream)
    out.append((result_file,'video_paths/RENDER_RESULTS.json'))
    for result in results['results']:
        name=result['name']
        if name not in results['requested_names'] or name.startswith('_test_'):raise RuntimeError('Unexpected video '+name)
        if result.get('refused'):continue
        filename=safe_name(name)
        for extension in ('.mp4','.json'):
            f=DOCS+'/delivery/video_paths/'+filename+extension
            out.append((f,'video_paths/'+filename+extension))
    return out


def superseded_note(folder, name):
    receipt=DOCS+'/delivery/r3_drive_verified.json'
    if not os.path.exists(receipt):return 'pending cloud metadata verification'
    with open(receipt,encoding='utf-8') as stream:verified=json.load(stream)
    if verified.get('package')!=name or verified.get('verified') is not True:return 'pending cloud metadata verification'
    path = folder + "/SUPERSEDED.md"
    if os.path.exists(path):
        return "kept"
    text = ("# Superseded\n\nThis package (%s) is superseded by **%s** (same folder level), made on 2026-11-15.\n\n"
            "What the newer revision replaces: the stills of every station and design view and the skyline sheets (Phase 20 "
            "round 2: all 27 landmarks of the owner's sightline sheet present and labelled, nine of them added, the John "
            "Hancock Center rebuilt with its taper and cross-bracing, landmark materials from photographs), and it adds the "
            "owner's seven walking-path videos.\n\nWhat stays valid here: the test video and its record, and the notes on "
            "the path tool. The packaged build and the 60-second animation stay in the 2026-11-14 package and show the "
            "earlier surroundings.\n\nNothing in this folder was changed or deleted; only this note was added.\n" % (P.EARLIER, name))
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(text)
    return "written"


P.files = files
P.superseded_note = superseded_note

if __name__ == "__main__":
    sys.exit(P.main([sys.argv[0], NAME] + sys.argv[1:]))
