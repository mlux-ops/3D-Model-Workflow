from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools'/'render_native_studio.py'
s=p.read_text()
old="        nt.links.new(glow.outputs['Color'],shader.inputs['Emission Color'])"
new="""        nt.links.new(glow.outputs['Color'],shader.inputs['Emission Color'])
        if info.get('class')=='Stone':
            emitter=nt.nodes.new('ShaderNodeEmission')
            emitter.inputs['Strength'].default_value=1.0
            nt.links.new(glow.outputs['Color'],emitter.inputs['Color'])
            nt.links.new(emitter.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])"""
assert old in s;s=s.replace(old,new)
s=s.replace("scene.view_settings.exposure=-1.5","scene.view_settings.exposure=0.0")
s=s.replace("'method':'actual native RFA mesh and saved appearance inputs; Cycles shader translation approximate'","'method':'actual native RFA mesh and saved appearance inputs; Cycles shader translation approximate; luminous stone shown with its saved luminous-color bitmap under normalized emission'")
p.write_text(s)