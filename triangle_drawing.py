import json
from pathlib import Path
from project import compute_end_points

_TEXTURES_PATH = Path("Textures.json")
_texture_cache = None


def _load_all_textures():
    global _texture_cache
    if _texture_cache is None:
        raw = json.loads(_TEXTURES_PATH.read_text())
        _texture_cache = {t["index"]: t for t in raw}
    return _texture_cache


def get_texture(texture_index):
    return _load_all_textures()[texture_index]["texture"]


class line:
    def __init__(self, start_point, end_point):

        def sort_(first, second):
            return sorted([first, second]), first >= second

        def abs_(number):
            return abs(number), (1 if number >= 0 else -1)

        self.delta_x, self.delta_y, self.swapped_xy = sort_(end_point[0] - start_point[0], end_point[1] - start_point[1])
        self.delta_x, self.x_sign = abs_(self.delta_x)
        self.delta_y, self.y_sign = abs_(self.delta_y)

        self.error = -self.delta_y
        self.x, self.y = start_point


class Polygon:
    def __init__(self, vertexes, texture_index):
        self.vertexes = vertexes
        self.texture = get_texture(texture_index)

        self.lines = compute_end_points(vertexes)
        
        self.delta_x
        self.delta_y
