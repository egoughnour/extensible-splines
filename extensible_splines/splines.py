from abc import ABC, abstractmethod  
from dataclasses import dataclass, field
import numpy as np
from itertools import islice, tee
from typing import Dict, Iterable, List, Tuple

#Spline and Matrix classes

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

    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    def transform_control_points(self, points:Tuple[Tuple[int,int]]) -> np.ndarray:
        transformed = (points[0], (points[1][0]-points[0][0],points[1][1]-points[0][1]), points[2], (points[3][0]-points[2][0],points[3][1]-points[2][1])) 
        return np.vstack(transformed, dtype=float)
    
class BSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(BSM)
    
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)

class BezierSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(BezM)
    
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        whole_list = list(raw_segments)
        return list(whole_list[0::3])

    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)

class QuadraticBezierSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(QuadBezM)

    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        whole_list = list(raw_segments)
        # should be able to use same logic as cubic implementation, maybe
        # justification is that the kernel ought to take care of each fourth control point
        # (By multiplying it with zero)
        # TODO verify this is workable with this implementation
        return list(whole_list[0::3])
    
    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)


class CatmullRomSpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(CatRomM)
    
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)

# End of Spline and Matrix classes

#  
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

# Interpolant and Centroid classes

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


def signed_area_by_triangulation(points:List[complex]) -> float:
    """
    Signed area of a point cloud by triangulation. Strictly we're using trapezoids, but this is equivalent.
    """
    if points[0] != points[-1]:
        points.append(points[0])
    area = 0.0
    for i in range(len(points)-1):
        area += (points[i+1].imag + points[i].imag)*(points[i].real - points[i+1].real)
    return area/2.0



# End of Interpolant and Centroid classes
    
# Editor class
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from typing import TypeVar, Generic
import math

SplineType = TypeVar('SplineType', bound=BaseSpline)
# SplineEditor, enables click and drag editing of knots, visualization of the series of knots and of the path generated by them
class SplineEditor(Generic[SplineType]):
    """click and drag spline knot editor"""
    def __init__(self, spline: SplineType, point_click_distance_min=3.0, points_per_segment=20, interpolant_fmt: str="b", knot_line_fmt: str="r") -> None:
        self.figure = None
        self.axes = None
        self.line = None
        self.interpolant = Interpolant(spline)
        self.points = {}
        self.knot_line = None
        self.click_epsilon_dist = point_click_distance_min
        self.points_per_segment = points_per_segment
        self.interpolant_fmt = interpolant_fmt
        self.knot_line_fmt = knot_line_fmt
        self.extent: tuple[int,int] = None
        self.knot_moving = None
        #TODO decide whether to init figure, axes, handlers in init. Probably should separate this

    def init_figure(self, caption:str, extent:tuple[int,int] = (100,100)) -> None:
        """initialize figure and show"""
        self.extent = extent
        self.figure = plt.figure(caption)
        self.axes = plt.subplot()
        self.axes.set_xlim(0, extent[0])
        self.axes.set_ylim(0, extent[1])
        self.axes.set_aspect('equal')
        self.axes.set_title('Click and drag to edit knots')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.axes.grid(which='both')
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        plt.show()

    def add_knot(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)
        self.points[x] = y
        self.interpolant.spline.set_control_points(self.points)
        return x, y
    
    def remove_knot(self, x, _):
        if x in self.points:
            del self.points[x]
            self.interpolant.spline.set_control_points(self.points)

    def on_click(self, event):
        #check that we have left click and are in the axes
        if event.button == 1 and event.inaxes == self.axes:
            point = self.get_nearest_point(event)
            if point:
                # we found a point so we're moving it
                self.knot_moving = point
            else:
                self.add_knot(event)
            self.update_graph()
        elif event.button == 3 and event.inaxes == self.axes:
            point = self.get_nearest_point(event)
            if point:
                self.remove_knot(*point)
                self.update_graph()

    def update_graph(self) -> None:
        #if no points are defined, clear the line data.
        #otherwise if the minimum number of points is defined,
        #update the line data with the interpolant and the knot_line data with the knots (i.e, the points)
        #let the interpolant.spline determine the minimum number of points needed.
        # interpolant will determine rotation (if any)
        if not self.points:
            self.line.set_data([], [])
            self.knot_line.set_data([], [])
        else:
            if len(self.points) >= self.interpolant.spline.min_points_needed:
                theta = self.interpolant.rotation_angle
                # first get the interpolant and knot data
                # then if self.line is not defined, plot to create it and the line tracing out the knots
                # otherwise update the line data with the interpolant and the knot_line data with the knots (i.e, the points)
                # finally draw
                x, y = zip(*self.interpolant.get_all_points_all_segments(self.points_per_segment, theta))
                x_knot, y_knot = zip(*list(self.points.items()))
                if not self.line:
                    self.line, = self.axes.plot(x, y, self.interpolant_fmt)
                    line_between_knots, = self.axes.plot(x_knot, y_knot, self.knot_line_fmt)
                    self.knot_line = self.axes.add_line(line_between_knots)
                else:
                    self.line.set_data(x, y)
                    self.knot_line.set_data(x_knot, y_knot)
        self.figure.canvas.draw()

    def on_motion(self, event):
        if not self.knot_moving:
            return
        if event.xdata is None or event.ydata is None:
            return
        self.remove_knot(*self.knot_moving)
        self.knot_moving = self.add_knot(event)
        self.update_graph()

    def on_release(self, event):
        if event.button == 1 and event.inaxes == self.axes and self.knot_moving:
            self.knot_moving = None
            self.update_graph()

    def get_nearest_point(self, event):
        nearest_point = None
        # initially set the minimum distance so that it is larger than any possible point
        # this will vary given the extent of the plot/figure/axes
        min_distance_found = math.hypot(self.extent[0], self.extent[1])
        for x,y in self.points.items():
            dist = math.hypot(event.xdata - x, event.ydata - y)
            if dist < min_distance_found:
                min_distance_found = dist
                nearest_point = (x,y)
        if min_distance_found <= self.click_epsilon_dist:
            return nearest_point
        return None

# End of Editor class
# LineSegment class
import cmath

PATH_CRUFT_START = "<path xmlns=\"http://www.w3.org/2000/svg\" id=\""
PATH_CRUFT_MIDDLE = "\" fill=\"none\" stroke=\"black\" stroke-width=\"1\" d=\"M "
PATH_CRUFT_END = "\"></path>"
PATH_PARSER_DELIMITER = " d=\"M "

@dataclass
class LineSegment:
    start: complex
    end: complex
    length: float = None
    angle: float = None
    def __post_init__(self):
        self.length =  abs(self.end - self.start)
        self.angle = cmath.phase(self.end-self.start)

    def __add__(self, other):
        normal =-1.0*np.exp(1j*((math.pi/2.0)+self.angle))
        if isinstance(other, int) or isinstance(other, float):
            return LineSegment(self.start+other*normal, self.end+other*normal)
        raise TypeError(f"unsupported operand type(s) for +: 'LineSegment' and '{type(other)}'")
    
    def reverse(self):
        return LineSegment(self.end, self.start)

    def as_svg_fragment(self, initial=False):
        if initial:
            return f"{self.start.real} {self.start.imag} L {self.end.real} {self.end.imag}"
        return f"L {self.end.real} {self.end.imag}"

class Box:
    def __init__(self, line: LineSegment, width, id) -> None:
        self.path_element = line
        self.parallel: LineSegment = (line + width).reverse()
        self.fourth_edge = LineSegment(self.parallel.end, self.path_element.start)
        self.second_edge = LineSegment(self.path_element.end, self.parallel.start)
        self.id = id
    #TODO handle tabs
    def as_svg_path(self):
        return f"{PATH_CRUFT_START}{self.id}{PATH_CRUFT_MIDDLE} {self.path_element.as_svg_fragment(initial=True)} {self.second_edge.as_svg_fragment()} {self.parallel.as_svg_fragment()} {self.fourth_edge.as_svg_fragment()}{PATH_CRUFT_END}"

class TablessNet:
    """
    This is the net corresponding to the prism we take as input.  Currently has no tabs.
    """
    def __init__(self, svg_path: str, prism_height, generated_path_prefix:str='box_'):
        self.box_width = prism_height
        self.generated_path_prefix = generated_path_prefix
        path_guts = svg_path.split(PATH_PARSER_DELIMITER)[-1]
        path_guts = path_guts.removesuffix(PATH_CRUFT_END)
        if '"' in path_guts:
            path_guts = path_guts.split('"')[0]
        self.path = []
        points =[complex(float(w.split()[0]),float(w.split()[-1])) for w in path_guts.split(' L ')]
        #now we check for--and prevent (!)--mathematically negative traversal
        area = signed_area_by_triangulation(points)
        if area < 0:
            points.reverse()
        for i in range(len(points)-1):
            self.path.append(LineSegment(points[i], points[i+1]))
        self.boxes = [Box(line, self.box_width, generated_path_prefix+str(i)) for i, line in enumerate(self.path)]
        self.generated_paths = [box.as_svg_path() for box in self.boxes]
    
    def __str__(self):
        return '\n'.join(self.generated_paths)


