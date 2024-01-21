# Extensible Splines
[![PyPI version](https://badge.fury.io/py/extensible-splines.svg)](https://badge.fury.io/py/extensible-splines)
[![Package](https://github.com/egoughnour/extensible-splines/actions/workflows/python-package.yml/badge.svg)](https://github.com/egoughnour/extensible-splines/actions/workflows/python-package.yml/badge.svg)
[![Publish](https://github.com/egoughnour/extensible-splines/actions/workflows/python-publish.yml/badge.svg)](https://github.com/egoughnour/extensible-splines/actions/workflows/python-publish.yml/badge.svg)
[![codecov](https://codecov.io/gh/egoughnour/extensible-splines/graph/badge.svg?token=MELC9EGTYU)](https://codecov.io/gh/egoughnour/extensible-splines)

Python Spline Interpolation. Interactive plot for quick testing of new spline kernels or control point usage.  

## Why?

If you look at the source of `extensible_splines/splines.py` you will notice that the most commonly used varieties of spline can be defined with only one or two of four possible overloads or attribute definitions relative to the base class.

1. The kernel itself. That is, the square matrix by which we will multiply the powers of the parameter--in the form of a vector.
2. The scaling factor.  This defaults to 1.0, but supplying a value on the open unit interval is fine.
3. Any filter on the segments themselves.
4. How to transform the knots. In the case of the Hermite spline, this is p0, (δx,δy), p2, (δx,δy).  Points p0 and p2 are unchanged, but p1 and p3 are tranformed to relative offsets from p0 and p2, respectively.

# Installation

````
pip install extensible-splines
````

# Usage

![bspline_usage](https://github.com/egoughnour/extensible-splines/assets/457471/4e9676a4-6c33-4a98-889e-93bc47dae9cc)

### Create an instance of `SplineMatrix`
For example:

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
# Kernel instance and Spline class go here
# ....
##

def main():
    editor = interactive.SplineEditor(MySpline())
    editor.init_figure(caption='Testing New Splines')


if __name__ == '__main__':
    main()
````
