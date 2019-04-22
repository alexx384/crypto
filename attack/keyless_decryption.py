import sys

sys.path.append('..')
import lib
import functools
from decimal import Decimal


def _generate_broadcast_params(msg: bytes = b"Hello!!!", num_msgs: int = 3):
    print("Original message: ", msg)
    e = []
    c = []
    n = []
    i = 0
    while i < num_msgs:
        rsa_crypt = lib.RSACrypto(e=7)
        i_msg = int.from_bytes(msg, byteorder='big')
        encrypted_msg = rsa_crypt.encrypt(i_msg)
        c.append(encrypted_msg)
        e.append(rsa_crypt.e)
        n.append(rsa_crypt.n)
        i = i + 1

    return e, n, c


def _chinese_remainder(n, a):
    summary = 0
    production = functools.reduce(lambda mul_1, mul_2: mul_1 * mul_2, n)

    for n_i, a_i in zip(n, a):
        p = production // n_i
        summary += a_i * lib.RSACrypto._evklid(p, n_i)[0] * p

    return summary % production


def keyless_attack(e, n, c):
    x = _chinese_remainder(n, c)
    power = Decimal(1) / Decimal(e[0])
    i_msg = int(Decimal(x)**power)
    msg = i_msg.to_bytes(8, byteorder="big")
    print("Decrypted message: ", msg)


def main():
    e, n, c = _generate_broadcast_params()
    keyless_attack(e, n, c)


main()
