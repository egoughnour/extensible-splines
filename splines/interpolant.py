import numpy as np
from .spline_kinds import BaseSpline
from typing import List, Tuple

#polynomial terms
powers = np.array([0,1,2,3], int)

#convenience methods
def get_elements(arr):
    return arr[0], arr[1]

def get_sample_points(number_of_points:int):
    return [m/float(number_of_points) for m in range(1, number_of_points)]

def correct_sample_ends(raw_points:List[float], is_final:bool=False):
    raw_points.insert(0,0.0)
    if is_final:
        raw_points.append(1.0)
    return raw_points


class Interpolant:
    def __init__(self, spline:BaseSpline) -> None:
        self.spline = spline
    
    def evaluate_on_kth_segment(self, k:int, tfrs: list[float]) -> List[Tuple[float]]:
        """
        Evaluate tfrs, the fractional parts traversed on the interval [0,1] projected onto segment k.
        """
        return [get_elements((t**powers) @ self.spline.segments[k]) for t in tfrs]
    
    def get_all_points_all_segments(self, points_per_segment:int, theta:float = 0.0) -> List[Tuple[float]]:
        """
        Get all points on all segments.
        """
        points = []
        sample_points = get_sample_points(points_per_segment)
        for k in range(len(self.spline.segments)):
            if k == len(self.spline.segments) - 1:
                points += self.evaluate_on_kth_segment(k, correct_sample_ends(sample_points, is_final=True))
            else:
                points += self.evaluate_on_kth_segment(k, correct_sample_ends(sample_points))    
        if theta != 0.0:
            self.centroid = Centroid(points)
            self.centroid.rotate(theta)
            return self.centroid.as_tuple_list()
        return points

    @property
    def rotation_angle(self) -> float:
        """angle to rotate the points interpolated. default implemntation does not rotate."""
        return 0.0

class Centroid:
    def __init__(self, point_cloud: List[Tuple[float]]) -> None:
        self.points = [complex(x,y) for x,y in point_cloud]
        if self.points:
            self.location = sum(self.points)/len(self.points)
            self.centered = [w - self.location for w in self.points]
            self.transformed = None

    def rotate(self, theta:float) -> None:
        self.transformed = [self.location + (w*np.exp(1j*theta)) for w in self.centered]

    def as_tuple_list(self) -> List[Tuple[float]]:
        return [(w.real, w.imag) for w in self.transformed]
