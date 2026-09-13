import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class VeraAcceptance(unittest.TestCase):
    def test_saved_family(self):
        d = json.loads((ROOT/'output/vera/validation.json').read_text())
        self.assertNotIn('error', d)
        self.assertEqual(d['stage'], 'complete')
        self.assertEqual(d['revit_version'], '2025')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['category'], 'Lighting Fixtures')
        self.assertEqual(d['placement'], 'WorkPlaneBased')
        for actual, expected in zip(d['dimensions_inches'], [22.87, 4.75, 3.25]):
            self.assertAlmostEqual(actual, expected, places=3)
        self.assertEqual(d['diffuser_count'], 2)
        self.assertLess(min(d['diffuser_centers_y_inches']), 0)
        self.assertGreater(max(d['diffuser_centers_y_inches']), 0)
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['mounting_normal_dot_host_normal'], 1, places=5)
        self.assertTrue(all(d['material_tests'].values()))
        self.assertGreater(d['diffuser_glow_luminance'], 0)
        self.assertEqual(d['warnings'] + d['project_warnings'], [])
        self.assertIsNone(d['export_error'])
        self.assertGreater(Path(d['rfa_path']).stat().st_size, 10000)

if __name__ == '__main__':
    unittest.main()
