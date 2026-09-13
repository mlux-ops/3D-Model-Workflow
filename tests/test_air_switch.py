import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class AirSwitchAcceptance(unittest.TestCase):
    def test_saved_family(self):
        d=json.loads((ROOT/'output/air_switch/validation.json').read_text())
        self.assertNotIn('error',d,d.get('error'))
        self.assertEqual(d['stage'],'complete')
        self.assertEqual(d['revit_version'],'2025')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['placement'],'WorkPlaneBased')
        for actual,expected in zip(d['dimensions_inches'],[1.875,1.875,.9375]):
            self.assertAlmostEqual(actual,expected,places=3)
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['mounting_normal_dot_host_normal'],1,places=6)
        self.assertTrue(all(d['material_tests'].values()))
        self.assertEqual(d['warnings']+d['project_warnings'],[])
        self.assertIsNone(d['export_error'])
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__=='__main__':unittest.main()
