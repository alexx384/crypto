import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        server_address = (SERVER_HOST, SERVER_PORT)
        s.connect(server_address)
        s.send(b"Hello from client")


main()
