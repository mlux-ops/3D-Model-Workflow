"""Read Chrome --dump-dom result without executing or modifying model/source files."""
from pathlib import Path
import argparse
import html
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument("path", type=Path)
parser.add_argument("--expect-qa", action="store_true")
parser.add_argument("--expect-gallery", action="store_true")
parser.add_argument("--expect-instance")
args = parser.parse_args()
doc = args.path.read_text(encoding="utf-8", errors="replace")
match = re.search(r'<div id="viewer-qa-result"[^>]*>(.*?)</div>', doc, re.S)
qa = None
if match:
    try:
        qa = json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError as exc:
        qa = {"parse_error": str(exc)}
gal = re.search(r'<div id="viewer-gallery"[^>]*data-status="([^"]+)"', doc)
body = re.search(r'<body([^>]*)>', doc)
body_attrs = body.group(1) if body else ""
def body_attr(name):
    match = re.search(r'\b' + re.escape(name) + r'="([^"]+)"', body_attrs)
    return match.group(1) if match else None
instance = re.search(r'<select id="viewer-instance"[^>]*>(.*?)</select>', doc, re.S)
selected = re.findall(r'<option[^>]*selected=""[^>]*>(.*?)</option>', instance.group(1), re.S) if instance else []
result = {
    "html_chars": len(doc),
    "runtime_toolbar": '<div id="viewer-v2-toolbar"' in doc,
    "runtime_native_element_inspector": 'id="viewer-v2-element"' in doc,
    "runtime_gallery_status": gal.group(1) if gal else None,
    "runtime_gallery_cards": len(re.findall(r'<img src="data:image/png;base64,', doc)),
    "active_room": body_attr("data-viewer-room"),
    "active_instance": body_attr("data-viewer-instance"),
    "active_mode": body_attr("data-viewer-mode"),
    "qa_in_progress": re.search(r'<body[^>]*data-viewer-qa="([^"]+)"', doc).group(1) if re.search(r'<body[^>]*data-viewer-qa="([^"]+)"', doc) else None,
    "qa_last_step": re.search(r'<body[^>]*data-viewer-qa-step="([^"]+)"', doc).group(1) if re.search(r'<body[^>]*data-viewer-qa-step="([^"]+)"', doc) else None,
    "url_instance_option_selected": selected,
    "qa": {key: qa.get(key) for key in ("status", "tested", "physical_instance_links", "fail")} if qa else None,
}
print(json.dumps(result, indent=2, ensure_ascii=True))
if not result["runtime_toolbar"]:
    raise SystemExit("Browser module did not initialize; investigate before claiming QA.")
if args.expect_qa and not qa:
    raise SystemExit("Expected QA DOM absent.")
if args.expect_gallery and (not gal or gal.group(1) != "COMPLETE" or result["runtime_gallery_cards"] != 13):
    raise SystemExit("Full 13-room gallery not yet complete.")
if args.expect_instance and result["active_instance"] != args.expect_instance:
    raise SystemExit("Expected direct instance not active.")
