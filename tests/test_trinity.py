import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TrinityAcceptance(unittest.TestCase):
    def test_saved_family(self):
        p=ROOT/'output/trinity/validation.json'
        self.assertTrue(p.exists(),'Trinity has not been built in Revit')
        d=json.loads(p.read_text())
        self.assertNotIn('error',d,d.get('error'))
        self.assertEqual(d['stage'],'complete')
        self.assertEqual(d['revit_version'],'2025')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['category'],'Lighting Fixtures')
        self.assertEqual(d['placement'],'WorkPlaneBased')
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['placed_axis_z'],-1,places=5)
        for actual,expected in zip(d['overall_dimensions_inches'],[14.25,14.25,48]):
            self.assertAlmostEqual(actual,expected,places=3)
        self.assertAlmostEqual(d['shade_height_inches'],6.125,places=3)
        self.assertAlmostEqual(d['bottom_opening_inches'],9.75,places=3)
        self.assertAlmostEqual(d['canopy_diameter_inches'],4.75,places=3)
        self.assertFalse(d['bottom_center_obstructed'])
        self.assertTrue(d['underside_diffuser_exposed'])
        self.assertTrue(all(d['material_tests'].values()))
        self.assertGreater(d['diffuser_glow_luminance'],0)
        self.assertEqual(d['smoke_asset_schema'],'SolidGlassSchema')
        # IronPython may serialize CLR Byte channel values as numeric strings.
        self.assertEqual([int(v) for v in d['smoke_transmission_rgb']],[115,120,127])
        self.assertEqual(d['warnings'],[])
        self.assertEqual(d['project_warnings'],[])
        self.assertIsNone(d['export_error'])
        self.assertGreaterEqual(len(d['preview_files']),4)
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__=='__main__': unittest.main()
