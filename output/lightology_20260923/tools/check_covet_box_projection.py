from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools'/'render_native_studio.py'
s=p.read_text().replace("uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map='Revit physical scale'","uvnode=nt.nodes.new('ShaderNodeTexCoord')")
s=s.replace("nt.links.new(uvnode.outputs['UV'],img.inputs['Vector'])","img.projection='BOX';img.projection_blend=.1\n        nt.links.new(uvnode.outputs['Generated'],img.inputs['Vector'])")
s=s.replace("nt.links.new(uvnode.outputs['UV'],glow.inputs['Vector'])","glow.projection='BOX';glow.projection_blend=.1\n        nt.links.new(uvnode.outputs['Generated'],glow.inputs['Vector'])")
s=s.replace("'size':list(n.image.size) if n.type=='TEX_IMAGE' and n.image else None","'size':list(n.image.size) if n.type=='TEX_IMAGE' and n.image else None,'pixel_sample':list(n.image.pixels[0:4]) if n.type=='TEX_IMAGE' and n.image else None")
import ast;ast.parse(s);p.write_text(s)