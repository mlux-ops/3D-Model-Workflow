"""Fetch candidate references (manufacturer / distributor) into references/web/. Logs HTTP status and size.
Usage: python a01_fetch.py name=url [name=url ...]   (no args: the default list below)"""
import json
import os
import sys
import urllib.request

from guard import out_path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"
ELM = "https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/"
MS = "https://www.milestonetiles.com/cdn/shop/files/"
DEFAULT = {
    "w01_elm_jute_veincut_24x48_01.jpg": ELM + "6508c8490fee3dfe75084253_ElmStone_Jute_Vein-Cut_24x48_01.jpg",
    "w02_elm_jute_crosscut_24x48_03.jpg": ELM + "6508c8490fee3dfe75084250_ElmStone_Jute_Cross-Cut_24x48_03.jpg",
    "w03_elm_elmstone_catalog.pdf": ELM + "67e1e333dbe0edb3e5233508_ElmStone%20Catalog.pdf",
    "w04_ms_ecostone_jute_veincut_24x48_01.jpg": MS + "MILE_stone_EcoStone_Jute_VeinCut_24x48_01.jpg",
    "w05_ms_ecostone_veincut_jute_24x48_panel.jpg": MS + "MILE_stone_EcoStone_Vein-Cut_Jute_24x48_Panel.jpg",
    "w06_ms_room_wall48x110_floor24x48.jpg": MS + "MILE_stone_EcoStone_Wall_Vein-Cut_Jute_48x110_Floor_Vein-Cut_Jute_24x48_dde562be-5433-40ff-8376-1dce42296a0c.jpg",
    "w07_ms_jute_veincut_1x3mosaic_01.jpg": MS + "MILE_stone_EcoStone_Jute_VeinCut_1x3Mosaic_01.jpg",
    "w08_ms_ecostone_brochure_2026.pdf": MS + "MILE_stone_EcoStone_Brochure_2026.pdf",
    "w09_ms_tech_specs.pdf": MS + "MILE_stone_Tech_Specs.pdf",
}


def main():
    items = dict(a.split("=", 1) for a in sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT
    logp = out_path("_work/fetch_log.json")
    log = json.load(open(logp)) if os.path.exists(logp) else []
    for name, url in items.items():
        rec = {"name": name, "url": url}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                rec["status"] = r.status
            open(out_path("references/web/" + name), "wb").write(data)
            rec["bytes"] = len(data)
        except Exception as e:  # noqa: BLE001
            rec["error"] = repr(e)
        log.append(rec)
        print(rec)
    json.dump(log, open(logp, "w"), indent=1)


if __name__ == "__main__":
    main()
