import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CourceletteAcceptance(unittest.TestCase):
    def test_saved_family(self):
        path = ROOT / 'output/courcelette/validation.json'
        self.assertTrue(path.exists(), 'Courcelette has not been built in Revit')
        d = json.loads(path.read_text())
        self.assertNotIn('error',d,d.get('error'))
        self.assertEqual(d['stage'],'complete')
        self.assertEqual(d['revit_version'],'2025')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['category'],'Lighting Fixtures')
        self.assertEqual(d['placement'],'WorkPlaneBased')
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['placed_axis_z'],-1,places=5)
        self.assertEqual(d['globe_count'],6)
        self.assertEqual(d['bulb_count'],6)
        for actual,expected in zip(d['overall_dimensions_inches'],[46.6,21.59,50.5]):
            self.assertAlmostEqual(actual,expected,places=3)
        self.assertAlmostEqual(d['fixture_body_height_inches'],12.95,places=3)
        self.assertEqual(len(set(round(g['center'][2],3) for g in d['globes'])),3)
        self.assertTrue(all(d['material_tests'].values()))
        self.assertGreater(d['glass_transparency'],.8)
        self.assertGreater(d['bulb_glow_luminance'],0)
        self.assertEqual(d['warnings'],[])
        self.assertEqual(d['project_warnings'],[])
        self.assertIsNone(d['export_error'])
        self.assertGreaterEqual(len(d['preview_files']),4)
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__=='__main__':
    unittest.main()
