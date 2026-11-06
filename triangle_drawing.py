import json
from pathlib import Path
# from project import compute_end_points


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


class Line:
    def __init__(self, start_point, end_point):
        self.x0, self.y0, self.x1, self.y1 = start_point + end_point
        if self.y1 > self.y0:
            self.x0, self.x1 = self.x1, self.x0
            self.y0, self.y1 = self.y1, self.y0
        
        self.dx = self.x1 - self.x0
        self.dy = self.y0 - self.y1

        self.dx, self.dx_sign = abs(self.dx), 1 if self.dx >= 0 else -1
        if self.dy > self.dx:
            self.error = 2 * self.dx - self.dy
            self.derror0 = 2 * self.dx - 2 * self.dy
            self.derror1 = 2 * self.dx
            self.dx0 = self.dx_sign
            self.dx1 = 0
            self.r0 = 1

        elif self.dy == 0:
            self.r0 = self.dx + 1

        elif self.dy == 1:
            self.r0 = (self.dx - 1) // 2 + 1

        else:
            self.r = self.dx // self.dy
            self.dx_ = self.dx % self.dy
            r = self.r % 2
            self.r0 = (self.r + r) // 2 + (1 - r) * (self.dx_ != 0)

            self.derror0 = -2 * self.dy if self.dx_ == 0 else -2 * self.dx_
            self.derror1 = 0 if self.dx_ == 0 else -2 * self.dx_ + 2 * self.dy
            self.dx0 = self.r * self.dx_sign
            self.dx1 = (self.r + 1 - (self.dx_ == 0)) * self.dx_sign

            self.error = self.derror0 - self.dx_ + self.dy * (r + 2 * (r == 0) * (self.dx_ != 0))

        self.x = self.x0 - self.dx_sign
        self.y = self.y0 + 1

    def configure_run(self):
        x = self.x_prev
        if self.x != self.x_prev:
            x += self.dx_sign
        return min(x, self.x), max(x, self.x), self.y

    def advance(self, current_y=0):
        #if current_y > self.y0:
        #    return (), True
        self.y -= 1
        self.x_prev = self.x
        if self.y == self.y0:
            self.x = self.x0 + (self.r0 - 1) * self.dx_sign
        elif self.y == self.y1:
            self.x = self.x1
        else:
            if self.error >= 0:
                self.error += self.derror0
                self.x += self.dx0
            else:
                self.error += self.derror1
                self.x += self.dx1

        return self.configure_run(), self.y <= self.y1

    def __repr__(self):
        return f"dx: {self.dx}, dy: {self.dy}, x: {self.x}, y: {self.y}, x_prev: {self.x_prev}, error: {self.error}"
    

class Polygon:
    def __init__(self, vertexes, texture_index):
        self.vertexes = vertexes
        self.texture = get_texture(texture_index)

        # lines = compute_end_points(vertexes)
        # self.hor_lines = [line(hor) for hor in lines[0]]
        # self.ver_lines = [line(ver) for ver in lines[1]]

if __name__ == "__main__":
    check = Line((0, 0), (6, 4))
    while True:
        a = check.advance()
        print(a[0])
        if a[1]:
            break
