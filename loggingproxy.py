import socket

LOGFILE = 'logger.txt'
CVC_IP = '127.0.0.1'
CVC_PORT = 5555
# PROXY_IP: normaal socket.gethostname() om te connecteren vanbuitenaf, localhost(127.0.0.1) om te testen:
PROXY_IP = '127.0.0.1'
PROXY_PORT = 1234

def logmessage(fromip, toip, message):
    with open(LOGFILE, "a+") as writefile:
        writefile.write(f'{fromip} -> {toip}: {message}\n')


def read_request(clientsocket):
    return clientsocket.recv(4096).decode()

def send_response(clientsocket, message):
    clientsocket.send(message.encode())


def server_sendrecv(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
        serversocket.connect((CVC_IP, CVC_PORT))
        serversocket.sendall(message.encode())
        response = serversocket.recv(4096).decode()

        return response

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
    serversocket.bind((PROXY_IP, PROXY_PORT))
    serversocket.listen(5)
    while 1:
        try:
            (clientsocket, address) = serversocket.accept()

            # Receive request from client, and log
            request = read_request(clientsocket)
            logmessage(address[0], CVC_IP, request)

            # Send request to server, wait for response, and log
            response = server_sendrecv(request)
            logmessage(CVC_IP, address[0], response)

            if response == 0:
                raise socket.error('server socked closed')
            # Send server response to client
            send_response(clientsocket, response)
        except socket.error:
            logmessage('ERROR', 'ERROR', 'errorlog.txt')
        finally:
            clientsocket.close()