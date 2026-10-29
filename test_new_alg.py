from PIL import Image

CELL = 10
line_points_cache = []

def draw_cell(x, y, color=(255, 255, 255)):
    """Draw a 10x10 block at cell (x, y), where cell (0, 0) is the bottom-left."""
    # vibecoded
    line_points_cache.append((x, y))
    if False:
        return
    
    left = x * CELL
    bottom = y * CELL
    for dx in range(CELL):
        for dy in range(CELL):
            px = left + dx
            py = img.height - 1 - (bottom + dy)
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), color)

def draw_line(x0, y0, x1, y1):
    def draw_run(x0, x1, y):
        x = min(x0, x1)
        draw_cell(x, y)
        while x < max(x0, x1):
            x += 1
            draw_cell(x, y)

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
        
        # error = -dx + R0 * 2 * dy + de0
        error = de0 - dx_ + dy * (r + 2 * (r == 0) * (dx_ != 0))

    if dy >= dx:
        draw_run(x0, x0, y0) # first run
    else:
        draw_run(x0, x, y0) # first run
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

    if dy >= dx:
        draw_run(x1, x1, y1)
    else:
        draw_run(x_prev + dx_sign, x1, y1) # last run

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
    points = draw_line_BR(x0, y0, x1, y1)
    for point in points:
        if point not in line_points_cache:
            #print(f"Point {point} is missing from the cache.")
            return False

    for point in line_points_cache:
        if point not in points:
            #print(f"Point {point} is extra in the cache.")
            return False
    return True

def stress_test():
    incorrect_count = 0
    all_counts = 0
    for x0 in range(10):
        for y0 in range(10):
            for x1 in range(10):
                for y1 in range(10):
                    line_points_cache.clear()
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
    img.save("test.png")
