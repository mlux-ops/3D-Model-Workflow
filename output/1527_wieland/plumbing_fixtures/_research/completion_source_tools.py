"""Inspect only task downloads and render manufacturer SVG references when available."""
import datetime,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
folder=Path(os.environ['USERPROFILE'])/'Downloads'
files=[]
for path in folder.iterdir():
    if path.is_file() and path.name.startswith('produravit_downloads_20261002'):
        files.append({'path':str(path),'bytes':path.stat().st_size,'modified':datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat()})
print(json.dumps({'duravit_task_downloads':files,'svg_renderers':{x:bool(importlib.util.find_spec(x)) for x in ['cairosvg','svglib','fitz']}},indent=2))
if importlib.util.find_spec('cairosvg'):
    import cairosvg
    for svg in (ROOT/'443306/downloads').glob('*.svg'):
        png=svg.with_suffix('.png')
        if not png.exists():cairosvg.svg2png(url=str(svg),write_to=str(png),output_width=1600)
        print(str(png))
