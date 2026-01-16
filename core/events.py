class Event: pass

class request_JoinServer(Event): 
    def __init__(self, data):
        self.data = data
        
class response_JoinServer(Event):
    def __init__(self, data):
        self.data = data

class request_ServerInfo(Event): pass