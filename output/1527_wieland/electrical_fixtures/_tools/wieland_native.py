# -*- coding: utf-8 -*-
"""Task-local native family builds and independent saved-file measurements.

Run exclusively via the shared revit_run.py lock harness. IronPython 2.7.
"""
import os, json, datetime, traceback, math
from native_fixture_support import NativeFixture, DB, xyz, measured_geometry_bounds, all_solids

class WielandFixture(NativeFixture):
    def check_component(self, label, elements, dimensions, source):
        self.report.setdefault('component_checks', []).append({'label':label,
            'element_ids':[str(e.Id.Value) for e in elements], 'expected_dimensions_in':dimensions,
            'source':source})

    def material(self, label, rgb, gloss=.3, transparency=0, reflectivity=.08,
                 emission=0, cct=None, material_class='Metal'):
        param = NativeFixture.material(self, label, rgb, gloss, transparency,
                                       reflectivity, emission, cct, material_class)
        path = os.path.join(self.out, 'source', 'textures', label.replace(' ', '_') + '.png')
        if not os.path.isfile(path):
            raise RuntimeError('Missing companion bitmap: ' + path)
        mat = self.materials[label]
        scope = DB.Visual.AppearanceAssetEditScope(self.doc)
        asset = scope.Start(mat.AppearanceAssetId)
        prop = asset.FindByName('generic_diffuse')
        if prop.NumberOfConnectedProperties:
            prop.RemoveConnectedAsset()
        prop.AddConnectedAsset('UnifiedBitmap')
        bitmap = prop.GetSingleConnectedAsset()
        bitmap.FindByName('unifiedbitmap_Bitmap').Value = path
        for key in ['texture_URepeat', 'texture_VRepeat']:
            p = bitmap.FindByName(key)
            if p is not None:
                p.Value = True
        scope.Commit(True)
        scope.Dispose()
        self.report.setdefault('companion_bitmaps', {})[label] = path
        return param

    def finish(self):
        report = NativeFixture.finish(self)
        reopened = None
        try:
            reopened = self.app.OpenDocumentFile(self.path)
            elements = [reopened.GetElement(DB.ElementId(int(p['id']))) for p in report['parts']]
            if any(e is None for e in elements):
                raise RuntimeError('Saved-file geometry IDs did not survive reopen')
            bounds = measured_geometry_bounds(elements)
            actual = [bounds[i + 3] - bounds[i] for i in range(3)]
            errors = [abs(a - b) * 25.4 for a, b in zip(actual, self.expected)]
            textures = {}
            for label in self.parameters:
                param = reopened.FamilyManager.get_Parameter(label)
                mat = reopened.GetElement(reopened.FamilyManager.CurrentType.AsElementId(param))
                appearance = reopened.GetElement(mat.AppearanceAssetId).GetRenderingAsset()
                connected = appearance.FindByName('generic_diffuse').GetSingleConnectedAsset()
                path = connected.FindByName('unifiedbitmap_Bitmap').Value
                textures[label] = {'path': path, 'exists': os.path.isfile(path)}
            report.update({'saved_file_reopened_for_measurement': True, 'measured_saved_bounds_in': bounds,
                           'measured_saved_dimensions_in': actual, 'dimensional_error_mm': errors,
                           'saved_material_bitmaps': textures,
                           'parameter_scope': 'Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.'})
            report['gates']['saved_dimensions_within_1mm'] = max(errors) <= 1.0
            report['gates']['saved_bitmaps_resolve'] = all(t['exists'] for t in textures.values())
            for check in report.get('component_checks', []):
                parts = [reopened.GetElement(DB.ElementId(int(i))) for i in check['element_ids']]
                box = measured_geometry_bounds(parts)
                dims = [box[i+3]-box[i] for i in range(3)]
                check['measured_dimensions_in'] = dims
                check['error_mm'] = [abs(dims[i]-v)*25.4 if v is not None else None
                                     for i,v in enumerate(check['expected_dimensions_in'])]
                check['pass'] = all(v is None or v <= 1.0 for v in check['error_mm'])
            report['gates']['saved_components_within_1mm'] = all(c['pass'] for c in report.get('component_checks', []))
            for check in report.get('radial_checks', []):
                points=[]
                options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine
                for ident in check['element_ids']:
                    element=reopened.GetElement(DB.ElementId(int(ident)))
                    for solid in all_solids(element.get_Geometry(options)):
                        for face in solid.Faces:points.extend(face.Triangulate(1).Vertices)
                        for edge in solid.Edges:
                            curve=edge.AsCurve()
                            points.extend(curve.Evaluate(float(i)/256,True) for i in range(257))
                cx,cy=check.get('center_in',[0,0])
                diameter=2*max(math.hypot(p.X*12-cx,p.Y*12-cy) for p in points)
                check.update(measured_diameter_in=diameter,error_mm=abs(diameter-check['expected_diameter_in'])*25.4)
                check['pass']=check['error_mm']<=1.0
            report['gates']['saved_radial_dimensions_within_1mm']=all(c['pass'] for c in report.get('radial_checks',[]))
            report['technical_pass'] = all(report['gates'].values())
        except Exception:
            report['technical_pass'] = False
            report['independent_readback_error'] = traceback.format_exc()
        finally:
            if reopened is not None:
                reopened.Close(False)
        report['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
        with open(os.path.join(self.out, 'validation.json'), 'w') as stream:
            json.dump(report, stream, indent=2, default=str)
        if not report['technical_pass']:
            raise RuntimeError('Saved-family readback failed; see validation.json')
        return report

def build_maxim(app, out):
    fixture = None
    try:
        fixture = WielandFixture(app, out, 'Maxim_Trim_57670WTBK_Black_R2025',
                                 'Maxim Lighting', '57670WTBK', '57670WTBK - Black / White',
                                 'ceiling', [16.0, 16.0, 1.5])
        black = fixture.material('Black Housing', (24, 24, 24), gloss=.22)
        diffuser = fixture.material('White Diffuser', (244, 244, 240), gloss=.15,
                                    reflectivity=.025, material_class='Plastic')
        fixture.revolve('Continuous recessed perimeter housing', xyz(), DB.XYZ.BasisZ,
                        [(7.72, 0), (7.88, 0), (8.0, .15), (8.0, 1.35),
                         (7.92, 1.5), (7.72, 1.5)], black)
        fixture.cylinder('Recessed white polycarbonate diffuser', xyz(), DB.XYZ.BasisZ,
                         7.74, .30, 1.36, diffuser, .06)
        fixture.cylinder('Rear mounting disk', xyz(), DB.XYZ.BasisZ, 7.73, 0, .15, black)
        fixture.note('Manufacturer 57670WTBK dimensions: 16 x 16 x 1.5 inches. '
                     'ASSUMPTION: recessed diffuser diameter, perimeter profile, sheet thickness and small edge rounds are photo-derived visualization details. '
                     'Black housing and white diffuser; no photometric light source. Nominal product geometry is fixed; finishes are editable.')
        fixture.report['source_url'] = 'https://www.maximlighting.com/product/indoor-lighting/flush-mounts/trim-16-rd-led-flush-mount-3000k/57670WTBK'
        fixture.report['rfa_search'] = 'Manufacturer product page and BIM/Photometric resources inspected; no direct 57670WTBK RFA link found.'
        fixture.finish()
    except Exception:
        if fixture is not None:
            fixture.fail()
            with open(os.path.join(out, 'validation.json'), 'w') as stream:
                json.dump(fixture.report, stream, indent=2, default=str)
        raise
