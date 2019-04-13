import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import gamal
import asn1

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432


def add_padding(value: bytes, pad_size: int = 8):
    if (len(value) % pad_size) != 0:
        to_pad = len(value) % pad_size
        integral_data = value[:(len(value) - to_pad)]
        unpadded_data = value[(len(integral_data)):]

        data_block = unpadded_data + b'\x00' * (8 - len(unpadded_data))

        return integral_data + data_block

    else:
        return value


def del_padding(value: bytes, real_size: int, pad_size: int = 8):
    if len(value) > real_size:
        integral_data = value[:(len(value) - pad_size)]
        padded_data = value[len(integral_data):]

        sub = len(value) - real_size
        data = padded_data[:(8 - sub)]

        return integral_data + data

    else:
        return value


def sym_encrypt_msg(data: bytes) -> (int, bytes):
    key = os.urandom(24)
    triple_des = algorithms.TripleDES(key)
    cipher = Cipher(algorithm=triple_des, mode=modes.CBC(bytes(8)),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    b_data_len = (len(data) + 4).to_bytes(4, byteorder='big')
    data = b_data_len + data
    padded_data = add_padding(data)

    ciph_data = encryptor.update(padded_data)
    i_key = int.from_bytes(key, byteorder='big')
    return i_key, ciph_data


def sym_decrypt_msg(i_key: int, ciph_data: bytes) -> bytes:
    key = i_key.to_bytes(24, byteorder='big')
    triple_des = algorithms.TripleDES(key)
    cipher = Cipher(algorithm=triple_des, mode=modes.CBC(bytes(8)),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(ciph_data)
    data_len = int.from_bytes(padded_data[:4], byteorder='big')

    if (data_len - 4) > len(padded_data):
        print("Message is corrupted")
        return b''

    data = del_padding(padded_data, data_len)[4:]
    return data


def recvall(sock: socket.socket, n: int):
    """ Helper function to recv n bytes or return None if EOF is hit """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def client():
    elgamal = gamal.ElGamal()
    shared_key = elgamal.get_shared_key()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SERVER_HOST, SERVER_PORT)
        sock.connect(server_address)

        # ===== Send init message to server =====
        encoded_init_msg = asn1.encode(a_y=0, c=0, p=elgamal.p, g=elgamal.g,
                                       a_x=shared_key, encrypted_msg=b'')

        len_encoded_init_msg = len(encoded_init_msg)
        b_len_encoded_init_msg = len_encoded_init_msg.to_bytes(4,
                                                               byteorder='big')
        sock.send(b_len_encoded_init_msg + encoded_init_msg)

        # ===== Receive Hello message from server =====
        b_len_encoded_hello_msg = sock.recv(4)
        len_encoded_hello_msg = int.from_bytes(b_len_encoded_hello_msg,
                                               byteorder='big')
        encoded_hello_msg = recvall(sock, len_encoded_hello_msg)
        a_y, c, p, g, a_x, encrypted_hello_msg = asn1.decode(encoded_hello_msg)

        if a_x != shared_key:
            print("The MITM discovered")

        hello_msg_key = elgamal.decrypt_msg(a_y, c)
        hello_msg = sym_decrypt_msg(hello_msg_key, encrypted_hello_msg)
        print(hello_msg.decode("utf-8"))

        # ===== Send Hello message to server =====
        hello_msg = "Hello World from client".encode("utf-8")
        hello_msg_key, encrypted_hello_msg = sym_encrypt_msg(hello_msg)
        ciph_hello_msg_key = elgamal.encrypt_msg(a_y, hello_msg_key)
        encoded_hello_msg = asn1.encode(a_y=a_y, c=ciph_hello_msg_key,
                                        p=elgamal.p, g=elgamal.g,
                                        a_x=shared_key,
                                        encrypted_msg=encrypted_hello_msg)

        len_encoded_hello_msg = len(encoded_hello_msg)
        b_len_encoded_hello_msg = len_encoded_hello_msg.to_bytes(
            4, byteorder='big')
        sock.send(b_len_encoded_hello_msg + encoded_hello_msg)

    print("Session is successfully ended")


client()
