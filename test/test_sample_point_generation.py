import unittest
import extensible_splines.splines as es

class TestSamplePointGeneration(unittest.TestCase):
    def test_sample_points_not_mutated(self):
        spline = es.HermiteSpline()
        spline.set_control_points({i: i for i in range(5)})
        interpolant = es.Interpolant(spline)
        pts = interpolant.get_all_points_all_segments(5)
        expected_len = 5 * len(spline.segments) + 1
        self.assertEqual(len(pts), expected_len)
        # verify the second segment does not start with duplicate point
        first_seg_len = 5  # points_per_segment
        self.assertNotEqual(pts[first_seg_len], pts[first_seg_len + 1])

if __name__ == '__main__':
    unittest.main()
