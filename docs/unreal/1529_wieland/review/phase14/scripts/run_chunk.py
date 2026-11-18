import sys, json, importlib, time, os, asyncio
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase14/scripts")
import p14
importlib.reload(p14)
unreal = p14.unreal
job = json.load(open(p14.OUT + "/scripts/job.json"))
deck, day = job["deck"], job["day"]
folder = "%s/%s_%s" % (p14.FRAMES, deck, day)
times = p14.sun_times(day)
meta = {"deck": deck, "day": day, "camera": p14.DECKS[deck], "date": p14.DAYS[day], "sun_times_hours": times, "frames": 240}
os.makedirs(folder, exist_ok=True)
json.dump(meta, open(folder + "/meta.json", "w"), indent=1)
p14.wl.window_restore()
p14.snapshot_state()
unreal.SystemLibrary.execute_console_command(p14.wl.world(), "viewmode lit")
p14.camera(deck)
t0 = time.time()
first = job["start"]
hour0 = times["sunrise"] + first * (times["sunset"] - times["sunrise"]) / 239.0
s0 = p14.set_sun(day, hour0)
p14.set_ev(p14.ev_for(s0["height"]))
await asyncio.sleep(job.get("presettle", 6.0))
done, skipped, rows = 0, 0, []
for i in range(job["start"], min(240, job["start"] + job["count"])):
    path = "%s/f%03d.png" % (folder, i)
    hour = times["sunrise"] + i * (times["sunset"] - times["sunrise"]) / 239.0
    s = p14.set_sun(day, hour)
    ev = p14.ev_for(s["height"])
    p14.set_ev(ev)
    if os.path.exists(path) and os.path.getsize(path) > 10000 and not job.get("redo"):
        skipped += 1
        continue
    ok = await p14.shoot(path, settle=job.get("settle", 1.0))
    done += 1
    rows.append([i, round(hour, 4), round(s["bearing"], 2), round(s["height"], 2), round(ev, 2), ok])
log = folder + "/frames_log.jsonl"
with open(log, "a") as handle:
    for r in rows:
        handle.write(json.dumps(r) + "\n")
json.dumps({"done": done, "skipped": skipped, "seconds": round(time.time() - t0, 1), "times": times, "last": rows[-1] if rows else None})
