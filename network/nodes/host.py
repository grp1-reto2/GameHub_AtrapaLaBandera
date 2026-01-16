from .base import NetworkNode
from .client import ClientNode
from .server import ServerNode


class HostNode(NetworkNode):
    def __init__(self):
        self.client = ClientNode()
        self.server = ServerNode()