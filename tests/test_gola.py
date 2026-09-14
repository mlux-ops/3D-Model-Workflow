import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class GolaAcceptance(unittest.TestCase):
    def test_open_cap_catalog_envelope(self):
        r = json.loads((ROOT/'output/gola/validation.json').read_text())
        for t in r['types']:
            if t['key'].startswith('H'):
                self.assertIn('open_cap_envelope_mm', t, 'Catalog cap dimensions have not been measured')
                expected = [11, 76, 29] if t['key'] == 'HC' else [11, 58, 29]
                for measured, want in zip(t['open_cap_envelope_mm'], expected):
                    self.assertAlmostEqual(measured, want, delta=0.1)

    def test_saved_revit_family_and_behavior(self):
        path = ROOT/'output'/'gola'/'validation.json'
        self.assertTrue(path.exists(), 'No actual Revit validation report')
        r = json.loads(path.read_text())
        self.assertNotIn('error', r, r.get('error'))
        self.assertTrue(r['success'])
        self.assertEqual(r['revit_version'], '2025')
        self.assertTrue(r['reopened'])
        self.assertEqual(r['placement'], 'CurveBased')
        self.assertTrue(r['length_is_instance'])
        self.assertEqual(set(r['endpoint_references']), {'Left', 'Right'})
        self.assertTrue(r['vertical_face_placement'])
        self.assertEqual(len(r['types']), 4)
        for t in r['types']:
            self.assertTrue(t['both_endpoint_edits'])
            self.assertTrue(t['material_test'])
            for f in t['flex']:
                self.assertAlmostEqual(f['requested'], f['measured'], delta=0.1)
                expected = {'HC':(72.7,26),'HL':(56,27),'VS':(48.25,36.6),'VD':(66.5,36.6)}[t['key']]
                b = f['section']
                self.assertAlmostEqual(b[4]-b[1], expected[0], delta=0.1)
                self.assertAlmostEqual(b[5]-b[2], expected[1], delta=0.1)
            for a in t['accessories']:
                if t['key'].startswith('H'):
                    self.assertGreater(a['added_volume_mm3'], 0.1)
                else:
                    self.assertAlmostEqual(a['added_volume_mm3'], 0, delta=0.1)
            if t['key'].startswith('H'):
                self.assertTrue(t['end_cap_follows_length'])
                self.assertTrue(t['open_cap_test'])
        self.assertEqual(r['family_warnings'], [])
        self.assertEqual(r['project_warnings'], [])
        self.assertGreaterEqual(len(r['previews']), 6)
        for p in [r['rfa_path'], r['sample_project_path']]:
            self.assertGreater(Path(p).stat().st_size, 10000)

if __name__ == '__main__':
    unittest.main()
