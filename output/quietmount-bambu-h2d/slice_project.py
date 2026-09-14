from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parent
(root/'sliced').mkdir(exist_ok=True)
args=['C:/Program Files/Bambu Studio/bambu-studio.exe',str(root/'QuietMount_H2D_PolyTerra_project.3mf'),
      '--slice','0','--outputdir',str(root/'sliced'),'--export-3mf','QuietMount_H2D_PolyTerra_sliced.3mf']
print('Slicing both plates in Bambu Studio',flush=True)
p=subprocess.run(args,capture_output=True,timeout=900)
(root/'sliced'/'native_slice.log').write_bytes(p.stdout+p.stderr)
print('Slice return',p.returncode,flush=True)
if (root/'sliced'/'result.json').exists():print((root/'sliced'/'result.json').read_text(),flush=True)
