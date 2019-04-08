import ctypes
import sympy


class ElGamal(object):
    def __init__(self, dimension: int, p: int = None, g: int = None):
        if p is None:
            self.p = sympy.randprime(pow(2, dimension), pow(2, dimension + 1))
        else:
            self.p = p
        generate(p)


# Algorithm from:
# https://cp-algorithms.com/algebra/primitive-root.html


def _powmod(a: int, b: int, p: int) -> int:
    res = 1
    while b:
        if b & 1:
            res = int(res * a % p)
            b -= 1
        else:
            a = int(a * a % p)
            b >>= 1

    return res


def generate(prime: int) -> int:
    fact = []
    phi = prime - 1
    n = phi

    i = 2
    while (i * i) <= n:
        if (n % i) == 0:
            fact.append(i)
            while (n % i) == 0:
                n /= i

        i += 1

    if n > 1:
        fact.append(n)

    res = 2
    while res <= prime:
        ok = True
        for i in range(0, len(fact), 1):
            if not ok:
                break
            ok &= (_powmod(res, int(phi / fact[i]), prime) != 1)

        if ok:
            return res

        res += 1

    return -1


def main():
    libgenerator = ctypes.CDLL('./libgenerator.so')
    print(libgenerator.generator(23))

    print(generate(23))


main()
