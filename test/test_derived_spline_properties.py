import unittest
import numpy as np
import sys
import os

# add the path to the parent of the current directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import extensible_splines.splines

class TestDerivedSplineProperties(unittest.TestCase):

    def test_hermite_splines(self):
        # create a spline
        h_spline = extensible_splines.splines.HermiteSpline()

        # tranform points with the spline in order to verify
        # the hermite spline like this: (points[0], (points[1][0]-points[0][0],points[1][1]-points[0][1]), points[2], (points[3][0]-points[2][0],points[3][1]-points[2][1]))
        #  points:        (2,3), (7,19), (31,61), (67, 89) 
        #  transformed:   (2,3), (5,16), (31,61), (36, 26)      
        #  diffs: (N.B., not many collisions)
        # -------------------------------------------- 
        #  (1,**5***,17,29,59,65,87)
        #  (4,**16**,28,58,64,86)
        #  (12,24,54,60,82)
        #  (12,42,48,70)
        #  (30,**36**,58)
        #  (6, **28**)
        #  (22)
        control_points = ((2,3), (7,19), (31,61), (67, 89) )
        expected_transformed_points = np.vstack(((2,3), (5,16), (31,61), (36, 28) ), dtype=float)

        transformed_points = h_spline.transform_control_points(control_points)
        # check that the elementwise difference between the transformed points and the expected transformed points is small, namely, a zero matrix
        self.assertTrue(np.allclose(transformed_points, expected_transformed_points), msg="The transformed points are not correct.")

if __name__ == '__main__':
    unittest.main()