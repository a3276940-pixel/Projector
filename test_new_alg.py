from PIL import Image
from triangle_drawing import Line

CELL = 10
line_run_cache = []

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


def draw_run_(x_, x_prev, y, x_s):
    if x_ != x_prev:
        x_ += x_s
    x = min(x_, x_prev)
    x_max = max(x_, x_prev)
    line_run_cache.append((x, x_max, y))
    draw_cell(x, y)
    while x < x_max:
        x += 1
        draw_cell(x, y)

    #draw_run(x_, x_prev, y)


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
    x_prev = x

    if dy > dx:
        error = 2 * dx - dy
        de0 = 2 * dx - 2 * dy
        de1 = 2 * dx
        dx0 = dx_sign
        dx1 = 0
        #x_prev = x0 - dx_sign
    else:
        if dy == 0:
            R0 = dx + 1
            x = x0 + (R0 - 1) * dx_sign
            x_prev = x0 - dx_sign
            draw_run_(x_prev, x, y, dx_sign) # horizontal line
            return
        elif dy == 1:
            R0 = (dx - 1) // 2 + 1
            x = x0 + (R0 - 1) * dx_sign
            x_prev = x0 - dx_sign
            draw_run_(x_prev, x, y0, dx_sign) # first run
            x_prev = x
            x = x1
            draw_run_(x_prev, x, y1, dx_sign) # last run
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
        
        de0 = -2 * dy if dx_ == 0 else -2 * dx_
        de1 = 0 if dx_ == 0 else -2 * dx_ + 2 * dy
        dx0 = R * dx_sign
        dx1 = (R + 1 - (dx_ == 0)) * dx_sign
        error = de0 - dx_ + dy * (r + 2 * (r == 0) * (dx_ != 0))

    # first run
    x_prev -= dx_sign
    draw_run_(x_prev, x, y, dx_sign)
    r0 = x - x_prev
    x_prev = x
    y -= 1

    while y1 < y:
        if error >= 0:
            error += de0
            x += dx0
        else:
            error += de1
            x += dx1
        draw_run_(x_prev, x, y, dx_sign)
        x_prev = x
        y -= 1

    # last run    
    draw_run_(x_prev, x1, y, dx_sign)
    return

def draw_line_BR(x0, y0, x1, y1):
    if y1 > y0:
        x1, x0 = x0, x1
        y1, y0 = y0, y1

    dx, dy = x1 - x0, y0 - y1
    x, y = x0, y0

    dx_sign = 1 if dx >= 0 else -1
    dy_sign = -1
    dx, dy = abs(dx), abs(dy)

    swapped = dy >= dx
    if swapped:
        dx, dy = dy, dx
        x, y = y, x
        dx_sign, dy_sign = dy_sign, dx_sign

    # print(f"Drawing line from ({x0}, {y0}) to ({x1}, {y1}), swapped: {swapped}, dx: {dx}, dy: {dy}, dx_sign: {dx_sign}, dy_sign: {dy_sign}")

    error = 2 * dy - dx

    result = []
    for _ in range(dx + 1):
        result.append((x, y) if not swapped else (y, x))
        if error >= 0:
            y += dy_sign
            error -= 2 * dx
        x += dx_sign
        error += 2 * dy
    return result

def check_line(x0, y0, x1, y1):
    check = Line((x0, y0), (x1, y1))
    for run in line_run_cache:
        run1 = check.advance()
        if run != run1[0]:
            return False
    
    return True

def stress_test():
    incorrect_count = 0
    all_counts = 0
    for x0 in range(10):
        for y0 in range(10):
            for x1 in range(10):
                for y1 in range(10):
                    #if abs(x1 - x0) < abs(y1 - y0):
                    #    continue
                    line_run_cache.clear()
                    draw_line(x0, y0, x1, y1)
                    if not check_line(x0, y0, x1, y1):
                        print(f"Line from ({x0}, {y0}) to ({x1}, {y1}) failed.")
                        incorrect_count += 1
                    all_counts += 1
            print(f"Completed stress test for starting point ({x0}, {y0}), tested {all_counts} lines so far, incorrect: {incorrect_count}, progress: {(all_counts / (10 * 10 * 10 * 10)) * 100:.2f}%")

    print(f"Total lines tested: {all_counts}")

    if incorrect_count == 0:
        print("All lines passed the stress test.")
    else:
        print(f"Failed lines: {incorrect_count} out of {all_counts} ({(incorrect_count / all_counts) * 100:.2f}%)")


if __name__ == "__main__":
    img = Image.new("RGB", (250, 250), (0, 0, 0))
    stress_test()
    #draw_line(0, 0, 6, 4)
    #print(check_line(4, 9, 4, 9))
    img.save("test.png")
