import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DuoAcceptance(unittest.TestCase):
    def test_revit_family(self):
        path = ROOT / 'output/duo/validation.json'
        self.assertTrue(path.exists(), 'Duo has not been built in Revit')
        d = json.loads(path.read_text())
        self.assertNotIn('error', d, d.get('error'))
        self.assertEqual(d['stage'], 'complete')
        self.assertEqual(d['revit_version'], '2025')
        self.assertEqual(d['category'], 'Lighting Fixtures')
        self.assertEqual(d['placement'], 'WorkPlaneBased')
        self.assertTrue(d['reopened'])
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['placed_axis_z'], -1, places=5)
        for actual, expected in zip(d['dimensions_mm'], [210,210,d['total_drop_mm']]):
            self.assertAlmostEqual(actual,expected,places=2)
        for actual, expected in zip(d['shade_dimensions_mm'], [210,210,210]):
            self.assertAlmostEqual(actual,expected,places=2)
        self.assertGreater(d['saved_glow_luminance'],0)
        self.assertTrue(all(d['material_tests'].values()))
        self.assertEqual(d['warnings'], [])
        self.assertEqual(d['project_warnings'], [])
        self.assertIsNone(d['export_error'])
        self.assertGreaterEqual(len(d['preview_files']),3)
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__ == '__main__':
    unittest.main()
