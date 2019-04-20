from sympy.ntheory.continued_fraction import continued_fraction_periodic
import os

import sys

sys.path.append('..')
import lib


def isqrt(n):
    '''
    Calculates the integer square root
    for arbitrary large nonnegative integers
    '''
    if n < 0:
        raise ValueError('square root not defined for negative numbers')

    if n == 0:
        return 0
    a, b = divmod(lib.bitcount(n), 2)
    x = 2 ** (a + b)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def is_perfect_square(n):
    '''
    If n is a perfect square it returns sqrt(n),

    otherwise returns -1
    '''
    n = int(n)
    h = n & 0xF  # last hexadecimal "digit"

    if h > 9:
        return -1  # return immediately in 6 cases out of 16.

    # Take advantage of Boolean short-circuit evaluation
    if (h != 2 and h != 3 and h != 5 and h != 6 and h != 7 and h != 8):
        # take square root if you must
        t = isqrt(n)
        if t * t == n:
            return t
        else:
            return -1

    return -1


def viner_attack(e, n):
    tmp_n = n
    counter = 1
    while tmp_n > 255:
        tmp_n >>= 8
    test_msg = int.from_bytes(os.urandom(counter), byteorder='big')

    drob = continued_fraction_periodic(e, n)
    P = []
    Q = []

    convergents = []
    convergents.append((drob[0], 1))
    convergents.append((drob[0] * drob[1] + 1, drob[1]))

    i = 2
    while i < len(drob):
        p = convergents[i - 1][0] * drob[i] + convergents[i - 2][0]
        q = convergents[i - 1][1] * drob[i] + convergents[i - 2][1]
        convergents.append((p, q))
        i = i + 1

    i = 0

    for (k, d) in convergents:
        # check if d is actually the key
        if k != 0 and (e * d - 1) % k == 0:
            phi = (e * d - 1) // k
            s = n - phi + 1
            # check if the equation x^2 - s*x + n = 0
            # has integer roots
            discr = s * s - 4 * n
            if (discr >= 0):
                t = is_perfect_square(discr)
                if t != -1 and (s + t) % 2 == 0:
                    return int(d)


def main():
    e = 0x64e8cf64953d37e8ab29671150555e40b224f0c24fa7b741adfbcb611ea999c83eef6803fc78404f6389fe9c48e7c88163a5e0f3abbf45312e209e70d7e84f869e008a52132726dc319ea3f1be3879632b24180cc41d95430ee6e383c7ffa16a02a22172169ddd89e931b1544d5446b3befd43a85ffff1822b131c726f2a6c9b
    n = 0x46286d0a3dc5c6a51f8ee62b510f407104097d6e316d53c92b2a3973410dbcafe9e543ca2b05dc05cbbed069669c80d0f93ddd6be179f0a09caff75a8db8b9dc7e71ed6d1a32e174add0bb4093256e3c96d705107f39329e8a8fc614846edcfa4e2779f8e025470447c4b5d0cb4cbe578a1e4d56f2bccacba30048f890513d9d1

    d = viner_attack(e, n)
    print(d)

    msg = int.from_bytes(b"Hello!!!", byteorder='big')

    crypted = pow(msg, e, n)
    decr = pow(msg, d, n)
    if decr == msg:
        print('Found d == ' + str(d))


main()

