import sympy
import random
import lib


class RSACrypto(object):
    # Weird: Program works when e is 65537 but not when e is 3
    def __init__(self, dimension: int = 256, e: int = None):
        is_params_generated = False

        if not is_params_generated:
            self._gen_params(dimension, e)

    def _gen_params(self, dimension, fixed_e):
        if fixed_e is not None:
            if (fixed_e % 2) == 0:
                print("Error: e is even number")
                fixed_e = None
            if fixed_e < 3:
                fixed_e = None

        difference = 2 ** (dimension // 2 - 2)

        while True:
            p = q = 0

            # Based on Pollard's p − 1 algorithm generate strong primes
            # https://en.wikipedia.org/wiki/Pollard%27s_p_%E2%88%92_1_algorithm
            # (p - 1 = prime * 2) => (p = prime * 2 + 1)
            while sympy.isprime(p) is False:
                p_1 = sympy.nextprime(random.getrandbits(dimension // 2 + 1)) * 2
                p = p_1 + 1
            while sympy.isprime(q) is False:
                q_1 = sympy.nextprime(random.getrandbits(dimension // 2)) * 2
                q = q_1 + 1

            # Anti Fermat's factorization method
            # https://en.wikipedia.org/wiki/Fermat%27s_factorization_method
            if abs(p - q) > difference:
                n = p * q
                if lib.bitcount(n) == dimension:
                    phi = (p - 1) * (q - 1)
                    while True:
                        if fixed_e is None:
                            e = random.randint(3, phi - 1)
                        else:
                            e = fixed_e

                        if sympy.gcd(e, phi) == 1:
                            d = sympy.invert(e, phi)

                            # Anti Wiener's attack
                            # https://en.wikipedia.org/wiki/Wiener%27s_attack
                            if d > 1 / 3 * sympy.root(n, 4):
                                break
                    break

        self.p = p
        self.q = q
        self.n = n
        self.e = e
        self.d = int(d)

        return e, d, n

    def encrypt_sign(self, value: int) -> int:
        return pow(value, self.d, self.n)

    def decrypt_sign(self, value: int) -> int:
        return pow(value, self.e, self.n)

    def encrypt(self, value: int) -> int:
        return pow(value, self.e, self.n)

    def decrypt(self, value: int) -> int:
        return pow(value, self.d, self.n)
