import sympy
import random
from pyasn1.codec.der.encoder import encode as der_encoder
from pyasn1.codec.der.decoder import decode as der_decoder
from . import asn1struct


class ElGamal(object):
    def __init__(self, need_init: bool = True, p: int = None, g: int = None,
                 dimension: int = 256):
        if need_init:
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
            self.shared_key = pow(self.g, self.x, self.p)

    def _func_encrypt(self, msg: int, shared_key: int):
        return pow(msg - shared_key, 1, self.p)

    def _reversed_func_encrypt(self, c: int, shared_key: int):
        return pow(c + shared_key, 1, self.p)

    # msg must be lower than self.p
    def encrypt(self, shared_key: int, msg: int):
        if msg >= self.p:
            return None

        common_shared_key = pow(shared_key, self.x, self.p)
        return self._func_encrypt(msg=msg, shared_key=common_shared_key)

    def decrypt(self, shared_key: int, c: int):
        common_shared_key = pow(shared_key, self.x, self.p)
        return self._reversed_func_encrypt(c=c, shared_key=common_shared_key)

    def encode(self, bobs_shared_key: int, encr_sym_key: int, encr_data: bytes) \
            -> bytes:
        struct = asn1struct.ElGamalStruct()

        # Create structure and pack it
        struct["keys"]["first_key"]["algorithm_id"] = b"\x80\x01\x02\x03"
        struct["keys"]["first_key"]["str_key_id"] = "test"
        struct["keys"]["first_key"]["public_key"]["a_x"] = self.shared_key
        struct["keys"]["first_key"]["parameters"]["prime"] = self.p
        struct["keys"]["first_key"]["parameters"]["generator"] = self.g
        struct["keys"]["first_key"]["ciphertext"]["a_y"] = bobs_shared_key
        struct["keys"]["first_key"]["ciphertext"]["c"] = encr_sym_key
        struct["payload"]["payload_id"] = 0x0132.to_bytes(2, byteorder="big")
        struct["payload"]["file_len"] = len(encr_data)

        encoded_header = der_encoder(struct)
        return encoded_header + encr_data

    def decode(self, encoded_msg: bytes, checks: bool = True) -> (int, int, bytes):
        struct, encr_data = der_decoder(encoded_msg, asn1Spec=asn1struct.ElGamalStruct())

        bobs_shared_key = int(struct["keys"]["first_key"]["public_key"]["a_x"])
        p = int(struct["keys"]["first_key"]["parameters"]["prime"])
        g = int(struct["keys"]["first_key"]["parameters"]["generator"])
        shared_key = int(struct["keys"]["first_key"]["ciphertext"]["a_y"])
        encr_sym_key = int(struct["keys"]["first_key"]["ciphertext"]["c"])
        data_len = int(struct["payload"]["file_len"])

        if data_len != len(encr_data):
            print("Warning: unknown message length")
            encr_data = b''

        # Check values
        if checks:
            if p != self.p:
                print("Warning: p is not equal")
                self.p = p

            if g != self.g:
                print("Warning: g is not equal")
                self.g = g

            if shared_key != self.shared_key:
                print("Error: unknown shared key")
                return 0, 0, b''
        else:
            self.p = p
            self.g = g
            self.x = random.randint(2, (self.p - 1))
            self.shared_key = pow(self.g, self.x, self.p)

        return bobs_shared_key, encr_sym_key, encr_data

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
