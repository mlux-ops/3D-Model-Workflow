"""Phase 20 round 2: photographs to instance settings, and the round-2 building table.

SETTINGS holds, per building, the instance, the settings judged from the round-2 observations
(review/phase20/round2/*observations*.json, landmark_obs_A/B.json), the confidence and what the photographs show.
Colours are sRGB 0-255 as judged on lit facade areas: stone and metal as sampled; glass keeps the sampled hue
but is darkened (largest channel 62) to a glass base colour, because a photograph's glass carries the sky's
reflection, which the engine adds itself. Converted to linear and clamped 0.02-0.80 as in round 1.

Run inside the editor (applies and saves by name, writes the tables):
    g = {'__name__': 'mat'}; exec(compile(open(p).read(), p, 'exec'), g); g['RESULT']
Outside the editor (`python -B phase20r2_materials.py --tables`) it only writes the tables.
"""
import csv
import json
import os
import sys

ROOT = r'E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland'
R2 = ROOT + '/review/phase20/round2'


def glass(rgb, top=62.0):
    m = max(rgb)
    return tuple(round(c * top / m) for c in rgb)


def lin(c):
    c = c / 255.0
    v = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return round(min(max(v, 0.02), 0.80), 4)


# id: (instance suffix, settings, confidence before, confidence after, what the photographs show, observation key)
SETTINGS = {
    '859995': ('859995', {'GlassColor': (45, 58, 72), 'FrameColor': (175, 180, 185), 'FloorHeight': 3.6, 'BayWidth': 1.5, 'FrameWidth': 0.12},
               2, 3, 'silver-blue reflective curtain wall with stainless mullions; spire above the setback roof (in the scan)', 'B17'),
    '861033': ('861033', {'GlassColor': glass((79, 97, 111)), 'FrameColor': (28, 26, 24), 'FloorHeight': 4.1, 'BayWidth': 1.52, 'FrameWidth': 0.15},
               2, 3, 'dark bronze-black glass and mullions (Mies), flat roof', 'B18'),
    'osm1333503945': ('osm1333503945', {'GlassColor': glass((20, 83, 113)), 'FrameColor': (110, 120, 125), 'FloorHeight': 3.4, 'BayWidth': 1.5, 'FrameWidth': 0.1},
                      1, 3, 'blue-green reflective glass, stepped stacked blocks (height an assumption: not in the 2022 survey)', 'B19'),
    '881912': ('881912', {'FrameColor': (202, 198, 197), 'GlassColor': glass((85, 89, 111)), 'FloorHeight': 4.3, 'BayWidth': 1.5, 'FrameWidth': 0.6, 'SpandrelHeight': 1.0},
               2, 4, 'light granite piers, dark bronze recessed glass in bands', 'T881912'),
    '862529': ('862529', {'GlassColor': glass((141, 160, 175)), 'FrameColor': (190, 196, 198), 'FloorHeight': 4.0, 'BayWidth': 1.5, 'FrameWidth': 0.1},
               1, 4, 'pale blue-grey curtain wall with fine light mullions, stepped notched crown', 'T862529'),
    '886111': ('886111', {'FrameColor': (140, 130, 120), 'GlassColor': (35, 38, 42), 'FloorHeight': 4.5, 'FrameWidth': 0.7, 'BayWidth': 1.6, 'SpandrelHeight': 1.1},
               2, 3, 'taupe stone piers with punched glass, stepped crown with pinnacles (in the scan)', 'T886111'),
    '894404': ('894404', {'FrameColor': (125, 105, 96), 'GlassColor': (35, 38, 40), 'FloorHeight': 4.5, 'FrameWidth': 0.7, 'BayWidth': 1.6, 'SpandrelHeight': 1.1},
               2, 3, 'brown-red granite piers and dark glass, lit cylindrical glass crown (in the scan)', 'B23'),
    '874616': ('874616', {'GlassColor': glass((8, 90, 148)), 'FrameColor': (165, 170, 175), 'FloorHeight': 4.5, 'BayWidth': 1.5, 'FrameWidth': 0.12},
               2, 4, 'blue reflective curtain wall, light stepped setback blocks at the top', 'B26'),
    '821343': ('821343', {'FrameColor': (211, 198, 174), 'GlassColor': (35, 40, 45), 'FloorHeight': 4.0, 'FrameWidth': 0.7, 'BayWidth': 1.6, 'SpandrelHeight': 1.1},
               2, 3, 'cream stone with punched windows, turret pinnacles', 'A7'),
    '864656': ('864656', {'GlassColor': (18, 40, 46), 'FrameColor': (60, 75, 80), 'FloorHeight': 3.6, 'BayWidth': 1.5, 'FrameWidth': 0.08},
               2, 3, 'dark blue-green glass with fine verticals, three stacked tapering sections', 'A10'),
    '866027': ('866027', {'FrameColor': (215, 215, 210), 'GlassColor': (40, 60, 68), 'FloorHeight': 3.19, 'BayWidth': 3.0, 'FrameWidth': 0.05, 'SpandrelHeight': 0.6},
               1, 3, 'white undulating balcony slabs over glass; drawn as light slab bands (the facade material has no wave)', 'A12'),
    'osm686187393': ('osm686187393', {'FrameColor': (190, 186, 178), 'GlassColor': (35, 48, 58), 'FloorHeight': 3.84, 'FrameWidth': 0.4, 'BayWidth': 1.6},
                     1, 2, 'glass tower with curved balcony bands beside the Water Tower (height an assumption: not in the 2022 survey)', 'A9'),
    'osm150408224': ('osm150408224', {'GlassColor': (30, 32, 28), 'FrameColor': (77, 81, 67), 'FloorHeight': 2.81, 'BayWidth': 1.5, 'FrameWidth': 0.12},
                     1, 2, 'curved three-lobed tower, dark bronze glass in banded floors (height an assumption: not in the 2022 survey)', 'A1'),
    '821196': ('821196', {'FrameColor': (200, 190, 170), 'GlassColor': (35, 38, 40), 'FloorHeight': 4.65, 'FrameWidth': 0.8, 'BayWidth': 1.6, 'SpandrelHeight': 1.2},
               1, 2, 'limestone setback tower (old postcards only); beacon mast', 'A3'),
    'osm143756601': ('osm143756601', {'FrameColor': (200, 190, 170), 'GlassColor': (35, 38, 40), 'FloorHeight': 4.65, 'FrameWidth': 0.8, 'BayWidth': 1.6, 'SpandrelHeight': 1.2},
                     1, 2, 'limestone setback tower (old postcards only); beacon mast (tower height an assumption)', 'A3'),
    '828186': ('828186', {'FrameColor': (210, 208, 200), 'GlassColor': (35, 38, 42), 'FloorHeight': 3.54, 'FrameWidth': 0.9, 'BayWidth': 1.8},
               1, 3, 'white marble tower with narrow windows, stepped top', 'A6'),
    '828450': ('828450', {'FrameColor': (210, 208, 200), 'GlassColor': (35, 38, 42), 'FloorHeight': 3.54, 'FrameWidth': 0.9, 'BayWidth': 1.8},
               1, 3, 'white marble (part of Water Tower Place)', 'A6'),
    '884598': ('884598', {'FrameColor': (171, 158, 124), 'GlassColor': (35, 38, 42), 'FloorHeight': 4.06, 'FrameWidth': 0.7, 'BayWidth': 1.6, 'SpandrelHeight': 1.1},
               1, 3, 'warm beige stone piers, punched grid, pinnacled crown', 'T884598'),
    '861253': ('861253', {'FrameColor': (152, 149, 141), 'GlassColor': (35, 38, 42), 'FrameWidth': 0.06, 'SpandrelHeight': 1.3},
               2, 2, 'beige horizontal ribbon face (River North Point, the former Apparel Center)', 'T861253'),
}
# Identified but nothing set (confidence noted): (id, confidence before, after, what is seen)
SEEN_ONLY = {
    '835665': (1, 2, 'Olympia Centre (Phase 17 called it "ADA Building"): a light banded mass beside Hancock; not measured'),
    '852376': (1, 2, 'One Bennett Park: two reviewers disagree (stone with punched windows / tinted glass); kept as built in J13'),
    '817666': (1, 1, 'One Magnificent Mile: no photograph identifies it; kept as built in J13'),
    '870704': (2, 2, 'Blue Cross Blue Shield: probable pale grey punched grid, assigned by position only'),
    '869122': (4, 4, 'Two Prudential Plaza: round-1 colours stand; the peaked crown with its spire shown (spire added as a built element)'),
    '889662': (4, 4, 'Willis Tower: round-1 colours stand; two antennas and stepped tubes are in the scan'),
    '836153': (4, 4, 'One Chicago: round-1 colours stand'),
}
ZONE = {
    # zone id: (settings or None, confidence before, after, what is seen)
    '779596': ({'BayWidth': 1.0, 'FloorHeight': 1.0, 'FrameWidth': 0.25, 'SpandrelHeight': 0.25, 'WindowPattern': 1.0},
               1, 2, 'Up Down Cigar, 1550 N Wells: upper wall a deep-recessed square-cell precast grid (2006 night photograph); colour not seen'),
    '779924': (None, 1, 1, 'Zanies, 1548 N Wells: lit marquee only (2006 night photograph); wall not seen'),
    '779308': (None, 2, 2, '1552 N Wells: cream awning (2006 night photograph); wall lamp-lit, not used'),
    '777736': (None, 1, 1, 'Old Town Ale House, 219 W North: ground-floor storefront dark sage-green (2007); upper facade not seen'),
}


def load_obs():
    out = {}
    a = json.load(open(R2 + '/landmark_obs_A.json', encoding='utf-8'))
    b = json.load(open(R2 + '/landmark_obs_B.json', encoding='utf-8'))
    t = json.load(open(R2 + '/tower_observations.json', encoding='utf-8'))['towers']
    z = json.load(open(R2 + '/zone12_observations.json', encoding='utf-8'))['buildings']
    for k, v in a.items():
        out['A' + k] = v
    for k, v in b.items():
        out['B' + k] = v
    for k, v in t.items():
        out['T' + k] = v
    for k, v in z.items():
        out['Z' + k] = v
    return out


def params_of(settings):
    p = {}
    for k, v in settings.items():
        p[k] = [lin(c) for c in v] if isinstance(v, tuple) else float(v)
    return p


def tables():
    obs = load_obs()
    rows, params, used = [], {}, []
    for bid, (suffix, sets, c0, c1, shows, key) in SETTINGS.items():
        mi = 'MI_P17_T_' + suffix
        params[mi] = params_of(sets)
        files = obs.get(key, {}).get('files') or []
        used += [(bid, f) for f in files]
        rows.append({'group': 'skyline/landmark', 'county_id': bid, 'instance': mi, 'what_they_show': shows,
                     'photographs': ' | '.join('%s (%s, %s, %s)' % (f.get('title', ''), f.get('licence', ''), f.get('author', ''), f.get('page_url', '')) for f in files),
                     'settings_changed': json.dumps(params[mi]), 'confidence_before': c0, 'confidence_after': c1})
    for bid, (c0, c1, shows) in SEEN_ONLY.items():
        rows.append({'group': 'skyline/landmark', 'county_id': bid, 'instance': 'MI_P17_T_' + bid, 'what_they_show': shows,
                     'photographs': '', 'settings_changed': 'none', 'confidence_before': c0, 'confidence_after': c1})
    for bid, (sets, c0, c1, shows) in ZONE.items():
        mi = 'MI_P17_Z_' + bid
        files = obs.get('Z' + bid, {}).get('files') or []
        used += [(bid, f) for f in files]
        if sets:
            params[mi] = params_of(sets)
        rows.append({'group': 'zone1/2', 'county_id': bid, 'instance': mi, 'what_they_show': shows,
                     'photographs': ' | '.join('%s (%s, %s, %s)' % (f.get('title', ''), f.get('licence', ''), f.get('author', ''), f.get('page_url', '')) for f in files),
                     'settings_changed': json.dumps(params.get(mi)) if sets else 'none', 'confidence_before': c0, 'confidence_after': c1})
    with open(R2 + '/building_table_r2.csv', 'w', newline='', encoding='utf-8') as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    json.dump(params, open(R2 + '/instance_params_r2.json', 'w', encoding='utf-8'), indent=1)
    seen, uniq = set(), []
    for bid, f in used:
        key = f.get('page_url') or f.get('title')
        if key and key not in seen:
            seen.add(key)
            uniq.append((bid, f))
    with open(R2 + '/photographs_used_r2.csv', 'w', newline='', encoding='utf-8') as h:
        w = csv.writer(h, lineterminator='\n')
        w.writerow(['building', 'title', 'licence', 'author', 'date', 'page_url', 'use'])
        for bid, f in uniq:
            w.writerow([bid, f.get('title', ''), f.get('licence', ''), f.get('author', ''), f.get('date', ''), f.get('page_url', ''), f.get('use', '')])
    return rows, params, uniq


def apply(params):
    import unreal
    tools = ROOT + '/tools'
    if tools not in sys.path:
        sys.path.append(tools)
    import wieland_p17 as wp
    out = []
    for mi, p in params.items():
        path = '/Game/Wieland1529/Surroundings/P17/Materials/' + mi
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            out.append('MISSING ' + mi)
            continue
        wp.ensure_instance(mi, {k: tuple(v) if isinstance(v, list) else v for k, v in p.items()})
        unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        out.append(mi)
    return out


if __name__ == '__main__' and '--tables' in sys.argv:
    r, p, u = tables()
    print(len(r), 'rows', len(p), 'instances', len(u), 'photographs')
elif __name__ != '__main__':
    _rows, _params, _used = tables()
    _done = apply(_params)
    RESULT = 'table rows %d, instances set %d (%s), photographs %d' % (len(_rows), len([d for d in _done if not d.startswith('MISSING')]),
                                                                       ', '.join(d for d in _done if d.startswith('MISSING')) or 'none missing', len(_used))
