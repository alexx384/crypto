import sympy
from pygost import gost34112012256
import random
from . import elliptic
from . import asn1struct
from pyasn1.codec.der.encoder import encode as der_encoder
from pyasn1.codec.der.decoder import decode as der_decoder


class Gost3410(object):
    def __init__(self):
        # Point generation with great m is not a trivial task, so for now i will use the following constants
        self.a = 57896044625414088412406986721186632159605151965036429316594800028484330862738
        self.b = 53520245325288251180656443226770638951803337703360722011463033447827147086694
        self.p = 57896044625414088412406986721186632159605151965036429316594800028484330862739
        self.q = 28948022312707044206203493360593316079803694388568974763893400879284219004579

        self.p_x = 36066034950041118412594006918367965339490267219250288222432003968962962331642
        self.p_y = 54906983586985298119491343295734802658016371303757622466870297979342757624191
        self.d = 3373452694262939308592124827557035091303265571060727328929113752221898696042740095694987215545723900605561073171693636801501206615786632546812832785609947

        (self.q_x, self.q_y), _ = elliptic.mul_point_on_number((
            self.p_x, self.p_y), self.d, self.a, self.p)

        # if p is None:
        #     self.p = sympy.randprime(pow(2, 254), pow(2, 257))
        #
        # self.a, self.b = self._generate_curve(a, b)

    @staticmethod
    def _generate_curve(p: int, start_a: int = 0, start_b: int = 0):
        if start_a != 0:
            if start_a >= p:
                print("Warning: a is greater or equal p")
                start_a %= p

        if start_b != 0:
            if start_b >= p:
                print("Warning: b is greater or equal p")
                start_b %= p

        if start_a != 0 and start_b != 0:
            if Gost3410._is_j_invariant_good(start_a, start_b, p):
                print("Info: Parameters a and b are good")
                return start_a, start_b
            else:
                print("Error: Parameters a and b are bad and were cleared")
                start_a = 0
                start_b = 0

        a = 0
        b = 0

        while not Gost3410._is_j_invariant_good(a, b, p):
            if start_a == 0:
                a = p
                while a >= p:
                    a = sympy.randprime(pow(2, 254), pow(2, 257))
            else:
                a = start_a

            if start_b == 0:
                b = p
                while b >= p:
                    b = sympy.randprime(pow(2, 254), pow(2, 257))
            else:
                b = start_b

        return a, b

    @staticmethod
    def _is_j_invariant_good(a: int, b: int, p: int):
        x = 1728 * 4 * pow(a, 3)
        y = 4 * pow(a, 3) + 27 * pow(b, 2)
        y_1 = sympy.mod_inverse(y, p)

        j = (x * y_1) % p
        if j == 0 or j == 1728:
            return False
        else:
            return True

    def sign(self, filename: str, output: str):
        with open(filename, "rb") as file:
            data = file.read()

        data_hash = gost34112012256.GOST34112012(data)

        data_hash_digest = data_hash.digest()
        print(data_hash.hexdigest())

        alpha = int.from_bytes(data_hash_digest, byteorder='big')
        e = alpha % self.q
        if e == 0:
            e = 1

        s = 0
        r = 0
        while s == 0 or r == 0:
            k = random.randint(1, self.q - 1)
            (c_x, c_y), _ = elliptic.mul_point_on_number((self.p_x, self.p_y), k, self.a, self.p)
            r = c_x % self.q
            if r == 0:
                continue

            s = (r * self.d + k * e) % self.q

        result_data = self._encode(r, s, data)

        with open(output, "wb") as file:
            file.write(result_data)

        print("Successfully signed")

    def verify(self, filename: str):
        with open(filename, "rb") as file:
            encoded_data = file.read()

        r, s, data = self._decode(encoded_data)
        if r <= 0 or r >= self.q or s <= 0 or s >= self.q:
            print("Error: Invalid signature")

        data_hash = gost34112012256.GOST34112012(data)

        data_hash_digest = data_hash.digest()
        print(data_hash.hexdigest())

        alpha = int.from_bytes(data_hash_digest, byteorder='big')
        e = alpha % self.q
        if e == 0:
            e = 1

        v = sympy.mod_inverse(e, self.q)

        z_1 = (s * v) % self.q
        z_2 = (-r * v) % self.q

        tmp_1, _ = elliptic.mul_point_on_number((self.p_x, self.p_y), z_1, self.a, self.p)
        tmp_2, _ = elliptic.mul_point_on_number((self.q_x, self.q_y), z_2, self.a, self.p)
        (c_x, c_y), _ = elliptic.sum_points(tmp_1, tmp_2, self.a, self.p)
        result = c_x % self.q

        if result == r:
            print("Signature is correct")
        else:
            print("Signature is wrong")

    def _encode(self, r: int, s: int, data: bytes) -> bytes:
        private = asn1struct.Gost3410SignStruct()
        private["keys"]["first_key"]["algorithm_id"] = b"\x80\x06\x07\x00"
        private["keys"]["first_key"]["str_key_id"] = "gostSignKey"
        private["keys"]["first_key"]["public_key"]["q_x"] = self.q_x
        private["keys"]["first_key"]["public_key"]["q_y"] = self.q_y
        private["keys"]["first_key"]["parameters"]["field"]["p"] = self.p
        private["keys"]["first_key"]["parameters"]["curve"]["a"] = self.a
        private["keys"]["first_key"]["parameters"]["curve"]["b"] = self.b
        private["keys"]["first_key"]["parameters"]["generator"]["p_x"] = self.p_x
        private["keys"]["first_key"]["parameters"]["generator"]["p_y"] = self.p_y
        private["keys"]["first_key"]["parameters"]["q"] = self.q
        private["keys"]["first_key"]["signature"]["r"] = r
        private["keys"]["first_key"]["signature"]["s"] = s

        encoded_header = der_encoder(private)
        return encoded_header + data

    def _decode(self, encoded_data):
        private, data = der_decoder(encoded_data,
                                    asn1Spec=asn1struct.
                                    Gost3410SignStruct())

        self.q_x = private["keys"]["first_key"]["public_key"]["q_x"]
        self.q_y = private["keys"]["first_key"]["public_key"]["q_y"]
        self.p = private["keys"]["first_key"]["parameters"]["field"]["p"]
        self.a = private["keys"]["first_key"]["parameters"]["curve"]["a"]
        self.b = private["keys"]["first_key"]["parameters"]["curve"]["b"]
        self.p_x = private["keys"]["first_key"]["parameters"]["generator"]["p_x"]
        self.p_y = private["keys"]["first_key"]["parameters"]["generator"]["p_y"]
        self.q = private["keys"]["first_key"]["parameters"]["q"]
        r = private["keys"]["first_key"]["signature"]["r"]
        s = private["keys"]["first_key"]["signature"]["s"]

        return r, s, data
