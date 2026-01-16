from .base import NetworkNode
from transport import Socket

class ClientNode(NetworkNode):
    def __init__(self, server_ip, port):
        self.tcp_socket = Socket(server_ip, port, is_server=False)
    
    def start(self):
        self.tcp_socket.start()

    def stop(self):
        self.tcp_socket.stop()

    def send(self, msg):
        self.tcp_socket.send(msg)

    def poll(self):
        return [msg for sock, msg in self.tcp_socket.get_incoming_msgs()]