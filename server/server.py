import socket
import threading
import time
from map import generate_map

integer_map = generate_map()



class Receiver(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        print("starting the receiver, waiting for sockets")
        self.host = host
        self.port = port
        self.players = 0

    def run(self):
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.bind((self.host, self.port))
        while True:
            local_socket.listen()
            conn, address = local_socket.accept()
            client = Client(address, conn, self.players)
            client.start()
            server.clients.append(client)
            self.players += 1


class Server:
    def __init__(self):
        self.clients = []

    def send_all(self, header, msg):
        print("Sending", msg, "to all of the clients")
        for client in self.clients:
            client.send(header, msg)

    def send_all_but(self, id, header, msg):
        print("Sending", msg, "to all of the clients except", id)
        for client in self.clients:
            if client.id != id:
                client.send(header, msg)


class Client(threading.Thread):
    def __init__(self, address, connection, client_id):
        threading.Thread.__init__(self)
        self.id = client_id
        self.address = address
        self.conn = connection
        self.isRunning = True

        self.name = ""
        self.pos = (50, 50)

    def send(self, header, msg):
        packet = bytes(header + "|" + msg, 'utf-8')
        self.conn.sendall(packet)

    def send_large(self, header, msg, tail):
        packet = bytes(header + "|" + msg + "|" + tail, 'utf-8')
        self.conn.sendall(packet)

    def run(self):
        while self.isRunning:
            data = self.conn.recv(1024)
            if not data:
                server.clients.pop(server.clients.index(self))
                print(server.clients)
                self.isRunning = False
                break
            data = data.decode().split("|")
            print(data)
            if data[0] == "character_setup":
                self.name = data[1]
                self.send_large("map_start", get_map_as_string(), "map_end")
                time.sleep(0.5)
                msg = str(self.name + "|" + ":".join(str(s) for s in self.pos) + "|" + str(self.id))
                server.send_all_but(self.id, "new_player", msg)
                for client in server.clients:
                    if client.id != self.id:
                        msg = str(client.name + "|" + ":".join(str(s) for s in client.pos) + "|" + str(client.id))
                        self.send("new_player", msg)
            if data[0] == "update_my_position":
                self.pos = [int(i) for i in data[1].split(":")]
                server.send_all_but(self.id, "update_position", str(str(self.id) + "|" + ":".join(str(s) for s in self.pos)))



def get_map_as_string():
    row_arr = []
    for row in integer_map:
        string_ints = [str(integer)[0] for integer in row]
        row_arr.append(".".join(string_ints))
    return ":".join(row_arr)


receiver = Receiver('127.0.0.1', 65432)
receiver.start()
server = Server()
