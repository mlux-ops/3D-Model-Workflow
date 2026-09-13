import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class GolaCuttingAcceptance(unittest.TestCase):
    def test_recess_cuts_casework_and_tracks_each_type(self):
        path = ROOT/'output/gola_cutting/cutting_validation.json'
        self.assertTrue(path.exists(), 'The supplied family has no verified host-cutting behavior yet')
        r = json.loads(path.read_text())
        self.assertNotIn('error', r, r.get('error'))
        self.assertTrue(r['success'])
        self.assertEqual(r['revit_version'], '2025')
        self.assertTrue(r['cut_with_voids'])
        self.assertTrue(r['original_solids_preserved'])
        self.assertTrue(r['reopened'])
        self.assertEqual(r['family_warnings'], [])
        self.assertEqual(r['project_warnings'], [])
        self.assertEqual(len(r['types']), 4)
        for t in r['types']:
            self.assertTrue(t['casework_cut'])
            self.assertTrue(t['uncut_restores_host'])
            self.assertTrue(t['clearance_and_depth_test'])
            self.assertTrue(t['both_endpoint_tests'])
            self.assertTrue(t['vertical_cut_test'])
            for f in t['flex']:
                self.assertAlmostEqual(f['removed_mm3'], f['expected_mm3'], delta=1)
                self.assertAlmostEqual(f['profile_length_mm'], f['length_mm'], delta=.1)
        self.assertGreater(Path(r['rfa_path']).stat().st_size, 10000)

if __name__ == '__main__':
    unittest.main()
