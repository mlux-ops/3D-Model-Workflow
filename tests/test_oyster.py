import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class OysterAcceptance(unittest.TestCase):
    def test_saved_family(self):
        p=ROOT/'output/oyster/validation.json'
        self.assertTrue(p.exists(),'Oyster has not been built in Revit')
        d=json.loads(p.read_text())
        self.assertNotIn('error',d,d.get('error'))
        self.assertEqual(d['stage'],'complete')
        self.assertEqual(d['revit_version'],'2025')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['category'],'Lighting Fixtures')
        self.assertEqual(d['placement'],'WorkPlaneBased')
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['mounting_normal_dot_host_normal'],1,places=5)
        for actual,expected in zip(d['dimensions_inches'],[5.24,12,3]):
            self.assertAlmostEqual(actual,expected,places=3)
        self.assertAlmostEqual(d['diffuser_diameter_inches'],5,places=3)
        self.assertAlmostEqual(d['diffuser_depth_inches'],3,places=3)
        self.assertTrue(d['diffuser_depth_continuous'])
        self.assertEqual(d['diffuser_solid_count'],1)
        self.assertFalse(d['lower_opening_obstructed'])
        self.assertTrue(all(d['material_tests'].values()))
        self.assertGreater(d['diffuser_glow_luminance'],0)
        self.assertIn('stainless',d['steel_asset'].lower())
        self.assertEqual(d['warnings'],[])
        self.assertEqual(d['project_warnings'],[])
        self.assertIsNone(d['export_error'])
        self.assertGreaterEqual(len(d['preview_files']),4)
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__=='__main__': unittest.main()
