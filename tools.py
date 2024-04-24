import math
import random


def calcular_distancia(punto1, punto2):
    dx = (punto1[1] - punto2[1]) ** 2
    dy = (punto1[2] - punto2[2]) ** 2
    return math.sqrt(dx + dy)


def is_close(d1, d2):
    close = math.isclose(d1, d2, rel_tol=0.1)
    return close


def compute_direction(d1, d2, d3, d4):
    # is_up = math.isclose(d1, d2, rel_tol=0.01)
    # is_down = math.isclose(d3, d4, rel_tol=0.01)
    # if d1 < d2 and d3 < d4:
    #     volado = 1
    # else:
    #     volado = 0
    # print(f"is_up:{is_up}, is_down:{is_down}")
    volado = random.randint(0, 1)
    if volado:
        print("up")
        return "up"
    print("down")
    return "down"


def it_moves(d1, d2, d3, d4):
    center_left = math.isclose(d1, d2, rel_tol=0.1)
    center_right = math.isclose(d3, d4, rel_tol=0.1)
    # print(f"center_left:{center_left}, center_right:{center_right}")
    if not (center_left) or not (center_right):
        print("Hay movimiento de ojos")
        dir = compute_direction(d1, d2, d3, d4)
        return True, dir
    return False, ""


def get_data(x, lst):
    res = [(i, row) for i, row in enumerate(lst) if x in row]
    return res[0][1]


def can_process(data):
    center = get_data(168, data)
    right = get_data(127, data)
    left = get_data(264, data)
    d_center_right = calcular_distancia(center, right)
    d_center_left = calcular_distancia(center, left)
    res = is_close(d_center_right, d_center_left)
    if res:
        print("Puede procesar!")
    return res


def move_slider(data):
    iris_center_right = get_data(468, data)
    iris_center_left = get_data(473, data)
    up_right = get_data(297, data)
    up_left = get_data(67, data)
    down_right = get_data(205, data)
    down_left = get_data(425, data)
    d_iris_up_left = calcular_distancia(iris_center_left, up_left)
    d_iris_up_right = calcular_distancia(iris_center_right, up_right)
    d_iris_down_left = calcular_distancia(iris_center_left, down_left)
    d_iris_down_right = calcular_distancia(iris_center_right, down_right)
    res, dir = it_moves(
        d_iris_up_left,
        d_iris_down_left,
        d_iris_up_right,
        d_iris_down_right,
    )

    return res, dir
