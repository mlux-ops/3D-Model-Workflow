Status: DONE at 15:09 on 2026-11-13. Four 10-second timelapse videos (240 frames, 1920 by 1080, 24 frames a second, H.264) are made and play without errors; the sun and the exposure are back at the plan's review condition and read back. Nothing is saved in the project and nothing is pushed.

# Phase 14 results: sun-path timelapse videos from the two decks

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9), level `/Game/Wieland1529/L_Site_M4`. Each video follows the sun evenly from sunrise to sunset on one day, from one fixed camera, with the proposed hotel at 1520-1528 N. Wells switched on (Variant Manager list `Neighbour development`, option "Duke of Wells (proposed)"; read back as 56 hotel objects shown and the 3 existing objects hidden). The pictures come from the real-time renderer, not the Path Tracer, and picture quality is the editor's own, not polished.

## The four files

| Video | Deck | Day | Full path |
|---|---|---|---|
| 1 | Penthouse roof deck | 21 June 2026 | `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase14\timelapse_roofdeck_summer.mp4` |
| 2 | Penthouse roof deck | 21 December 2026 | `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase14\timelapse_roofdeck_winter.mp4` |
| 3 | Rear patio deck (ground level) | 21 June 2026 | `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase14\timelapse_reardeck_summer.mp4` |
| 4 | Rear patio deck (ground level) | 21 December 2026 | `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase14\timelapse_reardeck_winter.mp4` |

Checked with `ffprobe` and a full decode with `ffmpeg` (no messages means no errors): each file is H.264, 1920 by 1080, 24 frames a second, 240 frames, 10.0 seconds. Each frame has a small caption in the bottom-left corner: deck, date, clock time with CDT (daylight time) or CST (standard time), and "proposed hotel shown". The clock time on the caption is the time of that frame, so the clock runs faster than real time and evenly from sunrise (frame 1) to sunset (frame 240).

## Sun: times used

The sun is the project's own sun light `LGT_Sun`, turned for each frame from the Sun Position plugin's calculation (latitude 41.910215, longitude -87.635389, time zone -6 hours, daylight saving on for June and off for December), with the project's north offset applied exactly as in Phase 8 (level yaw = bearing - 178.82). Sunrise and sunset are the plugin's own results.

| Day | Clock | Sunrise | Solar noon | Sunset | Highest sun | Sun bearing at sunrise / sunset |
|---|---|---|---|---|---|---|
| 21 June 2026 | CDT | 05:15:26 | 12:52:22 | 20:29:17 | 71.5 degrees | 57 / 303 degrees |
| 21 December 2026 | CST | 07:14:57 | 11:48:37 | 16:22:18 | 24.7 degrees | 121 / 239 degrees |

Frame number i (0 to 239) is taken at sunrise + i x (sunset - sunrise) / 239, so the first frame is at sunrise and the last at sunset. Every frame's clock time, sun bearing, sun height and exposure are in `review\phase14\frames\<deck>_<day>\frames_log.jsonl`. Frames f000 to f011 of the winter roof deck were taken again at the end (the first ones were a little washed out because the sky light had not caught up), so every log has exactly one line per frame.

## Cameras

All four use one fixed camera per deck, the same for summer and winter: eye height 1.6 m above the floor, 100 degrees across (a 16 to 9 picture, so about 68 degrees up and down), turned due south (yaw 1.18 degrees in the level's axes). Positions are in level centimetres (+X is south, -Y is east; the street, Wieland, is at +Y).

| Deck | Position X, Y, Z (cm) | Pitch up | Sees from floor to sky |
|---|---|---|---|
| Penthouse roof deck | -1300, -2150, 1684 | 15 degrees | about 19 degrees below the horizon to 49 degrees above |
| Rear patio deck | -1370, -2800, 363 | 18 degrees | about 16 degrees below to 52 degrees above |

- **Roof deck.** D1's camera (`REFERENCE_VIEWS.md`: -1300, -1560, 1684) stands right under the pergola, which would hide the sky. The camera here keeps D1's X and height and moves 5.9 m east along the deck to an open spot (an upward line test from this point hits nothing). It looks south along the deck, over the planters, sofas and glass guard, with the pergola at the right edge and the hotel tower at the left.
- **Rear deck: which one and why.** The building has two outdoor places at the rear. (1) The 4th-floor rear terrace (floor about 11.8 m, in the Phase 8 level named `SV_W1529_Outdoor_RearTerrace`) is not usable for this job: it sits under the penthouse roof-deck slab, with a ceiling, a ceiling fan, side walls and lights (three trial pictures confirm it), so direct sun never reaches it. (2) The ground-level rear patio of the north triplex (glass guard, pergola, dining table, stair; the patio of D5) is open to the sky through the pergola slats. I used (2). Its camera stands at the patio's north end and looks south over the patio floor, the glass guard, the stair, the pergola and the tower beyond. The patio is a narrow slot between the building's own wall and the neighbour's wall, so only a strip of sky shows between the pergola beams.
- **What the frame cannot hold.** In June the sun disc is never in the picture on either deck: in the hours when it is within the 100-degree width (south-east to south-west) it is already higher than the top edge (about 49 to 52 degrees up), and before and after that it is far to the north-east or north-west. The June sun's path is read from the moving shadows. In December (sun never above 24.7 degrees, bearing 121 to 239) the sun disc is in the roof deck picture from 08:03 to 15:34 CST and leaves at the right edge. On the rear deck the sun is geometrically in view for about the same hours, but the walls and pergola hide it, so there only the light and shadows move.

## Brightness (exposure) method

The project's daylight exposure is fixed at EV 14.644 (ISO 100, f/8, 1/400 second), which makes dawn and dusk nearly black. For these videos only, the exposure was stepped with the height of the sun, in the outdoor exposure volume `LGT_Exposure_Outdoors`, still as a fixed (manual) camera setting each frame, not automatic exposure. The value for each frame was worked out from the sun's height and joined between these points:

| Sun height (degrees) | -5 or lower | 0 | 5 | 10 | 15 | 25 or higher |
|---|---|---|---|---|---|---|
| Exposure value (EV) | 6.0 | 7.5 | 10.0 | 12.0 | 13.2 | 14.644 (the project's fixed value) |

I chose a stepped value instead of automatic exposure because automatic exposure needs time to adapt, which a few settling ticks do not give, and it measures the bright sky. The steps were chosen by looking at dawn frames (the first trial at sunrise was washed out only because the sky light had not caught up after the jump from noon; a 6-second pause before each chunk fixed that). Consequences you can see: the frames at dawn and dusk are readable, the sky is bright and the building dark when the sun is low, and brightness from frame to frame follows the sun, not a real camera. Above 25 degrees the exposure is the same as the project's, so the summer midday frames show the real daylight look.

The other two exposure volumes (the room volumes, EV 9.0) were not touched; none of the cameras is inside them.

## What the videos show

(Measured on a patch of deck floor in each frame, scaled back by that frame's exposure, so that it can be compared across the day; the patch is small and the clock times are good to about 5 minutes. Hotel on and hotel off were compared at three clock times, with the same camera and the same sun, by switching the Variant Manager option and switching it back.)

- **Roof deck, December.** The deck floor is in shade from sunrise until 11:31 to 11:34 CST. At 10:30 CST a hotel-off picture shows the deck in full sun and the same picture with the hotel on shows it in shadow (the floor patch is 2.4 times brighter without the hotel), so the shadow at that time is the hotel tower's (compared with the hotel off at 10:30 only; the rest of the morning was not compared, but the shade leaves the deck at 11:31 in step with the sun moving past the tower). From about 11:33 the sun reaches the floor and stays on it until sunset (low and weak at the end). The sun disc crosses the picture from left to right between 08:03 and 15:34 and then leaves at the right edge.
- **Roof deck, June.** The floor is in direct sun from about 06:30 to 18:30 CDT, lit all day apart from the first and last hour (the floor patch is 1,100 units at 06:17 and 7,300 at 10:20); the floor patch never drops suddenly (no shadow edge sweeps over it); I did not run a hotel-off comparison for the June roof deck. 
- **Rear deck, June.** The patch of patio floor is dark until about 08:50 CDT, in direct sun from 08:50 to about 14:15 CDT (peak around 12:30), and back in shade from about 14:15 until sunset. The hotel is not the main cause of the shade here: with the hotel off the same floor patch is only 1.2 times brighter at 08:00 and at 14:45 CDT. The building's own wall, the neighbour's wall and the pergola make the shade. At sunset the hotel tower's upper floors glow orange in the evening sun, at the top of the picture.
- **Rear deck, December.** Direct sun never reaches the patio floor on 21 December. Its brightest reading in the day is 76 units, against 2,784 on 21 June, a factor of 36 lower, and it hardly changes between 08:30 and 14:30 CST. The video shows a patio in even shade all day.

## Scene state and what was put back

- Scene as it stood at the start: top level `/Game/Wieland1529/L_Site_M4`, 12 sub-levels loaded, hotel option proposed (56 of 56 hotel objects shown, 0 of 3 existing objects shown), `r.RayTracing.Nanite.Mode` 0 (read at the start, after every run and at the end).
- Put back and read back after the last run: sun 241.72 degrees bearing, 46.40 degrees height (the 15 August 2026, 15:30 CDT review condition; the same values as before the job); `LGT_Exposure_Outdoors` manual, EV 14.644 (ISO 100, f/8, 1/400.04 s); the two room volumes manual, EV 9.0; the temporary camera is removed and the viewport is released from it.
- One more temporary setting: the viewport's view-distance quality (`sg.ViewDistanceQuality`) was set to 3 in a trial; every other quality group (shadows, global illumination, reflections, post-processing, textures, effects, foliage) also reads 3, so this was already the editor's level and nothing needed putting back.
- Not saved: no level, no asset and no setting was saved (no "Save All"; `L_R15_Production` untouched). The editor therefore still marks `L_Site_M4`, `L_ProposedHotel`, `L_Light_SummerAfternoon`, `L_Surroundings_R15` and `L_Surroundings` as changed; their values are back to what they were (the hotel option switching and the sun and exposure changes are what mark them). Leave them unsaved; closing the editor and answering "do not save" drops the marks.
- Memory: free commit memory was 21.7 GB at the start (limit 79.1 GB; editor 23.7 GB), under the 30 GB rule, so the editor was closed (it came back at 47.3 GB free) and reopened on the same level; after the job it reads 29.4 GB free.

## Errors and how they were handled

Logged in `PROJECT_MEMORY.md`, section "Phase 14: sun-path timelapse videos":

1. The editor-closing call answered "Canceled" because the agent server stops with the editor; expected, nothing to fix.
2. **Two copies of the shooting script ran at the same time** for three of the videos (I started the second without noticing that the first, started in the background, was still running). They overwrote the same files, three first MP4 files did not decode, and the frames of those three days could not be trusted. Fix: those frame folders were renamed `*_suspect_doublerun` (nothing deleted), the three MP4 files moved to `review\phase14\suspect\`, and the three days were shot again from scratch with one copy running. The four final files above all decode with no errors and every frame log has exactly one line per frame. The roof deck in December had been shot before the second copy started, so it is from the first run, except that its first 12 frames (f000 to f011) were shot again and the video re-made.

## Where everything is

All under `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase14\`:

- The four videos (above).
- `frames\<deck>_<day>\f000.png` to `f239.png` (the raw 1920 by 1080 pictures), with `meta.json` and `frames_log.jsonl`; `frames\<deck>_<day>_cap\` holds the captioned pictures the videos are made from. Not committed. About 4.7 GB.
- `frames\test\` holds the trial pictures (camera choices, the 4th-floor terrace, the hotel on and off); `frames\*_suspect_doublerun\` and `suspect\` hold the discarded first attempt of three days.
- `start_state.json` holds the sun and exposure values read at the start.
- `scripts\`: `p14.py` (the sun, exposure, camera and picture steps, run inside the editor), `run_chunk.py` (one chunk of 80 frames), `run_all.sh` (shoots, captions and encodes the other three videos in chunks of 80 frames; run it once at a time), `make_video.py` (caption and join with ffmpeg), `restore.py` (puts the sun and exposure back and reads them), `sun_on_floor.py` (the floor-brightness check), `hotel_check.py` (hotel on and off), and the probe and trial scripts `probe*.py`, `find_decks*.py`, `t1.py` to `t3.py` (`t3.py` reads `t3_jobs.json`, committed with it).
- ffmpeg was already installed on this machine (a winget package); nothing was installed.
