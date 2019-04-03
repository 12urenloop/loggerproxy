import configparser
import socket
import _thread

lck = _thread.allocate_lock()

config = configparser.ConfigParser()
config.read("./proxyconfig.ini")
servers = config["cvc_servers"]
logging_conf = config["logging"]

connections = {}
for key, ip_port in servers.items():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip, port = ip_port.split(":")
        sock.connect((ip, int(port)))
        connections[key] = sock
    except:
        print(f"Could not connect to {ip_port}")

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind((logging_conf["proxy_ip"], int(logging_conf["proxy_port"])))
proxy_socket.listen(10)

def log(msg, prefix="MSG"):
    global lck
    lck.acquire(timeout=-1)
    with open(logging_conf["logfile_path"], "a") as f:
        f.write(f"[{prefix}] {msg}\n")
    lck.release()

def handle_connection(clientsocket, address):
    buff = ""
    while clientsocket:
        data = clientsocket.recv(1).decode()
        if data == "\n":
            buff += "\n"
            buff_split = buff.split(",", 1)
            if len(buff_split) == 2 and buff_split[0] in connections:
                connections[buff_split[0]].sendall(buff_split[1].encode())
                log(f"Sending \"{buff_split[1][:-1]}\" from {address} to {buff_split[0]}")
            else:
                log(f"Got \"{buff[:-1]}\" from {address}, don't know what to do with that", prefix="ERR")
            buff = ""
        else:
            buff += data
try:
    while True:
        _thread.start_new_thread(handle_connection, proxy_socket.accept())
finally:
    proxy_socket.close()
    for sock in connections.values():
        sock.close()
