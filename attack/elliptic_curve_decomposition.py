import math
import lib
import sympy

import sys

sys.path.append('..')
from lib import elliptic


def decomposition(n: int):
    """ Decomposition of number on elliptic curve """
    primes = lib.get_primes(up_to=300000)

    # 1024 bit field
    p_field = 95777621695595220893827582455568322949360165363785871654710150652523523455505729368460822100696774504239394103463514086278256724517146426653923971783093980678357933040312165712079620906481360086474298714890888636873090643116431715358613362273906310756306548690826034551206713409853566409729418426944350021177
    while True:
        A, B, Q = elliptic.generate_curve(p_field)
        i = 0

        # 3. Enumerating all prime numbers
        while i < len(primes):
            p = primes[i]
            i = i + 1
            if p >= n:
                break

            # Round down
            alpfa = math.floor(0.5 * math.log10(n) / math.log10(p))
            j = 0

            # 5. Do following actions
            while j <= alpfa:
                _, l_denominator = elliptic.mul_point_on_number(Q, p, A, p_field)
                d = int(sympy.gcd(n, l_denominator))
                if 1 < d < n:
                    return d
                j = j + 1


def main():
    rsa_crypt = lib.RSACrypto(20, 7)
    print("params:")

    rsa_crypt.n = 790129
    rsa_crypt.e = 7
    rsa_crypt.d = 337579

    print("n = ", str(rsa_crypt.n))
    print("e = ", str(rsa_crypt.e))
    print("d = ", str(rsa_crypt.d))

    p = 0
    q = 0
    iter = 1
    while (p * q) != rsa_crypt.n:
        print(iter)
        p = decomposition(rsa_crypt.n)
        q = rsa_crypt.n // rsa_crypt.p
        iter += 1

    m = (p - 1) * (q - 1)
    d2 = int(sympy.invert(rsa_crypt.e, m))

    print("Found p: " + str(p))
    print("Found q: " + str(q))
    print("Found d: " + str(d2))


main()
# print(gen_rsa_params(1024))
