import random
import sympy


def mul_point_on_number(p_point: (int, int), k: int, a_factor: int,
                        p_field: int):
    l_factor = 0
    if k == 0:
        return (None, None)
    k_bin = [int(i) for i in bin(k)[2:]]
    q_point = None
    for i in k_bin:
        q_point, l_factor = sum_points(q_point, q_point, a_factor, p_field)
        if i != 0:
            q_point, l_factor = sum_points(q_point, p_point, a_factor, p_field)
    return q_point, l_factor


def sum_points(point1, point2, a_factor, p_field):
    """
    Sum point algorithm

    :param point1: first point on elliptic curve
    :param point2: second point on elliptic curve
    :param a_factor: factor in equation: y^2 = x^3 + Ax + B
    :param p_field: field where elliptic curve is defined
    :return: point3, denominator of l factor
    """
    if point1 is None:
        return point2, 0
    if point2 is None:
        return point1, 0
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]

    if point1[0] == point2[0]:
        if point1[1] == point2[1]:
            l1 = (3 * x1 ** 2 + a_factor)
            s = int(sympy.mod_inverse(2 * y1, p_field))
            l_factor = (l1 * s) % p_field
            x3 = (l_factor ** 2 - 2 * x1) % p_field
            y3 = (l_factor * (x1 - x3) - y1) % p_field
            point3 = [x3, y3]
            return point3, 2 * y1
        else:
            # We assume that point1[1] % p = point2[1]
            # So: P + (-P) = 0
            return [0, 0], 0
    else:
        s = int(sympy.mod_inverse(x2 - x1, p_field))
        l_factor = ((y2 - y1) * s) % p_field
        x3 = (l_factor ** 2 - x1 - x2) % p_field
        y3 = (l_factor * (x1 - x3) - y1) % p_field
        point3 = [x3, y3]
        return point3, (x2 - x1) % p_field


def is_curve_valid(a_factor, b_factor, p_field):
    if (4 * a_factor ** 3 + 27 * b_factor ** 2) % p_field != 0:
        return True
    else:
        return False


def generate_curve(p_field: int):
    while True:
        random_point = [random.randint(1, p_field - 1),
                        random.randint(1, p_field - 1)]
        a_factor = random.randint(1, p_field - 1)
        b_factor = (random_point[1] ** 2 - random_point[0] ** 3 -
                    a_factor * random_point[0]) % p_field
        if is_curve_valid(a_factor, b_factor, p_field):
            return a_factor, b_factor, random_point
