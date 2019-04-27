import socket
from time import process_time
from enum import Enum, auto
from typing import Tuple, List, Dict

BACKLOG: int = 10
RECONNECT_DELAY = 1
LISTENER_TIMEOUT = 1
Listener = Tuple[str, int]


class Listener:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.last_update = 0
        self.status: SocketStatus = SocketStatus.INACTIVE
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(LISTENER_TIMEOUT)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, msg):
        self.socket.sendall(msg)
        self.last_update = process_time()

    def close(self):
        self.socket.shutdown(socket.SHUT_RD)
        self.socket.close()

    def __str__(self):
        return f"{self.host}:{self.port}"


class SocketStatus(Enum):
    ACTIVE = auto()
    INACTIVE = auto()


class Server:
    def __init__(self, listeners: List[Listener]):
        self.insock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeners = listeners
        self.reconnect_queue: List[Listener] = []
        self.last_reconnect: float = 0.0
        self.insock.settimeout(RECONNECT_DELAY)
        for listener in self.listeners:
            self.reconnect_queue.append(listener)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for listener in self.listeners:
            listener.close()
        self.insock.shutdown(socket.SHUT_RD)
        self.insock.close()

    def log(self, msg, prefix="MSG"):
        print(prefix, msg)

    def handle(self, clientsocket: socket.socket, address: str):

        self.log(f"New connection from {address}")
        buff = ""
        cur = ""
        while cur != "\n":
            cur = clientsocket.recv(1).decode()
            buff += cur
        buff += cur
        buff_split = buff.split(",", 1)
        if len(buff_split) == 2:
            self.send_all(buff_split[0].lower(), buff_split[1].encode())
        else:
            self.log(f"Got \"{buff[:-1]}\" from {address}, don't know what to do with that", prefix="ERR")

    def send_all(self, from_address: str, msg: bytes):
        for listener in self.listeners:
            try:
                self.log(f"Sending {msg} coming from {from_address} to {listener}")
                listener.send(msg)
            except OSError:
                self.reconnect_queue.append(listener)

    def listen(self, port: int):
        self.insock.bind(("localhost", port))
        self.insock.listen(BACKLOG)
        self.reconnect_all()
        while True:
            try:
                (clientsocket, address) = self.insock.accept()
                self.handle(clientsocket, address)
            except socket.timeout:
                self.reconnect_all()

    def reconnect_all(self):
        self.last_reconnect = process_time()
        for _ in range(len(self.reconnect_queue)):
            listener = self.reconnect_queue.pop()
            self.log(f"Connecting to {listener}")
            try:
                listener.connect()
                self.log(f"Succesfully connected to {listener}")
            except OSError:
                self.log(f"Could not connect to {listener}", "ERR")
                self.reconnect_queue.append(listener)


l1 = Listener("0.0.0.0", 5000)

with Server([l1]) as server:
    server.listen(12345)
