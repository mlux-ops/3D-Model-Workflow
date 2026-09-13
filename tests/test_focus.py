import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class FocusAcceptance(unittest.TestCase):
 def test_revit_results(self):
  d=json.loads((ROOT/'output/focus/validation.json').read_text())
  self.assertNotIn('error',d)
  self.assertEqual(d['stage'],'complete')
  self.assertTrue(d['reopened'] and d['loaded_and_face_placed'])
  self.assertEqual(d['placement'],'WorkPlaneBased')
  self.assertEqual(d['warnings']+d['project_warnings'],[])
  self.assertTrue(all(d['material_tests'].values()))
  self.assertEqual(len(d['flex_tests']),4)
  for f in d['flex_tests']: self.assertAlmostEqual(f['actual_drop'],f['expected_drop'],places=5)
  self.assertGreater(Path(d['rfa_path']).stat().st_size,100000)
if __name__=='__main__':unittest.main()
