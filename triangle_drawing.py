from project import compute_special_points
import pygame
import json

screen = pygame.display.set_mode((720, 500))
pixel = pygame.Surface((10, 10))
pixel.fill((255, 255, 255))


def sort_(arr, if_max):
    if if_max:
        max_ = max(arr)
        for i in arr:
            if max_ == arr[i]:
                return i
    else:
        min_ = min(arr)
        for i in arr:
            if min_ == arr[i]:
                return i


def draw_vertical_line(u, v0, v1):
    u = int(u)
    v0 = int(v0)
    v1 = int(v1)
    for v in range(min(v0, v1), max(v0, v1) + 1):
        screen.blit(pixel, (u, v))


def draw_polygon(vertex0: list[int, int, int],
                 vertex1: list[int, int, int],
                 vertex2: list[int, int, int],
                 sub_div: int = 8) -> None:
    delta_x = []
    delta_y = []
    x_sign = []
    y_sign = []
    swapped = []
    swapping = []
    error = []
    x = []
    y = []
    skip = []
    running = 9
    current_runnibg = 0
    triangle_special_points = compute_special_points(vertex0, vertex1, vertex2)
    if triangle_special_points is not None:
        row = []
        with open("Textures.json", "r") as f:
            data = json.load(f)
        texture = data["data"]
        start_points, end_points = triangle_special_points[1]
        for i in range(sub_div + 1):
            swapping.append(0)

            delta_x.append(abs(end_points[i][0] - start_points[i][0]))
            x_sign.append((1 if end_points[i][0] - start_points[i][0] >= 0 else -1))
            if delta_y[i] >= delta_x[i]:
                swapping[i] = delta_y[i]
                delta_y.append(abs(end_points[i][1] - start_points[i][1]))
                y_sign.append((1 if end_points[i][1] - start_points[i][1] >= 0 else -1))
                delta_y[i] = delta_x[i]
                delta_x[i] = swapping[i]
                swapped = True
            else:
                swapped = False

            error.append(delta_x[i])
            x.append((start_points[i][0] if not swapped else start_points[i][1]))
            y.append((start_points[i][1] if not swapped else start_points[i][0]))
            skip.append(False)

        while running:
            for i in range(sub_div + 1):
                if not skip[i]:
                    error[i] += 2 * delta_y[i]
                    if error[i] >= 0:
                        error[i] -= 2 * delta_x[i]
                        if not swapped:
                            y[i] += y_sign
                            skip[i] = True
                        else:
                            x[i] += x_sign
                    if not swapped:
                        x[i] += x_sign
                    else:
                        y[i] += y_sign
                    row.append([x[i], y[i]])
                if all(skip):
                    for k in skip:
                        skip[k] = False
            for i in range(sub_div):
                draw_vertical_line(row[i][0], row[i][1], row[i + 1][1])
    else:
        return
