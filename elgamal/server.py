import socket

HOST = '127.0.0.1'
PORT = 65432


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)

        # Wait for connection
        while True:
            connection, client_address = s.accept()
            data = connection.recv(1024)
            print(data)
            connection.send(b"Response from server")


main()
