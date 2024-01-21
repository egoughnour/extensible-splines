# Extensible Splines
[![PyPI version](https://badge.fury.io/py/extensible-splines.svg)](https://badge.fury.io/py/extensible-splines)
[![Package](https://github.com/egoughnour/extensible-splines/actions/workflows/python-package.yml/badge.svg)](https://github.com/egoughnour/extensible-splines/actions/workflows/python-package.yml/badge.svg)
[![Publish](https://github.com/egoughnour/extensible-splines/actions/workflows/python-publish.yml/badge.svg)](https://github.com/egoughnour/extensible-splines/actions/workflows/python-publish.yml/badge.svg)
[![codecov](https://codecov.io/gh/egoughnour/extensible-splines/graph/badge.svg?token=MELC9EGTYU)](https://codecov.io/gh/egoughnour/extensible-splines)

Python Spline Interpolation. Interactive plot for quick testing of new spline kernels or control point usage.  

# Installation

````
pip install extensible-splines
````

# Usage

![bspline_usage](https://github.com/egoughnour/extensible-splines/assets/457471/4e9676a4-6c33-4a98-889e-93bc47dae9cc)

### Create an instance of `SplineMatrix`
For instance:

````
my_kernel = SplineMatrix(np.array([[1, 0, 0, 0],[0, 1, 0, 0],[-3, -2, 3, -1],[2, 1, -2, 1]],float))
````

### Define a Subclass of `BaseSpline`
This can be as simple as (1) defining the abstract methods with super calls and (2) passing the kernel to the base constructor.

````
class MySpline(BaseSpline):
    def __init__(self) -> None:
        super().__init__(my_kernel)
    
    def filter_segments(self, raw_segments: Iterable[Tuple[Tuple[int, int]]]):
        return super().filter_segments(raw_segments)

    def transform_control_points(self, points: Tuple[Tuple[int, int]]) -> np.ndarray:
        return super().transform_control_points(points)
````

Notice that other than super() calls and type hinting, the kernel is the only aspect of the type definition to be handled above.

### Test the New Spline Interactively

````
import splines
import interactive

# Kernel instance and Spline class go here
# ....
##

def main():
    editor = interactive.SplineEditor(MySpline())
    editor.init_figure(caption='Testing New Splines')


if __name__ == '__main__':
    main()
````
