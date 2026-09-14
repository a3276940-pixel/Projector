from __future__ import annotations
import math
from PIL import Image

# test

screen = 80, 64
focal_length = 64
screen_rel = screen[0] / (2 * focal_length), screen[1] / (2 * focal_length)
sub_div = 8
sub_div_ = 1 / sub_div
Z_maximum = 2 << 7
Z_minimum = 0


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

    def __matmul__(self, other):
        if not isinstance(other, vector):
            return NotImplemented
        self._check_len(other)
        n = len(self.array)
        if n == 2:
            ax, ay = self.array
            bx, by = other.array
            return ax * by - ay * bx
        if n == 3:
            ax, ay, az = self.array
            bx, by, bz = other.array
            return vector([
                ay * bz - az * by,
                az * bx - ax * bz,
                ax * by - ay * bx,
            ])
        raise ValueError(
            f"cross product requires 2D or 3D vectors, got length {n}"
        )


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
    vec = [None] * 4
    for i in range(4):
        corner = [(1 if (i - 1) // 2 != 0 else -1) * screen[0] >> 1, (1 if i // 2 == 0 else -1) * screen[1] >> 1]
        vec[i] = corner - line[0]


    def get_direction(A, B):
        # Map each cell to its clockwise order index
        order = {
            (1, 2): 0,
            (2, 1): 1,
            (1, 0): 2,
            (0, 1): 3
        }
    
        diff = (order[B] - order[A]) % 4
    
        return 1 if diff == 1 else -1
    

    def point_type_position(point):
        def point_interval_div(point, interval):
            if interval[0] > point:
                return 0
            if interval[0] <= point <= interval[1]:
                return 1
            return 2

        position = [point_interval_div(point[0], [-screen[0] > 1, screen[0] > 1]),\
                    point_interval_div(point[1], [-screen[1] > 1, screen[1] > 1])]

        # 0 1 | 1 0 | 2 1 | 1 2
        point_type = (2 if position[1] - position[0] == 1 else 1)
        return point_type, position

    point0 = point_type_position(line[0])
    point1 = point_type_position(line[1])
    if any(point0[1][i] == point1[1][i] and point0[1][i] in (0, 2) for i in range(2)):
        return False

    if point0[0] == point1[0] == 2:
        return True
    if point0[0] == point1[0] == 1:
        if point0[1][0] == point1[1][0] or point0[1][1] == point1[1][1]:
            return True

    
        


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
       and points[2] >= Z_minimum\
       and points[2] <= Z_maximum


def min_line_on_screen(start_point, end_point):
    # computes the nearest point on start_end vector closest to start point

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


def seperate_point_beetween_lines(line, point):
    # line is set as a point the line is from 0 0 to the point the other point is symetrical
    # returns if line is to the left in beetwen or right
    cross0 = cross(line, point)
    cross1 = cross((line[0], -line[1]), point)
    if (cross0 > 0) ^ (cross1 > 0):
        return 1 # inbeetwen
    if cross0 <= 0:
        return 0
    return 2


def point_space_div(point):
    # position is encoded in 3rd number system
    # and 1 3 5 and 7 are first type where we can know for sure the closest plane
    # 2 is for the volume it is in
    position = 3 * seperate_point_beetween_lines((screen[0], screen[2]), (point[0], point[2])) +\
                   seperate_point_beetween_lines((screen[1], screen[2]), (point[1], point[2]))
    point_type = (1 if position == 1 or position == 3 or position == 5 or position == 7 else 0)

    if Z_minimum < point[2] < Z_maximum and not on_screen(point):
        return point_type + 1, 2, position
    if point[2] > Z_maximum:
        return point_type + 1, 3, position
    if 0 <= point[2] <= Z_minimum:
        return point_type + 1, 1, position
    if point[2] < 0:
        return point_type + 1, 0, 8 - position


def closest_plane(line: vector, cross_mul: vector, planes: list[int]):
    x0, y0, z0 = line[0]
    x1, y1, z1 = line[1]
    dx, dy, dz = line[1] - line[0]

    for plane in planes:
        if plane[0] < 0 ^ plane[1] >= 0: # never enters 
            return None

    if on_screen(line[0]) or on_screen(line[1]):
        if on_screen(line[0]):
            return
    return


def nearest_entry(a, b, z0=Z_minimum, z1=Z_maximum, srx=screen_rel[0], sry=screen_rel[1]):
    """Closest point along a->b (t in [0,1]) that's inside the frustum,
    or None if the segment never enters. a itself may be inside already.
    Exactly one division. Call nearest_entry(b, a, ...) and use t_far = 1 - t
    to get the far point instead, when you need it."""
    # Claude vibecoded
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx-ax, by-ay, bz-az
    srx_az, srx_dz = srx*az, srx*dz
    sry_az, sry_dz = sry*az, sry*dz

    planes = (
        (az-z0, dz), (z1-az, -dz),
        (srx_az-ax, srx_dz-dx), (ax+srx_az, dx+srx_dz),
        (sry_az-ay, sry_dz-dy), (ay+sry_az, dy+sry_dz),
    )

    best_L0 = best_L1 = None
    check_list = []                        # satisfied-at-a, decreasing planes
    for L0, L1 in planes:
        if L0 < 0.0:
            if L1 <= 0.0:
                return None                # violated forever, never enters
            if best_L0 is None or best_L0*L1 - L0*best_L1 > 0.0:
                best_L0, best_L1 = L0, L1
        elif L1 < 0.0:
            check_list.append((L0, L1))

    if best_L0 is None:
        return a, 0.0                      # a already inside


    t = -best_L0 / best_L1
    if t > 1.0:
        return None


    for L0, L1 in check_list:              # confirm nothing else broke by then
        if L0 + t*L1 < 0.0:
            return None

    return (ax+t*dx, ay+t*dy, az+t*dz), t


def calculate_t0(dt_: list[float], t0_: list[float], plane_index: int) -> float:
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


def line_precomputation(start_point: list[int], end_point: list[int]) -> list[list[int]]:
    """Splits line intersection viewing frustrum into 3 general cases
    0, 1 or 2 intersection points and computes based on that only nedded intersection checks"""

    start_point_on_screen = on_screen(start_point)
    end_point_on_screen = on_screen(end_point)
    if start_point_on_screen and end_point_on_screen:
        start = start_point
        end = end_point
    elif start_point_on_screen ^ end_point_on_screen:
        if start_point_on_screen:
            start = start_point
            end = nearest_entry(end_point, start_point)
        else:
            start = nearest_entry(start_point, end_point)
            end = end_point
    else:
        start = nearest_entry(start_point, end_point)
        end = nearest_entry(end_point, start_point)

    return list[start, end]


def family_of_lines(delta_vec: vector, driv: vector, zero_point: vector, num_line: int) -> list[list[float]]:
    start_point = [] * num_line
    end_point = [] * num_line
    corners = [zero_point, zero_point + delta_vec, zero_point + 8 * driv, zero_point + delta_vec + 8 * driv]
    if all(on_screen(corner.array) for corner in corners):

        start_point[0] = zero_point
        end_point[0] = start_point[0] + delta_vec

        for index in range(num_line):
            start_point[index + 1] = start_point[index] + driv
            end_point[index + 1] = start_point[index + 1] + delta_vec

        return zip(start_point, end_point)
    cross_multiplication = [[[] * (5 if Z_minimum == 0 else 6)] * num_line]
    for _ in range(num_line + 1):
        #calculate all cross multiplcation for first line
        print()


    return


def compute_end_points(vectors: list[list[int]]):
    """
    Computes end(minimum amd maximum u,v ∈ [0, 1] 0; 1/8 ,..., 1) points of a lines in square which are on a screen

    18 lines 0-9 u or v
    """
    iterations_left = sub_div
    lines = []
    start_point = vector([vectors[0], vectors[0]])
    end_point = vector([vectors[1], vectors[2]])
    v0, v1, v2 = vector(vectors[0]), vector(vectors[1]), vector(vectors[2])
    start_point = [v0, v0]
    end_point = [v1, v2]
    delta_v = v1 - v0, v2 - v0 # dw1, dw2
    sub_delta_v = [sub_div_ * delta_v[0], sub_div_ * delta_v[1]]

    while iterations_left >= 0:
        lines.append(line_precomputation(start_point[0], end_point[0]))
        lines.append(line_precomputation(start_point[1], end_point[1]))

        start_point[0] += sub_delta_v[1]
        start_point[1] += sub_delta_v[0]
        end_point[0] += sub_delta_v[1]
        end_point[1] += sub_delta_v[0]

        iterations_left -= 1

    lines.append(line_precomputation(start_point[0], end_point[0]))
    lines.append(line_precomputation(start_point[1], end_point[1]))
    return lines


def main() -> None:
    """
    img = Image.new('RGB', screen, color='black')
    vect1 = [-1, -1, 8]
    vect2 = [-1, 1, 8]
    vect3 = [1, -1, 8]
    special_points = compute_end_points([vect1, vect2, vect3])
    for point in special_points[0]:
        img.putpixel(project_vertex(point), (0, 0, 255))

    for point in special_points[1]:
        img.putpixel(project_vertex(point), (0, 255, 0))

    img.save('test.png')"""

