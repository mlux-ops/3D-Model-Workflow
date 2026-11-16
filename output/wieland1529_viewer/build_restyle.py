#!/usr/bin/env python3
"""1529 Wieland bathroom viewer -- Material Collager restyle + enhancement build.

Reads the released, self-contained viewer (baseline/index.html) and writes
dist/index.html.  Nothing in the frozen data payload, the native geometry
bundle, the Three.js import map or the scene/geometry logic is modified; the
build only

  1. repairs double-encoded (mojibake) text inside the module script,
  2. remaps the dark UI colours that the module injects at runtime,
  3. replaces the page chrome (head CSS + header markup) with the Material
     Collager "Monochrome Glass" design system (src/theme.css, Inter),
  4. appends src/enhance.js to the end of the existing module so it can use
     the viewer's own state and functions.

Every source hook is asserted; the build fails loudly rather than silently
producing a half-patched viewer.  Re-run after any upstream rebuild:

    python -B build_restyle.py [path/to/index.html]

Standard library only.
"""
import base64
import colorsys
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
BASELINE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "baseline" / "index.html"
SRC = ROOT / "src"
DIST = ROOT / "dist"
INTER = SRC / "fonts" / "InterVariable.woff2"


def must_replace(text, old, new, count=1, label=None):
    found = text.count(old)
    if found != count:
        raise SystemExit(f"FAIL hook '{label or old[:60]}': expected {count}, found {found}")
    return text.replace(old, new)


# ---------------------------------------------------------------- mojibake
_CP1252_REVERSE = {}
for _b in range(256):
    try:
        _CP1252_REVERSE[bytes([_b]).decode("cp1252")] = _b
    except UnicodeDecodeError:
        _CP1252_REVERSE[chr(_b)] = _b  # undefined cp1252 slots pass through as latin-1


def repair_mojibake(text):
    """Undo UTF-8 text that was read as cp1252 and re-saved as UTF-8."""
    fixed = 0

    def attempt(match):
        nonlocal fixed
        run = match.group(0)
        try:
            raw = bytes(_CP1252_REVERSE[ch] for ch in run)
            out = raw.decode("utf-8")
        except (KeyError, UnicodeDecodeError):
            return run
        fixed += 1
        return out

    # lead byte (C2-F4 as cp1252 chars) followed by 1-3 continuation bytes
    lead = "[Â-ô]"
    cont = "[\u0080-¿ŒœŠšŸŽžƒˆ˜–—‘-„†-•…‰‹›€™]"
    text = re.sub(f"{lead}{cont}{{1,3}}", attempt, text)
    return text, fixed


# ------------------------------------------------------------ colour remap
def _rgb(hexv):
    h = hexv.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return r, g, b, a


def _classify(hexv):
    r, g, b, a = _rgb(hexv)
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    hue, sat, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    warm = 0.04 <= hue <= 0.14 and sat >= 0.18  # the old tan/brass accent family
    return lum, warm, a


def _remap_hex(prop, hexv):
    lum, warm, a = _classify(hexv)
    prop = prop.strip().lower()
    if prop.startswith("background"):
        if warm and lum > 0.3:
            return "#000000"                      # old tan "active" fill -> ink
        if lum < 0.4:
            return f"rgba(255,255,255,{max(a, .9):.2f})" if a < 1 else "#ffffff"
        return "#f5f6f3"
    if prop in ("color", "fill"):
        if lum < 0.25:
            return "#ffffff"                      # dark-on-tan text -> white-on-ink
        if warm or lum > 0.72:
            return "#000000"
        return "#5d655f"
    if prop.startswith("box-shadow") or prop.startswith("text-shadow"):
        return "rgba(0,0,0,.10)"
    if prop.startswith("border") or prop.startswith("outline"):
        return "#000000" if warm else "rgba(0,0,0,.2)"
    return hexv


_DECL = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}`'\"]*#[0-9a-fA-F]{3,8}[^;{}`'\"]*)")
_HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def remap_css(css):
    def decl(match):
        prop, value = match.group(1), match.group(2)
        if "gradient" in value:
            return match.group(0)
        value = _HEX.sub(lambda h: _remap_hex(prop, h.group(0)), value)
        if prop.lower().startswith("text-shadow"):
            value = "none"
        return f"{prop}:{value}"
    return _DECL.sub(decl, css)


def remap_region(text, pattern, label, expect=None):
    """Apply remap_css to group 2 of every match of pattern."""
    hits = 0

    def sub(match):
        nonlocal hits
        hits += 1
        return match.group(1) + remap_css(match.group(2)) + match.group(3)

    text = re.sub(pattern, sub, text, flags=re.S)
    if expect is not None and hits != expect:
        raise SystemExit(f"FAIL colour region '{label}': expected {expect}, found {hits}")
    if hits == 0:
        raise SystemExit(f"FAIL colour region '{label}': no matches")
    return text


# -------------------------------------------------------------------- build
def main():
    html = BASELINE.read_text(encoding="utf-8")
    baseline_sha = hashlib.sha256(BASELINE.read_bytes()).hexdigest()

    # ---- split out the module script (last <script type="module">)
    open_tag = '<script type="module">'
    start = html.rfind(open_tag)
    if start < 0:
        raise SystemExit("FAIL: module script not found")
    start += len(open_tag)
    end = html.index("</script>", start)
    module = html[start:end]

    # ---- frozen payload fingerprints: must be byte-identical after the build
    def block(doc, marker):
        i = doc.index(marker) + len(marker)
        return doc[i:doc.index("</script>", i)]

    frozen_markers = ['<script id="data" type="application/json">',
                      '<script type="importmap">',
                      '<script id="r068-primary-plumbing" type="application/json">',
                      '<script id="native-geometry" type="application/octet-stream">']
    frozen_before = {m: hashlib.sha256(block(html, m).encode()).hexdigest() for m in frozen_markers}
    data = json.loads(block(html, frozen_markers[0]))
    rooms = data["rooms"]
    instances = sum(len(r["physical_instances"]) for r in rooms)
    if len(rooms) != 13 or instances != 26:
        raise SystemExit(f"FAIL: expected 13 types / 26 instances, found {len(rooms)} / {instances}")

    # ---- 1. text repair
    module, fixed = repair_mojibake(module)
    leftovers = len(re.findall("[ÂÃ]", module))
    # one comment deliberately documents the U+FFFD artefact; it is left alone

    # ---- 2. runtime-injected dark UI colours -> light system
    module = remap_region(module, r"((?:style|sheet)\.textContent=`)(.*?)(`;)", "injected sheets", 2)
    module = remap_region(module, r"(\.style\.cssText=')(.*?)(';)", "cssText", 9)
    module = remap_region(module, r"(style=\")([^\"]*#[0-9a-fA-F]{3,8}[^\"]*)(\")", "inline style attrs", 2)

    # ---- 3. scene presentation hooks (no geometry / material-pick changes)
    module = must_replace(module, "scene.background=new THREE.Color(0x17222b);",
                          "scene.background=null; /* paper backdrop comes from the stage CSS */",
                          label="scene background")
    module = must_replace(module, "ctx.fillStyle='rgba(14,27,38,.82)';",
                          "ctx.fillStyle='rgba(255,255,255,.94)';", label="plan label fill")
    module = must_replace(module, "ctx.strokeStyle='#ba9a72';ctx.lineWidth=3;",
                          "ctx.strokeStyle='#000000';ctx.lineWidth=2;", label="plan label stroke")
    module = must_replace(module, "function addPlanLabel(text,x,z,color='#dce5df'){",
                          "function addPlanLabel(text,x,z,color='#000000'){color='#000000';",
                          label="plan label ink")
    module = must_replace(module, "ctx.font='bold 32px Segoe UI, sans-serif';",
                          "ctx.font='600 30px Inter, Segoe UI, sans-serif';", label="plan label font")
    # gallery chrome
    module = module.replace("font:600 11px Segoe UI", "font:500 10.5px Inter,Arial,sans-serif")
    for hook in ("installViewerCompletion();", "installNativeAudit();", "window.__viewerDebug=", "start();"):
        if hook not in module:
            raise SystemExit(f"FAIL: upstream hook missing: {hook}")

    # ---- 4. enhancement layer runs inside the same module scope
    enhance = (SRC / "enhance.js").read_text(encoding="utf-8")
    # generated single-tile texture sheets (tools/gen_tile_textures.py)
    import base64 as _b64, json as _json
    sheets = _json.loads((SRC / "tiles" / "tiles.json").read_text(encoding="utf-8"))
    for sheet in sheets:
        for field, suffix in (("color", ".jpg"), ("normal", "_n.jpg")):
            raw = (SRC / "tiles" / (sheet["key"] + suffix)).read_bytes()
            sheet[field] = "data:image/jpeg;base64," + _b64.b64encode(raw).decode("ascii")
    marker = "/*MC_TILE_SHEETS*/[]"
    assert enhance.count(marker) == 1, "tile sheet marker missing in enhance.js"
    enhance = enhance.replace(marker, _json.dumps(sheets, ensure_ascii=False))
    module = module.rstrip() + "\n\n// ===== Material Collager enhancement layer (build_restyle.py) =====\n" + enhance + "\n"

    # ---- 5. page chrome
    theme = (SRC / "theme.css").read_text(encoding="utf-8")
    font_b64 = base64.b64encode(INTER.read_bytes()).decode("ascii")
    font_face = ("@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;"
                 f"src:url(data:font/woff2;base64,{font_b64}) format('woff2')}}\n")
    head_start = html.index("<style>")
    head_end = html.index("</style>", head_start) + len("</style>")
    html_head = (html[:head_start] + "<style id=\"mc-font\">\n" + font_face + "</style>\n"
                 + "<style id=\"mc-base\">\n" + (SRC / "base.css").read_text(encoding="utf-8") + "</style>")
    body = html[head_end:start - len(open_tag)]
    shell = (SRC / "shell.html").read_text(encoding="utf-8")
    old_header_start = body.index(" <header>")
    old_header_end = body.index("</header>") + len("</header>")
    body = body[:old_header_start] + shell + body[old_header_end:]
    body = must_replace(body, '<div class="alert">CONTEXT ONLY · NOT FIELD-ACCURATE</div>',
                        '<div class="alert">Provisional study · not for construction</div>', label="alert chip")
    body = must_replace(body, '<div id="app">', (SRC / "loading.html").read_text(encoding="utf-8") + '<div id="app">',
                        label="app root")
    tail = html[end:]
    # theme sheet sits at the end of <body> so it follows every sheet the
    # module appends to <head> and wins equal-specificity ties.
    tail = must_replace(tail, "</body>", "<style id=\"mc-theme\">\n" + theme + "</style>\n</body>", label="body end")

    out = html_head + body + open_tag + module + tail
    out = must_replace(out, "<title>1529 Wieland | Bathroom 3D Material Viewer</title>",
                       "<title>1529 Wieland — Bathroom Material Viewer</title>", label="title")

    # ---- 6. verify the frozen payloads are untouched
    for marker, digest in frozen_before.items():
        if hashlib.sha256(block(out, marker).encode()).hexdigest() != digest:
            raise SystemExit(f"FAIL: frozen payload changed: {marker}")

    DIST.mkdir(exist_ok=True)
    target = DIST / "index.html"
    target.write_text(out, encoding="utf-8", newline="")
    manifest = {
        "baseline": str(BASELINE), "baseline_sha256": baseline_sha,
        "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "output_bytes": target.stat().st_size,
        "mojibake_sequences_repaired": fixed, "mojibake_lead_chars_remaining": leftovers,
        "frozen_payloads_identical": True, "room_types": len(rooms), "physical_instances": instances,
    }
    (DIST / "build_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"PASS restyled viewer -> {target} ({target.stat().st_size:,} bytes), "
          f"{fixed} text repairs, {leftovers} lead chars left, frozen payloads identical, {len(rooms)} rooms")


if __name__ == "__main__":
    main()
