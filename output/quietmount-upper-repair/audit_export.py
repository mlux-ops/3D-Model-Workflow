from pathlib import Path
s=(Path(__file__).resolve().parent.parent/'quietmount-tab-down/audit_mesh.py').read_text().replace("*upper_mushroom.stl","*upper_mushroom_REPAIRED.stl")
exec(compile(s,__file__,'exec'))
assert len(result)==10 and all(x['bad_edges']==0 and x['volume']>0 for x in result)
print('All ten exported meshes pass edge-closure and positive-volume checks.')
