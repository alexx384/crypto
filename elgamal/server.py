import socket
import sys

sys.path.append('..')
import lib


HOST = '127.0.0.1'
PORT = 65432


def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(1)

        # Wait for connection
        while True:
            connection, client_address = sock.accept()
            print("Received connection from ", client_address)

            elgamal = lib.ElGamal(need_init=False)

            # ===== Receive init message from server =====
            b_len_encoded_hello_msg = connection.recv(4)
            len_encoded_hello_msg = int.from_bytes(b_len_encoded_hello_msg,
                                                   byteorder='big')
            encoded_hello_msg = lib.recvall(connection, len_encoded_hello_msg)

            bobs_shared_key, _, _ = elgamal.decode(encoded_hello_msg, checks=False)

            # ===== Send Hello message to client =====
            hello_msg = "Hello World from server".encode("utf-8")
            sym_key, encr_data = lib.sym_encrypt_msg(hello_msg)
            encr_sym_key = elgamal.encrypt(bobs_shared_key, sym_key)
            encoded_hello_msg = elgamal.encode(bobs_shared_key, encr_sym_key,
                                               encr_data)

            len_encoded_hello_msg = len(encoded_hello_msg)
            b_len_encoded_hello_msg = len_encoded_hello_msg.to_bytes(
                4, byteorder='big')
            connection.send(b_len_encoded_hello_msg + encoded_hello_msg)

            # ===== Receive Hello message from client =====
            b_len_encoded_hello_msg = connection.recv(4)
            len_encoded_hello_msg = int.from_bytes(b_len_encoded_hello_msg,
                                                   byteorder='big')
            encoded_hello_msg = lib.recvall(connection, len_encoded_hello_msg)
            bobs_shared_key, encr_sym_key, encr_data = elgamal.decode(encoded_hello_msg)

            sym_key = elgamal.decrypt(bobs_shared_key, encr_sym_key)
            hello_msg = lib.sym_decrypt_msg(sym_key, encr_data)
            print(hello_msg.decode("utf-8"))

            connection.close()


server()
