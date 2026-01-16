class EventManager:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, callback):
        self.listeners.setdefault(event_type, []).append(callback)
    
    def emit(self, event):
        for callback in self.listeners.get(type(event), []):
            callback(event)