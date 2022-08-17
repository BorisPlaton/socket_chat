import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))
with sock:
    while True:
        message = sock.recv(4096)
        if message:
            print(message)
