import random
import gmpy2
from . import elliptic


def pollard(p: int, p_point: (int, int), q_point: (int, int), q: int,
            a_factor: int, times: int):
    for i in range(times):
        print(i, end='\r', flush=True)
        result = _pollard(p, p_point, q_point, q, a_factor)
        if result is not None:
            return result

    print("Cant do it, choose differnt L")


def _pollard(p, p_point, q_point, q, a_factor):

    l_const = 4
    a = []
    b = []
    r_point_list = []
    while len(r_point_list) < l_const:
        aj = random.randint(0, q - 1)
        bj = random.randint(0, q - 1)
        p_point_j, _ = elliptic.mul_point_on_number(p_point, aj, a_factor, p)
        q_point_j, _ = elliptic.mul_point_on_number(q_point, bj, a_factor, p)

        if p_point_j is None or q_point_j is None:
            continue

        r_point_j, _ = elliptic.sum_points(q_point_j, p_point_j, a_factor, p)
        a.append(aj)
        b.append(bj)
        r_point_list.append(r_point_j)

    alpha1 = random.randint(0, q - 1)
    beta1 = random.randint(0, q - 1)

    alpha_p, _ = elliptic.mul_point_on_number(p_point, alpha1, a_factor, p)
    beta_p, _ = elliptic.mul_point_on_number(p_point, beta1, a_factor, p)
    t_point_1, _ = elliptic.sum_points(alpha_p, beta_p, a_factor, p)
    t_point_2 = t_point_1

    alpha2 = alpha1
    beta2 = beta1

    # First iteration of the next cycle
    j = t_point_1[0] % l_const
    t_point_1, lam = elliptic.sum_points(t_point_1, r_point_list[j], a_factor, p)
    alpha1 = (alpha1 + a[j]) % q
    beta1 = (beta1 + b[j]) % q

    for _ in range(2):
        j = t_point_2[0] % l_const
        t_point_2, _ = elliptic.sum_points(t_point_2, r_point_list[j], a_factor, p)
        alpha2 = (alpha2 + a[j]) % q
        beta2 = (beta2 + b[j]) % q

    # Main cycle
    while t_point_1[0] != t_point_2[0] or t_point_1[1] != t_point_2[1]:
        j = t_point_1[0] % l_const
        t_point_1, lam = elliptic.sum_points(t_point_1, r_point_list[j], a_factor, p)
        alpha1 = (alpha1 + a[j]) % q
        beta1 = (beta1 + b[j]) % q

        for _ in range(2):
            j = t_point_2[0] % l_const
            t_point_2, _ = elliptic.sum_points(t_point_2, r_point_list[j], a_factor, p)
            alpha2 = (alpha2 + a[j]) % q
            beta2 = (beta2 + b[j]) % q

    if alpha1 == alpha2 or beta1 == beta2:
        return None
    else:
        d = ((alpha1 - alpha2) * gmpy2.invert((beta2 - beta1), q)) % q
        return d
