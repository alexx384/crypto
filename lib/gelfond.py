import math


# Based on https://en.wikipedia.org/wiki/Baby-step_giant-step
def gelfond(a_generator: int, b_element: int, n_order: int):

    m = math.trunc(math.sqrt(n_order)) + 1
    c = pow(a_generator, m, n_order)

    base1 = []
    base2 = []
    i = 0
    u = 0
    v = 0

    while i < m:
        base1.append(pow(c, i, n_order))
        base2.append((b_element * (a_generator ** i)) % n_order)

        for k in range(i + 1):
            if base1[i] == base2[k]:
                u = i
                v = k
                break

            if base2[i] == base1[k]:
                u = k
                v = i
                break

        i = i + 1

    x = (m * u - v) % (n_order)

    return x
