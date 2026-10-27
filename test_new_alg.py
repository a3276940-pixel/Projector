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


def draw_line(x0, y0, x1, y1):
    # dx >= 0
    def draw_run(x0, x1, y):
        x = min(x0, x1)
        draw_cell(x0, y)
        while x < max(x0, x1):
            x += 1
            draw_cell(x, y)

    if y1 > y0:
        x1, x0 = x0, x1
        y1, y0 = y0, y1

    dx, dy = x1 - x0, y0 - y1
    x, y = x0, y0

    if dx < 0:
        raise ValueError("x1 must be greater than or equal to x0")

    if dy >= dx:
        # typical bresenham algorithm

        error = 2 * dx - dy
        draw_cell(x, y)
        print(error)

        while y1 < y:
            if error >= 0:
                error += 2 * dx - 2 * dy
                x += 1
            else:
                error += 2 * dx
            y -= 1
            draw_cell(x, y)
            print(error)

        return

    try:    
        R = dx // dy
        dx_ = dx % dy
    except ZeroDivisionError:
        R = dx

    r = R % 2
    R0 = (R - r - 2 * r * (dx_ == 0)) // 2 + 1
    R1 = R // 2 - R % 2

    x = x0 + R0 - 1
    x_prev = x
    draw_run(x0, x, y0) # first run

    draw_run(x1 - R1, x1, y1) # last run

    if dy < 2:
        # all runs are drawn
        # dy > 0
        return

    error = -dx + R0 * 2 * dy
    print(error, R0)
    y -= 1

    if dx_ == 0:
        de0 = -2 * dx_ - 2 * dy
        de1 = -2 * dx_
        dx0 = R - 1
        dx1 = R
    else:
        de0 = -2 * dx_
        de1 = -2 * dx_ + 2 * dy
        dx0 = R
        dx1 = R + 1


    while y1 < y:
        print(error)
        if error + de0 < 0:
            error += de1
            x += dx1
        else:
            error += de0
            x += dx0

        
        draw_run(x_prev + 1, x, y)
        x_prev = x

        y -= 1

    return


if __name__ == "__main__":
    img = Image.new("RGB", (250, 250), (0, 0, 0))
    # draw_line(5, 1, 1, 20)
    draw_line(1, 5, 20, 1)
    
    img.save("test.png")
