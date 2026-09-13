import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DeliverableAcceptance(unittest.TestCase):
    def test_revit_verified_family(self):
        report_path = ROOT / 'output' / 'purist-validation.json'
        self.assertTrue(report_path.exists(), 'No Revit validation report has been produced')
        report = json.loads(report_path.read_text())
        self.assertNotIn('error', report, report.get('error'))
        self.assertEqual(report['revit_version'], '2025')
        self.assertTrue(report['reopened'])
        self.assertTrue(report['loaded_and_face_placed'])
        self.assertTrue(report['material_parameter_test'])
        self.assertEqual(report['category'], 'Plumbing Fixtures')
        self.assertEqual(report['placement'], 'WorkPlaneBased')
        self.assertAlmostEqual(report['geometry_width_inches'], 7.25, places=3)
        self.assertAlmostEqual(report['geometry_projection_inches'], 4.25, places=3)
        self.assertAlmostEqual(report['analytic_projection_inches'], 4.25, places=3)
        self.assertAlmostEqual(report['mounting_normal_dot_host_normal'], 1.0, places=5)
        for measured, expected in zip(report['placed_dimensions_inches'], [7.25, 4.25, 9.125]):
            self.assertAlmostEqual(measured, expected, places=3)
        self.assertAlmostEqual(report['geometry_height_inches'], 9.125, places=3)
        self.assertEqual(report['warnings'], [])
        self.assertEqual(report['project_warnings'], [])
        self.assertIsNone(report['export_error'])
        self.assertEqual(len(report['preview_files']), 3)
        self.assertGreater(report['solid_volume_cubic_inches'], 0)
        self.assertTrue(report['chrome_appearance_asset'])
        self.assertTrue(Path(report['rfa_path']).exists())
        self.assertGreater(Path(report['rfa_path']).stat().st_size, 10000)


if __name__ == '__main__':
    unittest.main()
