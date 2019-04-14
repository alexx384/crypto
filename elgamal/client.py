import socket
import sys

sys.path.append('..')
import lib


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432


def client():
    elgamal = lib.ElGamal()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_address = (SERVER_HOST, SERVER_PORT)
        sock.connect(server_address)

        # ===== Send init message to server =====
        encoded_init_msg = elgamal.encode(0, 0, b'')

        len_encoded_init_msg = len(encoded_init_msg)
        b_len_encoded_init_msg = len_encoded_init_msg.to_bytes(4,
                                                               byteorder='big')
        sock.send(b_len_encoded_init_msg + encoded_init_msg)

        # ===== Receive Hello message from server =====
        b_len_encoded_hello_msg = sock.recv(4)
        len_encoded_hello_msg = int.from_bytes(b_len_encoded_hello_msg,
                                               byteorder='big')
        encoded_hello_msg = lib.recvall(sock, len_encoded_hello_msg)

        bobs_shared_key, encr_sym_key, encr_data = elgamal.decode(encoded_hello_msg)
        sym_key = elgamal.decrypt(bobs_shared_key, encr_sym_key)
        hello_msg = lib.sym_decrypt_msg(sym_key, encr_data)
        print(hello_msg.decode("utf-8"))

        # ===== Send Hello message to server =====
        hello_msg = "Hello World from client".encode("utf-8")
        sym_key, encr_data = lib.sym_encrypt_msg(hello_msg)
        encr_sym_key = elgamal.encrypt(bobs_shared_key, sym_key)
        encoded_hello_msg = elgamal.encode(bobs_shared_key, encr_sym_key, encr_data)

        len_encoded_hello_msg = len(encoded_hello_msg)
        b_len_encoded_hello_msg = len_encoded_hello_msg.to_bytes(
            4, byteorder='big')
        sock.send(b_len_encoded_hello_msg + encoded_hello_msg)

    print("Session is successfully ended")


client()
