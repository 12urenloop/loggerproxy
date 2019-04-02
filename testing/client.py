import socket

messages = ['1qsdfjmlksjdfmlkjqsdf', '2qsdfkùqlmdskfùmsqlkdf', '3fmlqjksdfmlkqjdf', '4skdfjmlkqsdjfmlkqsjdf', '5mlqdsfqsdfqksdjfmlj']

def send_request(socket, message):
    socket.sendall(message.encode())

def read_response(socket):
    return socket.recv(4096).decode()

for message in messages:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 1234))
        send_request(s, message)
        print(read_response(s))
