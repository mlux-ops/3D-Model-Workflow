import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ManufacturerRevision(unittest.TestCase):
    def test_saved_revision(self):
        d=json.loads((ROOT/'output/axor_angled_v2/validation.json').read_text())
        self.assertNotIn('error',d,d.get('error'))
        self.assertEqual(d['stage'],'complete')
        self.assertTrue(d['reopened'])
        self.assertEqual(d['revit_version'],'2025')
        self.assertAlmostEqual(d['dimensions_inches'][2],13.5,places=2)
        self.assertGreater(d['rear_extent_inches'],1.75)
        self.assertEqual({p['source_id'] for p in d['manufacturer_parts']},{4108,4101,4105})
        for p in d['manufacturer_parts']:
            self.assertLess(p['volume_delta']/p['source_volume'],1e-6)
        self.assertTrue(d['loaded_and_face_placed'])
        self.assertAlmostEqual(d['mounting_normal_dot_host_normal'],1,places=6)
        self.assertTrue(all(d['material_tests'].values()))
        self.assertEqual(d['warnings']+d['project_warnings'],[])
        self.assertIsNone(d['export_error'])
        self.assertGreater(Path(d['rfa_path']).stat().st_size,10000)

if __name__=='__main__':unittest.main()
