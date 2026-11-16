"""Phase 20 round 2: the owner's skyline sightline sheet against the model.

For each of the 27 landmarks of reference/skyline_landmarks_owner_sheet.csv:
  1. find its building among the Phase 17 skyline actors P17T_<county id> (by name in the Phase 17
     tower table where it is there, otherwise by footprint: the actors near the point at the sheet's
     bearing and distance, ranked by how well their height matches the sheet);
  2. measure from the model, from the D1 eye (-1300, -1560, 1684 cm):
       - main roof: downward traces on an 11 x 11 grid over the actor, the highest level that at least
         three traces land on (masts and small rooftop items are passed over);
       - bearing: to the centre of the traces that land within 15 m of that roof, as a true bearing
         (level north is -X, level east is -Y, level north is 1.18 degrees west of true north);
       - angles up to the main roof and to the tip (the mesh's highest point);
  3. trace sight lines from the eye to 12 points up the tower's centre line (ground to roof) and to the
     tip, naming the first thing in the way of each.
Run inside the editor:  g = {}; exec(compile(open(p).read(), p, 'exec'), g); g['RESULT']
Writes review/phase20/round2/landmarks.csv and landmarks.json.
"""
import csv
import json
import math
import os

import unreal

ROOT = r'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland'
SHEET = ROOT + '/reference/skyline_landmarks_owner_sheet.csv'
TOWER_TABLE = r'E:/Wieland1529_site_data/phase17/tower_materials.csv'
RECORDS = r'E:/Wieland1529_site_data/phase17/meshes_towers_clean/towers_record.jsonl'
OUT = ROOT + '/review/phase20/round2'

EYE = (-1300.0, -1560.0, 1684.0)          # D1, REFERENCE_VIEWS.md
TRUE_MINUS_LEVEL = -1.18                   # true bearing = level bearing - 1.18
FT = 30.48

# Landmarks whose county id the Phase 17 tower table names (supervisor's match, checked here by position).
BY_NAME = {
    '875 North Michigan Avenue (Hancock)': '824823',
    '900 North Michigan (Four Seasons)': '821343',
    'Waldorf Astoria Chicago': '821651',
    'One Chicago (East Tower)': '836153',
    'Aon Center': '869193',
    'Two Prudential Plaza': '869122',
    'Trump International Hotel & Tower': '859995',
    '330 North Wabash (AMA Plaza)': '861033',
    'Chase Tower': '881912',
    '300 North LaSalle': '862529',
    'Franklin Center': '886111',
    '311 South Wacker Drive': '894404',
    'Willis Tower': '889662',
    '110 North Wacker': '874616',
    'The St. Regis Chicago': '864656',
    'Salesforce Tower Chicago': '864465',
    '150 North Riverside': '869294',
    'Blue Cross Blue Shield Tower': '870704',
    # Found by footprint in round 2 (county outline and height, or OpenStreetMap for the four the 2022 survey
    # surface lacks); 835665 is Olympia Centre (Phase 17's name "ADA Building" was wrong: 736 ft at 737 N Michigan).
    'One Magnificent Mile': '817666',
    'Palmolive Building': 'osm143756601',
    'One Bennett Park': '852376',
    'Water Tower Place': '828186',
    'Olympia Centre': '835665',
    'Park Tower': 'osm686187393',
    'Aqua at Lakeshore East': '866027',
    'Lake Point Tower': 'osm150408224',
    'NEMA Chicago': 'osm1333503945',
}
NEAR_FIELD_CM = 3000.0   # hits this close to the eye are the deck's own structures (pergola, enclosure)


def _hidden(actor):
    try:
        if actor.is_temporarily_hidden_in_editor() or actor.is_hidden_ed():
            return True
    except Exception:
        pass
    try:
        return bool(actor.get_editor_property('hidden'))
    except Exception:
        return False


def level_from_bearing(bearing_true_deg, dist_cm):
    lb = math.radians(bearing_true_deg - TRUE_MINUS_LEVEL)
    north, east = dist_cm * math.cos(lb), dist_cm * math.sin(lb)
    return EYE[0] - north, EYE[1] - east


def bearing_true(x, y):
    dx, dy = x - EYE[0], y - EYE[1]
    lb = math.degrees(math.atan2(-dy, -dx)) % 360.0
    return (lb + TRUE_MINUS_LEVEL) % 360.0


def elev(z, dist_cm):
    return math.degrees(math.atan2(z - EYE[2], dist_cm))


def skyline_actors():
    out = {}
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith('P17T_') and isinstance(a, unreal.StaticMeshActor):
            o, e = a.get_actor_bounds(False)
            out[lab[5:]] = (a, o, e)
    return out


def roof_traces(actor, o, e, n=11):
    comp = actor.static_mesh_component
    top = o.z + e.z + 500.0
    bot = o.z - e.z - 500.0
    hits = []
    for i in range(n):
        for j in range(n):
            x = o.x - e.x + (i + 0.5) * 2.0 * e.x / n
            y = o.y - e.y + (j + 0.5) * 2.0 * e.y / n
            r = comp.line_trace_component(unreal.Vector(x, y, top), unreal.Vector(x, y, bot), True, False, False)
            # The editor's Python returns None when the trace misses, else the out values (location first).
            if r is None:
                continue
            loc = r[0] if isinstance(r[0], unreal.Vector) else r[1]
            hits.append((loc.x, loc.y, loc.z))
    if not hits:
        return None
    zs = sorted((h[2] for h in hits), reverse=True)
    roof = zs[0]
    for z in zs:
        if sum(1 for q in zs if z - 200.0 <= q <= z + 1.0) >= 3:
            roof = z
            break
    near = [h for h in hits if h[2] >= roof - 1500.0]
    cx = sum(h[0] for h in near) / len(near)
    cy = sum(h[1] for h in near) / len(near)
    return roof, cx, cy, len(hits)


DECK_HITS = {}


def first_obstacle(world, ignore, target_actor, end):
    """First visible thing beyond the deck's own structures on the line from the eye to end, or None when the
    line reaches the target. Hidden objects (stand-ins not drawn) are passed over; hits within NEAR_FIELD_CM of
    the eye (the pergola and roof enclosure around D1) are counted in DECK_HITS and passed over."""
    hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(*EYE), unreal.Vector(*end),
                                                 unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore,
                                                 unreal.DrawDebugTrace.NONE, True)
    for h in hits or []:
        t = h.to_tuple()
        actor, comp, loc = t[9], t[10], t[4]
        if actor == target_actor:
            return None
        # The option switch hides the earlier massing (SB_*) and the far-city stand-in by making their
        # components invisible; they still collide, so they are passed over here.
        if (actor is not None and _hidden(actor)) or (comp is not None and not comp.is_visible()):
            continue
        dist = math.dist(EYE, (loc.x, loc.y, loc.z))
        if dist < NEAR_FIELD_CM:
            key = actor.get_actor_label() if actor else 'unknown'
            DECK_HITS[key] = DECK_HITS.get(key, 0) + 1
            continue
        return (actor.get_actor_label() if actor else 'unknown', round(loc.x), round(loc.y), round(loc.z),
                round(dist / 100.0, 1))
    return None


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sheet = list(csv.DictReader(open(SHEET, encoding='utf-8')))
    names = {r['bldg_id']: r['name'] for r in csv.DictReader(open(TOWER_TABLE, encoding='utf-8'))}
    recs = {}
    for path in (RECORDS, os.path.dirname(RECORDS) + '/osm_assumption_record.jsonl'):
        for line in open(path, encoding='utf-8'):
            r = json.loads(line)
            recs[str(r['id'])] = r
    DECK_HITS.clear()
    actors = skyline_actors()
    try:
        import wieland_interiors as wi
        stand_ins = set(wi.REVIT_STAND_INS)
    except Exception:
        stand_ins = set()
    ignore = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
              if a.get_actor_label() in stand_ins]

    rows = []
    for s in sheet:
        name = s['landmark']
        b_sheet = float(s['azimuth_deg_true'])
        d_sheet_cm = float(s['distance_ft']) * FT
        roof_ft = float(s['roof_ft'])
        tip_ft = float(s['tip_ft']) if s['tip_ft'] else None
        ex, ey = level_from_bearing(b_sheet, d_sheet_cm)
        # Candidates by footprint: actors whose centre is near the sheet's point, ranked by height match.
        radius = max(30000.0, 0.08 * d_sheet_cm)
        cands = []
        for cid, (a, o, e) in actors.items():
            dxy = math.hypot(o.x - ex, o.y - ey)
            if dxy <= radius:
                rec = recs.get(cid, {})
                top_m = rec.get('top_incl_masts_m', (o.z + e.z) / 100.0)
                roof_m = rec.get('roof_top_m', top_m)
                score = abs(roof_m * 3.28084 - roof_ft) / max(roof_ft, 1.0) + dxy / radius * 0.5
                cands.append((score, cid, round(dxy / 100.0), round(roof_m * 3.28084), names.get(cid, '')))
        cands.sort()
        if name in BY_NAME:
            cid, how = BY_NAME[name], 'name in the Phase 17 tower table'
        elif cands:
            cid, how = cands[0][1], 'footprint at the sheet bearing and distance'
        else:
            cid, how = None, 'not found'
        row = {'no': s['no'], 'landmark': name, 'sheet_bearing': b_sheet, 'sheet_dist_ft': float(s['distance_ft']),
               'sheet_roof_ft': roof_ft, 'sheet_tip_ft': tip_ft or '',
               'sheet_elev_roof': float(s['elev_52ft_roof_deg']),
               'sheet_elev_tip': float(s['elev_52ft_tip_deg']) if s['elev_52ft_tip_deg'] else '',
               'county_id': cid or '', 'found_by': how, 'phase17_name': names.get(cid, '') if cid else '',
               'candidates': '; '.join('%s %s m off, roof %s ft %s' % (c[1], c[2], c[3], c[4]) for c in cands[:3])}
        if cid and cid in actors:
            a, o, e = actors[cid]
            rt = roof_traces(a, o, e)
            rec = recs.get(cid, {})
            tip_z = o.z + e.z
            if rt:
                roof_z, cx, cy, nh = rt
            else:
                roof_z, cx, cy, nh = tip_z, o.x, o.y, 0
            dist = math.hypot(cx - EYE[0], cy - EYE[1])
            mb = bearing_true(cx, cy)
            db = (mb - b_sheet + 180.0) % 360.0 - 180.0
            er, et = elev(roof_z, dist), elev(tip_z, dist)
            # sight lines up the centre line and to the tip
            ground_z = o.z - e.z
            seen, blockers = 0, {}
            for k in range(12):
                z = ground_z + (roof_z - ground_z) * (k + 0.5) / 12.0
                ob = first_obstacle(world, ignore, a, (cx, cy, z))
                if ob is None:
                    seen += 1
                else:
                    blockers[ob[0]] = blockers.get(ob[0], 0) + 1
            ob_roof = first_obstacle(world, ignore, a, (cx, cy, roof_z - 100.0))
            ob_tip = first_obstacle(world, ignore, a, (cx, cy, tip_z - 50.0)) if tip_z > roof_z + 300.0 else None
            sheet_e_tip = row['sheet_elev_tip'] if row['sheet_elev_tip'] != '' else row['sheet_elev_roof']
            row.update({
                'model_bearing': round(mb, 2), 'd_bearing': round(db, 2), 'model_dist_ft': round(dist / FT),
                'model_roof_ft_above_ground': round(rec.get('roof_top_m', 0) * 3.28084) if rec else '',
                'model_tip_ft_above_ground': round(rec.get('top_incl_masts_m', 0) * 3.28084) if rec else '',
                'model_roof_z_cm': round(roof_z), 'model_tip_z_cm': round(tip_z),
                'roof_cx_cm': round(cx), 'roof_cy_cm': round(cy),
                'model_elev_roof': round(er, 2), 'd_elev_roof': round(er - row['sheet_elev_roof'], 2),
                'model_elev_tip': round(et, 2), 'd_elev_tip': round(et - float(sheet_e_tip), 2),
                'roof_traces': nh,
                'centre_line_seen_of_12': seen,
                'centre_line_blockers': '; '.join('%s x%d' % kv for kv in sorted(blockers.items(), key=lambda kv: -kv[1])),
                'roof_sight': 'clear' if ob_roof is None else 'blocked by %s at %s m' % (ob_roof[0], ob_roof[4]),
                'tip_sight': '' if tip_z <= roof_z + 300.0 else ('clear' if ob_tip is None else 'blocked by %s at %s m' % (ob_tip[0], ob_tip[4])),
            })
        rows.append(row)
    os.makedirs(OUT, exist_ok=True)
    cols = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(OUT + '/landmarks.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open(OUT + '/landmarks.json', 'w', encoding='utf-8'), indent=1)
    return rows


ROWS = main()
RESULT = '\n'.join('%s %s | %s | b %s (%s) | roof %s (%s) | tip %s (%s) | seen %s/12 %s | roof %s | tip %s' % (
    r['no'], r['landmark'][:22], r['county_id'], r.get('model_bearing'), r.get('d_bearing'),
    r.get('model_elev_roof'), r.get('d_elev_roof'), r.get('model_elev_tip'), r.get('d_elev_tip'),
    r.get('centre_line_seen_of_12'), r.get('centre_line_blockers', '')[:50], r.get('roof_sight', '')[:45],
    r.get('tip_sight', '')[:35]) for r in ROWS) + '\nDECK HITS: ' + str(DECK_HITS)
