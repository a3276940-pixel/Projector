from __future__ import annotations
import math
import re
from PIL import Image
import ctypes
import os

os.add_dll_directory(r"C:\msys64\ucrt64\bin")

vector_library = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector.dll"))
screen = 80, 64
focal_length = 64
screen_rel = screen[0] / (2 * focal_length), screen[1] / (2 * focal_length)
sub_div = 8
sub_div_ = 1 / sub_div
Z_maximum = 2 << 7
Z_minimum = 0


class vector(ctypes.Structure):
    _fields_ = [
        ("components", ctypes.POINTER(ctypes.c_float)),
        ("dimensions", ctypes.c_int)
    ]

    def __init__(self, array):
        arr = (ctypes.c_float * len(array))(*array)
        built = _lib.vector_from_array(arr, len(array))
        self.components = built.components
        self.dimensions = built.dimensions
        built.components = None   # transfer ownership — stop built.__del__ from freeing our buffer
    
    def __del__(self):
        try:
            if self.components:
                _lib.free_vector(ctypes.byref(self))
        except (ValueError, AttributeError):
            pass

    def __len__(self):
        return self.dimensions

    def __iter__(self):
        return (self.components[i] for i in range(self.dimensions))

    def __getitem__(self, index):
        if not 0 <= index < self.dimensions:
            raise IndexError("vector index out of range")
        return self.components[index]

    def __setitem__(self, index, value):
        if not 0 <= index < self.dimensions:
            raise IndexError("vector index out of range")
        self.components[index] = value

    @property
    def array(self):
        return self  # already sequence-like: index/iterate/len read the C buffer

    @array.setter
    def array(self, values):
        values = list(values)
        arr = (ctypes.c_float * len(values))(*values)
        built = _lib.vector_from_array(arr, len(values))
        if self.components:
            _lib.free_vector(ctypes.byref(self))
        self.components = built.components
        self.dimensions = built.dimensions

    def __repr__(self):
        return f"vector({list(self)})"

    def __eq__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        if self.dimensions != other.dimensions:
            return False
        return list(self) == list(other)

    def check_len(self, other):
        if self.dimensions != other.dimensions:
            raise ValueError("Vector length mismatch")

    def __add__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self.check_len(other)
        return _lib.vector_add(self, other)

    def __sub__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self.check_len(other)
        return _lib.vector_subtract(self, other)

    def __neg__(self):
        return _lib.vector_negate(self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vector([a * other for a in self])
        if isinstance(other, vector):
            self.check_len(other)
            return _lib.vector_scalar_mul(self, other)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return vector([a * other for a in self])
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return _lib.vector_div(self, ctypes.c_float(other))
        return NotImplemented

    def magnitude(self):
        return _lib.vector_magnitude(self)

    def normalized(self):
        if self.magnitude() == 0:
            raise ZeroDivisionError("cannot normalize a zero-length vector")
        return _lib.vector_normalized(self)

    def __matmul__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self.check_len(other)
        if self.dimensions not in (2, 3):
            raise ValueError(
                f"cross product requires 2D or 3D vectors, got length {self.dimensions}"
            )
        result = _lib.vector_multiplication(self, other)
        if result.dimensions == 1:
            return result.components[0]  # matches original: 2D "cross" is a scalar
        return result

def _configure_lib(lib):
    lib.vector_from_array.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int]
    lib.vector_from_array.restype = vector

    lib.vector_add.argtypes = [vector, vector]
    lib.vector_add.restype = vector

    lib.vector_subtract.argtypes = [vector, vector]
    lib.vector_subtract.restype = vector

    lib.vector_negate.argtypes = [vector]
    lib.vector_negate.restype = vector

    lib.vector_div.argtypes = [vector, ctypes.c_float]
    lib.vector_div.restype = vector

    lib.vector_magnitude.argtypes = [vector]
    lib.vector_magnitude.restype = ctypes.c_float

    lib.vector_normalized.argtypes = [vector]
    lib.vector_normalized.restype = vector

    lib.vector_multiplication.argtypes = [vector, vector]
    lib.vector_multiplication.restype = vector

    lib.free_vector.argtypes = [ctypes.POINTER(vector)]
    lib.free_vector.restype = None

    lib.vector_scalar_mul.argtypes = [vector, vector]
    lib.vector_scalar_mul.restype = ctypes.c_float

    return lib


_lib = _configure_lib(vector_library)

def DoBelong(point: list[int], interval: list[int])  -> bool:
    point = list(map(abs, point))
    if point[0] <= interval[0] / 2 and point[1] <= interval[1] / 2:
        return  True
    else:
        return False 

def DoIntersect(line: list[list[int]]) -> bool:
    vec = [None] * 4
    for i in range(4):
        corner = [(1 if (i - 1) // 2 != 0 else -1) * screen[0] >> 1, (1 if i // 2 == 0 else -1) * screen[1] >> 1]
        vec[i] = corner - line[0]
    
    def point_type_position(point):
        def point_interval_div(point, interval):
            if interval[0] > point:
                return 0
            if interval[0] <= point <= interval[1]:
                return 1
            return 2

        position = [point_interval_div(point[0], [-screen[0] >> 1, screen[0] >> 1]),\
                    point_interval_div(point[1], [-screen[1] >> 1, screen[1] >> 1])]

        # 0 1 | 1 0 | 2 1 | 1 2
        point_type = (2 if abs(position[1] - position[0]) == 1 else 1)
        return point_type, position

    point0 = point_type_position(line[0])
    point1 = point_type_position(line[1])

    # checks if points are completely outside
    if any(point0[1][i] == point1[1][i] != 1 for i in range(2)):
        return False

    # checks if points cross the rectangle diagonally
    if point0[0] == point1[0] == 2:
        return True

    # checks if both points are on row/column 1 => intersect rectangle
    if point0[0] == point1[0] == 1:
        if point0[1][0] == point1[1][0] or point0[1][1] == point1[1][1]:
            return True

    # position encoding to vector class
    point0_ = vector(point0[1]) - vector([1, 1])
    point1_ = vector(point1[0]) - vector([1, 1])

    def pos_to_corners(type_: int, pos: vector) -> list[vector]:

        if type_ == 2:
            return [pos]

        # type 1
        # delta vector is just change in direction
        #  1 0 and 0 -1 if point is at position -1 0 or 0 1 line which div space with frustrum is horizontal
        delta_vec = vector([(0 if pos[0] == 0 else 1), (0 if pos[1] == 0 else 1)])

        return [pos + delta_vec, pos - delta_vec]

    corner_to_check = [x for x in pos_to_corners(point0[0], point0_) if x in set(pos_to_corners(point1[0], point1_))][0]

    return (-point0_ @ (corner_to_check - point0_) >= 0) == (line[1] - line[0])\
          @ (vector(corner_to_check[0] * screen[0] / 2 + corner_to_check[1] * screen[1] / 2) >= 0)

def PolygonOnScreen(points: list[list[int]]) -> bool:
    minx = min(p[0] for p in points)
    miny = min(p[1] for p in points)
    maxx = max(p[0] for p in points)
    maxy = max(p[1] for p in points)
    
    if (DoBelong([minx, miny], screen)\
    and DoBelong([maxx, maxy], screen))\
    or (maxx >= screen[0] / 2 and minx <= -1 * screen[0] / 2\
    and maxy >= screen[1] / 2 and miny <= -1 * screen[1] / 2):
        return True
    for i in range(len(points)):
        if DoIntersect([points[i], points[i - 1]]):
            return True
    return False

def project_vertex(vertex: list[float]) -> list[int]:
    x, y, z = vertex[0], vertex[1], vertex[2]
    if z == 0:
        return
    x_projected = int(focal_length * x // z) + screen[0] // 2
    y_projected = int(focal_length * y // z) + screen[1] // 2
    return x_projected, y_projected

def orientation(p1: list[int, int, int], p2: list[int, int, int], p3: list[int, int, int], normal=(0, 0, 1)):
    """
    Determine if three points are clockwise (CW), counterclockwise (CCW), or collinear
    when projected onto a plane defined by a normal vector.

    Args:
        p1, p2, p3: Tuples/lists of 3D coordinates (x, y, z).
        normal: Normal vector of the projection plane (default: z-plane).

    Returns:
        "True or False"
    """
    v1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    v2 = (p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])

    cross = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )

    dot = cross[0] * normal[0] + cross[1] * normal[1] + cross[2] * normal[2]

    if math.isclose(dot, 0, abs_tol=1e-9):
        return True
    elif dot > 0:
        return False
    else:
        return True

def on_screen(points: vector) -> bool:
    # checks if any point in 3d when projected is on screen
    return abs(points[0]) <= abs(points[2]) * screen_rel[0]\
       and abs(points[1]) <= abs(points[2]) * screen_rel[1]\
       and points[2] >= Z_minimum\
       and points[2] <= Z_maximum

def main() -> None:
    return

if __name__ == "__main__":
    main()
