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
    dy_dx = dy >= dx

    if dy_dx:
        # typical bresenham algorithm

        error = 2 * dx - dy
        de0 = 2 * dx - 2 * dy
        de1 = 2 * dx
        dx0 = 1
        dx1 = 0
        draw_run(x0, x, y) # first run

        """
        while y1 < y:
            if error >= 0:
                error += de0
                x += dx0
            else:
                error += de1
                x += dx1

            draw_run(x, x, y)
            y -= 1
        draw_run(x, x1, y1) # last run

        return
        """

    else:
        if dy < 2:
            if dy == 0:
                draw_run(x0, x1, y0) # horizontal line
            
            R0 = (dx - 1) // 2
            draw_run(x0, x0 + R0, y0) # first run
            draw_run(x0 + R0 + 1, x1, y1) # last run

            # all runs are drawn
            # dy >= 0
            return
        
        R = dx // dy
        dx_ = dx % dy

        r = R % 2
        R0 = (R - r - 2 * r * (dx_ == 0)) // 2 + 1

        x = x0 + R0 - 1
        x_prev = x
        
        de0 = -2 * dy if dx_ == 0 else -2 * dx_
        de1 = 0 if dx_ == 0 else -2 * dx_ + 2 * dy
        dx0 = R - (dx_ == 0)
        dx1 = R + 1 - (dx_ == 0)
        
        error = -dx_ + r * dy + 2 * (1 - r) * (dx_ != 0) * dy + de0

    draw_run(x0, x, y0) # first run

    y -= 1

    while y1 < y:
        if error >= 0:
            error += de0
            x += dx0
        else:
            error += de1
            x += dx1

        if dy_dx:
            draw_run(x, x, y)
        else:
            draw_run(x_prev + 1, x, y)
        x_prev = x

        y -= 1

    if dy_dx:
        draw_run(x, x1, y1)
    else:
        draw_run(x_prev + 1, x1, y1) # last run

    return


if __name__ == "__main__":
    img = Image.new("RGB", (250, 250), (0, 0, 0))
    #draw_line(5, 1, 1, 20)
    draw_line(1, 5, 20, 1)
    
    img.save("test.png")
