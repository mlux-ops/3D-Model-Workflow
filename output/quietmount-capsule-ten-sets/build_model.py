from pathlib import Path
import sys
source=(Path(__file__).resolve().parent.parent/'quietmount-v5-capsule/build_model.py').read_text()
source=source.replace('TS=[12.7,19.05,20,22.225]','TS=[12.7,19.05,20,22.225,20.5,18.5,18,14,17]')
# Check the actual selected snug covers against the unchanged screw envelope.
source=source.replace("# Optional shallow gauge", "lowercap=parts['lower_cover_snug'];uppercap=parts['upper_cover_snug']\n# Optional shallow gauge")
sys.argv.append('--geometry-only')
exec(compile(source,__file__,'exec'))
