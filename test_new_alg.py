from PIL import Image

CELL = 10

def draw_cell(x, y, color=(255, 255, 255)):
    """Draw a 10x10 block at cell (x, y), where cell (0, 0) is the bottom-left."""
    # vibecoded
    left = x * CELL
    bottom = y * CELL
    for dx in range(CELL):
        for dy in range(CELL):
            px = left + dx
            py = img.height - 1 - (bottom + dy)
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), color)

def draw_run(x0, x1, y):
    """draws run from xmin to xmax including"""
    x = min(x0, x1)
    draw_cell(x, y)
    while x < max(x0, x1):
        x += 1
        draw_cell(x, y)


def draw_line(x0, y0, x1, y1):
    """
    This algorithm draws line from (..., ymax) to (..., ymin)
    That arrange of points was choosen specifically to match redstone logic
    It simulates Bresenham algorithm or uses it and all lines are exactly as from
    BR algorithm. It uses runs to save some time (in this instacne usual BR algorithm
    is faster but for other problems where runs are hardware part and we need to itreate
    over some coordinate this is significatelly faster)"""
    if y1 > y0:
        x1, x0 = x0, x1
        y1, y0 = y0, y1
    dx, dy = x1 - x0, y0 - y1
    x, y = x0, y0
    dx, dx_sign = abs(dx), 1 if dx >= 0 else -1

    if dy >= dx:
        error = 2 * dx - dy
        de0 = 2 * dx - 2 * dy
        de1 = 2 * dx
        dx0 = dx_sign
        dx1 = 0
    else:
        if dy == 0:
            draw_run(x0, x1, y0) # horizontal line
            return
        elif dy == 1:
            
            R0 = (dx - 1) // 2
            draw_run(x0, x0 + R0 * dx_sign, y0) # first run
            draw_run(x0 + (R0 + 1) * dx_sign, x1, y1) # last run

            # all runs are drawn
            # dy >= 0
            return

        # R - amount of points in run in some runs its R + 1
        # R0 - amount of pixels in first run it varies from all other runs
        # and is close to R1 - amount of points in last run
        
        R = dx // dy
        dx_ = dx % dy
        r = R % 2
        R0 = (R + r) // 2 + (1 - r) * (dx_ > 0)

        x = x0 + (R0 - 1) * dx_sign
        x_prev = x
        
        de0 = -2 * dy if dx_ == 0 else -2 * dx_
        de1 = 0 if dx_ == 0 else -2 * dx_ + 2 * dy
        dx0 = R * dx_sign
        dx1 = (R + 1 - (dx_ == 0)) * dx_sign
        error = de0 - dx_ + dy * (r + 2 * (r == 0) * (dx_ != 0))

    # first run
    if dy >= dx:
        draw_run(x0, x0, y0)
    else:
        draw_run(x0, x, y0)
    y -= 1

    while y1 < y:
        if error >= 0:
            error += de0
            x += dx0
        else:
            error += de1
            x += dx1
        if dy >= dx:
            draw_run(x, x, y)
        else:
            draw_run(x_prev + dx_sign, x, y)
        x_prev = x
        y -= 1

    # last run
    if dy >= dx:
        draw_run(x1, x1, y1)
    else:
        draw_run(x_prev + dx_sign, x1, y1)
    return


if __name__ == "__main__":
    img = Image.new("RGB", (250, 250), (0, 0, 0))
    img.save("test.png")
