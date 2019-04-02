import socket



def read_request(clientsocket):
    return clientsocket.recv(4096).decode()

def send_response(clientsocket, message):
    clientsocket.send(message.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
    serversocket.bind(('127.0.0.1', 5555))
    serversocket.listen(5)
    while 1:
        (clientsocket, address) = serversocket.accept()
        print(read_request(clientsocket))
        send_response(clientsocket, 'potato')
