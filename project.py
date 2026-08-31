from __future__ import annotations
import math
from PIL import Image


screen = 80, 64
focal_length = 64
screen_rel = screen[0] / focal_length, screen[1] / focal_length
sub_div = 8
sub_div_ = 1 / sub_div
Z_maximum = 2 << 7
Z_minimum = 0
img = Image.new('RGB', screen, color='black')


class vector:
    def __init__(self, array):
        self.array = list(array)

    def __len__(self):
        return len(self.array)

    def __iter__(self):
        return iter(self.array)

    def __getitem__(self, index):
        return self.array[index]

    def __setitem__(self, index, value):
        self.array[index] = value

    def __eq__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        return self.array == other.array

    def __repr__(self):
        return f"vector({self.array})"

    def _check_len(self, other):
        if len(self.array) != len(other.array):
            raise ValueError(
                f"vector length mismatch: {len(self.array)} vs {len(other.array)}"
            )

    def __add__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self._check_len(other)
        return vector([a + b for a, b in zip(self.array, other.array)])

    def __sub__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self._check_len(other)
        return vector([a - b for a, b in zip(self.array, other.array)])

    def __neg__(self):
        return vector([-a for a in self.array])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vector([a * other for a in self.array])
        if isinstance(other, vector):
            self._check_len(other)
            return sum(a * b for a, b in zip(self.array, other.array))
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return vector([a * other for a in self.array])
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return vector([a / other for a in self.array])
        return NotImplemented

    def magnitude(self):
        return math.sqrt(sum(a * a for a in self.array))

    def normalized(self):
        m = self.magnitude()
        if m == 0:
            raise ZeroDivisionError("cannot normalize a zero-length vector")
        return self / m



def sign(a):
    return a >= 0


def cross(vec1: list[int], vec2: list[int]) -> int:
    return vec1[0] * vec2[1] - vec2[0] * vec1[1]


def DoBelong(point: list[int], interval: list[int])  -> bool:
    point = list(map(abs, point))
    if point[0] <= interval[0] / 2 and point[1] <= interval[1] / 2:
        return  True
    else:
        return False 


def DoIntersect(line: list[list[int]]) -> bool:
    vec1 = [screen[0] / 2 - line[0][0], screen[1] / 2 - line[0][1]]
    vec2 = [-1 * screen[0] / 2 - line[0][0], screen[1] / 2 - line[0][1]]
    vec3 = [-1 * screen[0] / 2 - line[0][0], -1 * screen[1] / 2 - line[0][1]]
    vec4 = [screen[0] / 2 - line[0][0], -1 * screen[1] / 2 - line[0][1]]

    border1 = min(line[0][0], line[1][0]) <= screen[0] / 2 <= max(line[0][0], line[1][0])
    border2 = min(line[0][1], line[1][1]) <= screen[1] / 2 <= max(line[0][1], line[1][1])
    border3 = min(line[0][0], line[1][0]) <= -1 * screen[0] / 2 <= max(line[0][0], line[1][0])
    border4 = min(line[0][1], line[1][1]) <= -1 * screen[1] / 2 <= max(line[0][1], line[1][1])

    vec_main = [line[1][0] - line[0][0], line[1][1] - line[0][1]]

    
    if border1 or border2:
        point1 = cross(vec1, vec_main)
    if border2 or border3:
        point2 = cross(vec2, vec_main)
    if border3 or border4:
        point3 = cross(vec3, vec_main)
    if border4 or border1:
        point4 = cross(vec4, vec_main)

    # print(border1, border2, border3, border4)
    # print(vec1, vec2, vec3, vec4, vec_main)
    # print(point1, point2, point3, point4)
        
    if border2 and (sign(point1) ^ sign(point2)):
        return True
    elif border3 and (sign(point2) ^ sign(point3)):
        return True
    elif border4 and sign(point3) ^ sign(point4):
        return True
    elif border1 and sign(point4) ^ sign(point1):
        return True
    else:
        return False


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
    for i in range(3):
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


def choose_direction(p0: list[int, int],
                     p1: list[int, int],
                     p2: list[int, int]) -> str | int:
    #0 - x+ y+ 1 - x+ y- 2 - x- y+ 3 - x- y-
    min_max = [[], []]
    min_max[0][0].append(min(p0[0], p1[0], p2[0])) # minimum x
    min_max[0][1].append(max(p0[0], p1[0], p2[0])) # maximum x
    min_max[1][0].append(min(p0[1], p1[1], p2[1])) # minimum y
    min_max[1][1].append(max(p0[1], p1[1], p2[1])) # maximum y
    for i in range(4):
        if p0[0] == min_max[0][i // 2] or p0[1] == min_max[1][i % 2]:
            return i, 0
        if p0[0] == min_max[0][i // 2] and p0[1] == min_max[1][i % 2]:
            return i, 0
        if p0[0] == min_max[0][i // 2] and p0[1] == min_max[1][i % 2]:
            return i, 0


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


def on_screen(points: list[int]) -> bool:
    # checks if any point in 3d when projected is on screen
    return abs(points[0]) <= abs(points[2]) * screen_rel[0]\
       and abs(points[1]) <= abs(points[2]) * screen_rel[1]\
       and points[2] >= 0


def min_line_on_screen(start_point, end_point):
    # computes the nearest point on start_end vector closest to start point
    """
    if isinstance(start_point, vector):
        start_point = start_point.array

    if isinstance(end_point, vector):
        end_point = end_point.array"""

    vec_chang = sub_div_ * (end_point - start_point)
    point = start_point

    for i in range(sub_div):
        if on_screen(point.array):
            return point.array
        point += vec_chang

    if on_screen(point.array):
        return point.array
    else:
        return False


def clip_line(dt_: list[float], t0_: list[float], plane_index: int) -> float:
    dtx, dty, dtz = dt_
    t0x, t0y, t0z = t0_

    match plane_index:
        case 1:
            # plane x = srx * z
            return (screen_rel[0] * t0z - t0x) / (dtx - screen_rel[0] * dtz)
        case 2:
            # plane x = -srx * z
            return -(screen_rel[0] * t0z + t0x) / (dtx + screen_rel[0] * dtz)
        case 3:
            # plane x = sry * z
            return (screen_rel[1] * t0z - t0y) / (dty - screen_rel[1] * dtz)
        case 4:
            # plane x = -sry * z
            return -(screen_rel[1] * t0z + t0y) / (dty + screen_rel[1] * dtz)
        case 5:
            # z = Z_maximum
            return (Z_maximum - t0z) / dtz
        case 5:
            # z = Z_minimum
            # while z_minimum = 0 shouldnt be called
            return (Z_minimum - t0z) / dtz


        

def compute_end_points(vectors: list[list[int]]):
    """
    Computes end(minimum amd maximum u,v ∈ [0, 1] 0; 1/8 ,..., 1) points of a lines in square which are on a screen

    18 lines 0-9 u or v
    """
    start_points = []
    end_points = []
    start_point = vector([vectors[0], vectors[0]])
    end_point = vector([vectors[1], vectors[2]])
    v0, v1, v2 = vector(vectors[0]), vector(vectors[1]), vector(vectors[2])
    start_point = [v0, v0]
    end_point = [v1, v2]
    delta_v = v1 - v0, v2 - v0
    sub_delta_v = [sub_div_ * delta_v[0], sub_div_ * delta_v[1]]

    for i in range(sub_div):
        start_points.append(min_line_on_screen(start_point[0], end_point[0])) # u
        end_points.append(min_line_on_screen(end_point[0], start_point[0]))
        start_points.append(min_line_on_screen(start_point[1], end_point[1])) # v
        end_points.append(min_line_on_screen(end_point[1], start_point[1]))

        start_point[0] += sub_delta_v[0]
        start_point[1] += sub_delta_v[1]
        end_point[0] += sub_delta_v[1]
        end_point[1] += sub_delta_v[0]
        
    start_points.append(min_line_on_screen(start_point[0], end_point[0])) # u
    end_points.append(min_line_on_screen(end_point[0], start_point[0]))
    start_points.append(min_line_on_screen(start_point[1], end_point[1])) # v
    end_points.append(min_line_on_screen(end_point[1], start_point[1]))

    return [start_points, end_points]


"""v1 = vector([1, 2, 3])
v2 = vector([2, 3, 4])
n = 5
print((v1 + v2).array)
print((n * v1). array)
print(v1[0], v2[2], v1[n])
for i in range(10):
    v1 += v2
print(v1.array)"""

vect1 = [-1, -1, 8]
vect2 = [-1, 1, 8]
vect3 = [1, -1, 8]
special_points = compute_end_points([vect1, vect2, vect3])
for point in special_points[0]:
    img.putpixel(project_vertex(point), (0, 0, 255))

for point in special_points[1]:
    img.putpixel(project_vertex(point), (0, 255, 0))

img.save('test.png')
