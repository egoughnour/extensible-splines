import unittest
import numpy as np
import sys
import os

# add the path to the parent of the current directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import extensible_splines.splines

#the SVG element we assume we are working with is something like this:
# <path xmlns="http://www.w3.org/2000/svg" id="Selection" fill="none" stroke="black" stroke-width="1" d="M 520 194.43 L 601.69 244 L 626.09 294.99 L 670 321.42 L 686.91 334.09 L 708.96 393 L 678 459.71 L 630.9 501 L 628 521 L 634 569 L 629.33 610 L 614.33 639 L 595 657.57 L 438 671 L 428 672.04 L 419 672.04 L 293 658.65 L 275.44 643 L 260.2 618 L 253 584 L 254.28 553 L 259 519 L 256.9 502 L 222 464.96 L 187 395 L 222 323.72 L 263.99 297.83 L 286.86 256 L 321 208.04 L 403 205.86 L 446 221.96 L 481 208.26 L 520 194.43 L 520 194.43"/>
# the line segments are defined by the d attribute of the path element, so we are only interested in the following:
# 520 194.43 L 601.69 244 L 626.09 294.99 L 670 321.42 L 686.91 334.09 L 708.96 393 L 678 459.71 L 630.9 501 L 628 521 L 634 569 L 629.33 610 L 614.33 639 L 595 657.57 L 438 671 L 428 672.04 L 419 672.04 L 293 658.65 L 275.44 643 L 260.2 618 L 253 584 L 254.28 553 L 259 519 L 256.9 502 L 222 464.96 L 187 395 L 222 323.72 L 263.99 297.83 L 286.86 256 L 321 208.04 L 403 205.86 L 446 221.96 L 481 208.26 L 520 194.43 L 520 194.43

RAW_POLYGON = '520 194.43 L 601.69 244 L 626.09 294.99 L 670 321.42 L 686.91 334.09 L 708.96 393 L 678 459.71 L 630.9 501 L 628 521 L 634 569 L 629.33 610 L 614.33 639 L 595 657.57 L 438 671 L 428 672.04 L 419 672.04 L 293 658.65 L 275.44 643 L 260.2 618 L 253 584 L 254.28 553 L 259 519 L 256.9 502 L 222 464.96 L 187 395 L 222 323.72 L 263.99 297.83 L 286.86 256 L 321 208.04 L 403 205.86 L 446 221.96 L 481 208.26 L 520 194.43 L 520 194.43'
PATH_TAG = '<path xmlns="http://www.w3.org/2000/svg" id="Selection" fill="none" stroke="black" stroke-width="1" d="M 520 194.43 L 601.69 244 L 626.09 294.99 L 670 321.42 L 686.91 334.09 L 708.96 393 L 678 459.71 L 630.9 501 L 628 521 L 634 569 L 629.33 610 L 614.33 639 L 595 657.57 L 438 671 L 428 672.04 L 419 672.04 L 293 658.65 L 275.44 643 L 260.2 618 L 253 584 L 254.28 553 L 259 519 L 256.9 502 L 222 464.96 L 187 395 L 222 323.72 L 263.99 297.83 L 286.86 256 L 321 208.04 L 403 205.86 L 446 221.96 L 481 208.26 L 520 194.43 L 520 194.43"/>'

class TestNetConstruction(unittest.TestCase):
    def test_net_construction(self):
        net_without_tabs = extensible_splines.splines.TablessNet(PATH_TAG, 20)
        text_lines = RAW_POLYGON.split(" L ")
        self.assertEqual(text_lines[0], text_lines[-1], msg="Path Not Closed. Over a closed path we assume first and last points are the same.")
        #  each 'L' represents a line segment.  This is basically a Dagwood sandwich.
        # thus, in a triangle, for instance, we expect 2 L's, 3 line segments, 3 points, but one with multiplicity 2.
        path_element_count = len(text_lines) - 1 # we look for N-1 because, to continue the previous analogy, we are looking at fillings, not bread slices.

        print(f"path elements in the original path: {path_element_count}")
        print(f"boxes in the net {len(net_without_tabs.boxes)}")

        self.assertEqual(path_element_count, len(net_without_tabs.boxes))
        
        print("Dumping the generated paths:")
        print(str(net_without_tabs))
        #TODO check that the svg fragment is well-formed?
        #TODO add tabs to the net and check them in another test (or two)
        #TODO add reflection (of n-1 `box.path_element` s) over (the center of one box). (This is creation of the lid)

if __name__ == '__main__':
    unittest.main()