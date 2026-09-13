import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TrisAcceptance(unittest.TestCase):
    def test_saved_revit_lighting_family(self):
        path = ROOT / 'output/tris/validation.json'
        self.assertTrue(path.exists(), 'Tris has not yet been built and verified in Revit')
        data = json.loads(path.read_text())
        self.assertNotIn('error', data, data.get('error'))
        self.assertEqual(data['stage'], 'complete')
        self.assertEqual(data['revit_version'], '2025')
        self.assertEqual(data['category'], 'Lighting Fixtures')
        self.assertEqual(data['placement'], 'WorkPlaneBased')
        self.assertTrue(data['reopened'])
        self.assertTrue(data['loaded_and_face_placed'])
        self.assertAlmostEqual(data['mounting_normal_dot_host_normal'], 1, places=5)
        for measured, expected in zip(data['dimensions_inches'], [25.6,4.5,3.4]):
            self.assertAlmostEqual(measured, expected, places=3)
        for measured, expected in zip(data['placed_dimensions_inches'], [25.6,3.4,4.5]):
            self.assertAlmostEqual(measured, expected, places=3)
        self.assertEqual(data['panel_count'], 3)
        self.assertEqual(len(data['panel_bounds_inches']), 3)
        panels = sorted(data['panel_bounds_inches'], key=lambda b:b[0])
        for box in panels:
            self.assertAlmostEqual(box[3]-box[0], 6.2, places=3)
            self.assertAlmostEqual(box[4]-box[1], .18, places=3)
        self.assertAlmostEqual(panels[1][0]-panels[0][3], 3.5, places=3)
        self.assertAlmostEqual(panels[2][0]-panels[1][3], 3.5, places=3)
        self.assertTrue(data['metal_material_test'])
        self.assertTrue(data['diffuser_material_test'])
        self.assertEqual(data['saved_unlit_luminance'],0)
        self.assertEqual(Path(data['saved_diffuse_texture']),Path(data['texture_path']))
        self.assertEqual(data['warnings'], [])
        self.assertEqual(data['project_warnings'], [])
        self.assertEqual(data['texture_connected_faces'], 6)
        self.assertTrue(Path(data['texture_path']).exists())
        self.assertTrue(Path(data['rfa_path']).exists())
        self.assertIsNone(data['export_error'])
        self.assertGreaterEqual(len(data['preview_files']), 4)

if __name__ == '__main__':
    unittest.main()
