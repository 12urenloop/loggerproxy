from typing import Tuple, Type, List
from socketserver import ThreadingTCPServer, ThreadingMixIn, BaseRequestHandler
from time import time
import socket
import threading
RECONNECT_DELAY = 1

def log(msg, prefix="MSG"):
    print(f"{prefix}: {msg}")


class Listener:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.last_updated: float = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, msg: bytes):
        self.socket.sendall(msg)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()

    def __str__(self):
        return f"{self.host}:{self.port}"
    def __repr__(self):
        return self.__str__()


class Handler(BaseRequestHandler):
    def setup(self):
        self.server.reconnect_all()
        self.server.reconnect_queue.clear()

    def handle(self):
        buff = ""
        cur = ""
        while cur != "\n":
            cur = self.request.recv(1).decode()
            buff += cur
        buff += cur
        buff_split = buff.split(",", 1)
        if len(buff_split) == 2:
            msg = buff_split[1].encode()
            for listener in self.server.listeners:
                try:
                    listener.send(msg)
                    log(f"sending {msg} from {self.client_address} to {listener}")
                except OSError:
                    log(f"Failed to send to {listener}")
                    self.server.reconnect_queue.append(listener)

        else:
            log(f"Got {buff[:-1]} from {self.client_address}, don't know what to do with it")


class Server(ThreadingTCPServer):

    def __init__(self, address: Tuple[str, int], handler: Type[BaseRequestHandler], listeners: List[Listener]):
        super().__init__(address, handler)
        self.address_family = socket.SOCK_STREAM
        self.listeners = listeners
        self.reconnect_queue = listeners[:]
        self.last_reconnect = -RECONNECT_DELAY
        self.reconnect_all()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        for listener in self.listeners:
            listener.__exit__()
        self.shutdown()

    def reconnect_all(self):
        if time() - self.last_reconnect > RECONNECT_DELAY:
            self.last_reconnect = time()
            for _ in range(len(self.reconnect_queue)):
                listener = self.reconnect_queue.pop(0)
                try:
                    log(f"Connecting to {listener}")
                    listener.connect()
                except OSError:
                    log(f"Could not connect to {listener}, will retry later")
                    self.reconnect_queue.append(listener)


HOST, PORT = "localhost", 12345
l1 = Listener("0.0.0.0", 5000)
l2 = Listener("0.0.0.0", 5001)
with Server((HOST, PORT), Handler, [l1, l2]) as server:
    server.serve_forever()
