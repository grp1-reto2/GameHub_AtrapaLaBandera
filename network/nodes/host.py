from .base import NetworkNode
from .client import ClientNode
from .server import ServerNode


class HostNode(NetworkNode):
    def __init__(self, port):
        self.server = ServerNode("0.0.0.0", port)
        self.client = ClientNode("127.0.0.1", port)

    def start(self):
        self.server.start()
        self.client.start()

    def stop(self):
        self.server.stop()
        self.client.stop()

    def send(self, msg):
        self.client.send(msg) # Utiliza el Cliente para enviar el mensaje a su Servidor

    def poll(self):
        return self.client.poll()