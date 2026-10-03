"""Guard the synthetic demo against misleading gap and number presentation."""
import copy
import unittest
from build_demo import build_demo


def assert_no_bridged_gaps(demo):
    for segment in demo['glucoseSegments']:
        assert all(b['minute'] - a['minute'] <= 10 for a,b in zip(segment,segment[1:])), 'CGM gap was bridged'


class DemoTruthTests(unittest.TestCase):
    def test_missing_window_stays_unknown(self):
        gap=next(m for m in build_demo()['moments'] if m['id']=='gap')
        self.assertIsNone(gap['minGlucose'])
        self.assertEqual(gap['readingCount'],0)
        self.assertEqual([f['id'] for f in gap['factors']],['no_glucose_data'])

    def test_chart_does_not_connect_missing_sensor_interval(self):
        demo=build_demo()
        assert_no_bridged_gaps(demo)
        broken=copy.deepcopy(demo)
        broken['glucoseSegments']=[broken['glucose']]
        with self.assertRaisesRegex(AssertionError,'CGM gap was bridged'):
            assert_no_bridged_gaps(broken)

    def test_cooccurring_factors_do_not_claim_separability(self):
        moment=next(m for m in build_demo()['moments'] if m['id']=='together')
        self.assertEqual({f['id'] for f in moment['factors']},{'uphill','low_glucose_nearby'})
        self.assertFalse(moment['separable'])
        self.assertEqual(moment['minGlucose'],65)

    def test_missing_glucose_window_does_not_claim_separability(self):
        gap=next(m for m in build_demo()['moments'] if m['id']=='gap')
        self.assertFalse(gap['separable'])

    def test_reported_counts_and_coverage_match_observed_points(self):
        demo=build_demo()
        self.assertEqual(demo['facts']['below70Count'],sum(p['value']<70 for p in demo['glucose']))
        self.assertEqual(demo['facts']['below54Count'],0)
        self.assertEqual(demo['facts']['coveredMinutes'],69)
        self.assertEqual(demo['facts']['coveragePct'],73)
        self.assertTrue(demo['synthetic'])
        self.assertFalse(demo['provenance']['clinicalValidation'])
        self.assertEqual(demo,build_demo())


if __name__=='__main__':
    unittest.main()
