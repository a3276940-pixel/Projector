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

        def configure_deltas(delta):
            

            return

        self.delta_x, self.delta_y, self.swapped_xy = sort_(end_point[0] - start_point[0], end_point[1] - start_point[1])
        self.delta_x, self.x_increment,
        self.delta_y, self.y_increment = configure_deltas(self.delta_x, self.delta_y)

        self.error = -self.delta_y
        self.x, self.y = start_point

        self.amount_of_iterations = self.delta_x

    def advance(self):
        self.error += 2 * self.delta_x
        (self.y if self.swapped_xy else self.x) += (self.y_increment if self.swapped_xy else self.x_increment)

        if self.error >= 0:
            self.error -= 2 * self.delta_y
            (self.y if not self.swapped_xy else self.x) += (self.y_increment if not self.swapped_xy else self.x_increment)

        self.amount_of_iterations -= 1

        return self.amount_of_iterations == 0
    

class Polygon:
    def __init__(self, vertexes, texture_index):
        self.vertexes = vertexes
        self.texture = get_texture(texture_index)

        lines = compute_end_points(vertexes)
        self.hor_lines = [line(hor) for hor in lines[0]]
        self.ver_lines = [line(ver) for ver in lines[1]]
