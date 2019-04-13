import sympy
import random


class ElGamal(object):
    def __init__(self, dimension: int = 256, p: int = None, g: int = None):
        if p is None:
            self.p = sympy.randprime(pow(2, dimension), pow(2, dimension + 1))
        else:
            self.p = p

        if g is None:
            self.g = ElGamal._generate(self.p)
        else:
            self.g = g

        if self.g >= self.p:
            raise Exception("")

        self.x = random.randint(2, (self.p - 1))

    def _func_encrypt(self, msg: int, shared_key: int):
        return pow(msg - shared_key, 1, self.p)

    def _reversed_func_encrypt(self, c: int, shared_key: int):
        return pow(c + shared_key, 1, self.p)

    def get_shared_key(self):
        return pow(self.g, self.x, self.p)

    # msg must be lower than self.p
    def encrypt_msg(self, shared_key: int, msg: int):
        if msg >= self.p:
            return None

        common_shared_key = pow(shared_key, self.x, self.p)
        return self._func_encrypt(msg=msg, shared_key=common_shared_key)

    def decrypt_msg(self, shared_key: int, c: int):
        common_shared_key = pow(shared_key, self.x, self.p)
        return self._reversed_func_encrypt(c=c, shared_key=common_shared_key)

# Algorithm from:
# https://cp-algorithms.com/algebra/primitive-root.html
    @staticmethod
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

    @staticmethod
    def _generate(prime: int) -> int:
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
                ok &= (ElGamal._powmod(res, int(phi / fact[i]), prime) != 1)

            if ok:
                return res

            res += 1

        return -1


# def main():
#     alice = ElGamal(768)
#     alice_encr = alice.get_shared_key()
#
#     bob = ElGamal(768, alice.p, alice.g)
#     bob_encr = bob.get_shared_key()
#
#     print(alice.p)
#     print(alice.g)
#
#     # Does not work
#     msg = int.from_bytes(b"Hello World", byteorder='big')
#     alice_ciph = alice.encrypt_msg(bob_encr, msg)
#     print(alice_ciph)
#     alice_msg = bob.decrypt_msg(alice_encr, alice_ciph)
#     print(alice_msg.to_bytes(11, byteorder='big'))
#
#
# main()
