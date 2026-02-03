# Diferentes clases para poder gestionar los datos de game_state mas fácil.

class Player:
    def __init__(self, name: str, color):
        self.name = name
        self.color = color

    def to_dict(self):
        return {
            "name" : self.name,
            "color" : self.color,
            "pos" : self.pos,
        }
    
    def update(self, data: dict):
        if "pos" in data:
            self.pos = tuple(data["pos"]) 
        if "color" in data:
            self.color = data["color"]
    
class Flag:
    def __init__(self):
        self.pos: tuple[int, int]= (0, 0)
        self.carrier = None
        self.color = (255, 255, 255)

    def to_dict(self):
        return {
            "pos": self.pos,
            "carrier" : self.carrier,
        }
    
    def update(self, data: dict):
        if "pos" in data:
            self.pos = tuple(data["pos"])
        self.carrier = data.get("carrier")

class GameState:
    def __init__(self):
        self.players: dict[int, Player] = {} 
        self.flag: Flag = Flag()
        self.score : dict[int, int]= {}    
        self.status = "WAITING"
        self.winner: str = ""

    def to_dict(self):  
        players_dict = {}
        for p_id, p_obj in self.players.items():
            data = p_obj.to_dict()
            data["id"] = p_id 
            players_dict[p_id] = data

        flag_dict = self.flag.to_dict()

        return {
            "players": players_dict,
            "flag": flag_dict,
            "score": self.score,
            "status": self.status,
            "winner": self.winner
        }
    
    def update(self, data: dict):
        if "flag" in data:
            self.flag.update(data["flag"])
        
        if "score" in data:
            self.score = {int(k): v for k, v in data["score"].items()}

        if "players" in data:
            incoming_players = data["players"]
            
            for pid_str, p_data in incoming_players.items():
                pid = int(pid_str)
                
                if pid not in self.players:
                    new_p = Player(p_data.get("name", "Unknown"), p_data.get("color", (255,255,255)))
                    self.players[pid] = new_p
                
                self.players[pid].update(p_data)

            current_ids = set(self.players.keys())
            incoming_ids = set(int(k) for k in incoming_players.keys())
            
            for missing_id in (current_ids - incoming_ids):
                del self.players[missing_id]

        if "status" in data:
            self.status = data["status"]
        
        if "winner" in data:
            self.winner = data["winner"]