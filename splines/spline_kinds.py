from abc import ABC, abstractmethod  
from dataclasses import dataclass, field
from typing_extensions import override
import numpy as np
from itertools import islice, tee
from typing import Dict, Iterable, List, Tuple

@dataclass
class SplineMatrix:
    kernel: np.ndarray
    scale_factor: float = field(default=1.0)


class BaseSpline(ABC):
    def __init__(self, mat: SplineMatrix) -> None:
        self.matrix = mat
        self.control_points = {}
        self.segments = None
        self.min_points_needed = 4

    def set_control_points(self, new_points: Dict[int,int]):
        """
        re-assign the set of control points. This causes the segments to change, meaning
        the segment matrix must be recalculated for each.
        """
        self.control_points = new_points
        self.set_segments_from_control_points()

    def get_segment_items(self):
        iters = tee(self.control_points.items(), 4)
        for i, it in enumerate(iters):
            next(islice(it, i, i), None)
        return zip(*iters)

    @abstractmethod
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int,int]]]):
        return list(raw_segments)

    @abstractmethod
    def transform_control_points(self, points:Tuple[Tuple[int,int]]) -> np.ndarray:
        return np.vstack(points, dtype=float)

    def set_segments_from_control_points(self) -> None:    
        self.segments = []
        for seg in self.filter_segments(self.get_segment_items()):
            self.segments.append((self.matrix.kernel @ self.transform_control_points(seg))*self.matrix.scale_factor)

HSM = SplineMatrix(np.array([[1, 0, 0, 0],[0, 1, 0, 0],[-3, -2, 3, -1],[2, 1, -2, 1]],float))

BSM = SplineMatrix(np.array([[1, 4, 1, 0],[-3, 0, 3, 0],[3, -6, 3, 0],[-1, 3, -3, 1]], float), 1/6.0)

BezM = SplineMatrix(np.array([[1, 0, 0, 0],[-3, 3, 0, 0],[3, -6, 3, 0],[-1, 3, -3, 1]], float))

QuadBezM = SplineMatrix(np.array([[1, 0, 0, 0],[-2, 2, 0, 0],[1, -2, 1, 0],[0, 0, 0, 0]], float))

CatRomM = SplineMatrix(np.array([[0, 2, 0, 0],[-1, 0, 1, 0],[2, -5, 4, -1],[-1, 3, -3, 1]],float), 0.5)

class HermiteSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(HSM)

    @override
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    @override
    def transform_control_points(self, points:Tuple[Tuple[int,int]]) -> np.ndarray:
        transformed = (points[0], (points[1][0]-points[0][0],points[1][1]-points[0][1]), points[2], (points[3][0]-points[2][0],points[3][1]-points[2][1])) 
        return np.vstack(transformed, dtype=float)
    
class BSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(BSM)
    
    @override
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    @override
    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)

class BezierSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(BezM)
    
    @override
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        whole_list = list(raw_segments)
        return list(whole_list[0::3])

    @override
    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)

class QuadraticBezierSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(QuadBezM)

    @override
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        whole_list = list(raw_segments)
        # should be able to use same logic as cubic implementation, maybe
        # justification is that the kernel ought to take care of each fourth control point
        # (By multiplying it with zero)
        # TODO verify this is workable with this implementation
        return list(whole_list[0::3])
    
    @override
    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)


class CatmullRomSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(CatRomM)
    
    @override
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    @override
    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)