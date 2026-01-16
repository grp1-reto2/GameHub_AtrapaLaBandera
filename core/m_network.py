from core.events import Event, request_JoinServer, response_JoinServer

class NetworkManager:
    def __init__(self, node, event_bus):
        self.node = node 
        self.event_bus = event_bus

    def update(self):
        for msg in self.node.poll():
            event: Event | None = self._msg_to_event(msg)

            if event: self.event_bus.emit(event)

    def handle_event(self, event: Event):
        msg = self._event_to_msg(event)
        
        if msg: self.node.send(msg)

    def _msg_to_event(self, msg) -> Event | None:
        _type = msg.get("type")
        _data = msg.get("data")

        if _type == "RESPONSE_JOIN":
            return response_JoinServer(_data)
        
        return None
        
    def _event_to_msg(self, event: Event):
        if isinstance(event, request_JoinServer):
            return {"type": "RQUEST_JOIN", "data" : event.data}