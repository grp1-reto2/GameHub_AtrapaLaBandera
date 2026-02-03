import socket, threading, json, time
from .settings import *
from .utils import *
from .types.game_state import GameState, Player

from flask_module import FlaskModule
from spring_module import SpringModule

class GameServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = get_local_ip()
        self.sock.bind(("0.0.0.0", PORT))

        self.sock.listen()
        self.clients = []
        self.game_state = GameState()
        self.game_state.flag.pos = FLAG_POS

        self.running = True
        self.game_started = False
        self.game_end_time = None 

    def start(self):
        print(f"[SERVIDOR] Iniciado en puerto {PORT}")
        threading.Thread(target=self._accept_loop, daemon=True).start() # Se inicia el loop para acpetar conexión en un hilo.

        # Se crean tanto el modulo de Flask y la conexion a Spring.
        self.api = FlaskModule(self) 
        self.api.start() # y se inicia.

        self.spring = SpringModule(self)
        
    def _accept_loop(self):
        while self.running:
            try: 
                conn, addr = self.sock.accept()
                self.clients.append(conn)

                p_id = len(self.clients)

                color_index = (p_id - 1) % len(PLAYER_PALETTE)
                color = PLAYER_PALETTE[color_index]

                new_player = Player(f"Jugador {p_id}", color)
                self.game_state.players[p_id] = new_player
                self.game_state.score[p_id] = 0

                spawn_index = (p_id - 1) % len(SPAWN_POINTS)
                self.game_state.players[p_id].pos =  SPAWN_POINTS[spawn_index]
                
                threading.Thread(target=self._handle_client, args=(conn, p_id), daemon=True).start() # Un hilo por cada conexión.

                if len(self.clients) >= 4 and not self.game_started:
                    self.game_started = True
                    threading.Thread(target=self._start_countdown, daemon=True).start() #Al llegar al maximo de jugadores > iniciamos countdown.

            except Exception as e:
                print(e)
                break

    def _start_countdown(self):
        print(f"[SERVIDOR] ¡{len(self.clients)} jugadores conectados! Iniciando cuenta regresiva...")
        time.sleep(0.5)

        for i in range(5, 0, -1):
            msg = {"type": "countdown", "value": i}
            self.broadcast(msg)
            time.sleep(1)

        self.game_state.status = "PLAYING"
        self.start_time = time.time()
        
        print("[SERVIDOR] ¡GO!")
        start_msg = {
            "type": "game_start", 
            "state": self.game_state.to_dict(),
        }
        self.broadcast(start_msg) #Cuando termine > mensaje a todos.

    def _handle_client(self, conn, p_id): #loop de la conexión de cada cliente
        try:
            init_msg = json.dumps({"type" : "init", "id": p_id}) #mandamos id a cada cliente.
            conn.send(init_msg.encode())
        except Exception as e:
            print(e)
            if conn in self.clients: self.clients.remove(conn) # si por lo que se a da error. Se quita la conexión.
            return
        
        while self.running:
            try:
                data = conn.recv(1024)
                if not data: break
                msg = json.loads(data.decode())

                if self.game_state.status == "FINISHED":
                    continue # si estatus finished se ignora.
                
                    # diferentes eventos que llegan.
                if "name" in msg: #nombre de cada usuario.
                    player_name = msg["name"]
                    p = self.game_state.players.get(p_id)
                    if not p: continue

                    p.name = player_name

                if "action" in msg: # intento de movimiento de cada usuario.
                    # El servidor decide si el movimiento es valido o si hay cambio de bandera. O si hay punto > Bandera al medio.
                    dx, dy = msg["action"]

                    p = self.game_state.players.get(p_id)
                    if not p: continue
                    
                    current_x, current_y = p.pos
                    target_x, target_y = current_x + dx, current_y + dy

                    if target_x < 0 or target_x >= GRID_W or target_y < 0 or target_y >= GRID_H:
                        continue 
                    
                    posicion_ocupada = False
                    for other_id, other_player in self.game_state.players.items():
                        if other_id != p_id:
                            if other_player.pos == (target_x, target_y):
                                posicion_ocupada = True
                                flag = self.game_state.flag
                                if flag.carrier == other_id:
                                    flag.carrier = p_id

                    if not posicion_ocupada:
                        p.pos = (target_x, target_y)
                        flag = self.game_state.flag
                        
                        if flag.carrier == p_id:     
                            flag.pos = (target_x, target_y)
                            spawn_index = (p_id - 1) % len(SPAWN_POINTS)
                            my_spawn = SPAWN_POINTS[spawn_index]
                            
                            if (target_x, target_y) == my_spawn:
                                current_score = self.game_state.score.get(p_id, 0)
                                self.game_state.score[p_id] = current_score + 1
                                print(f"¡PUNTO! Marcador: {self.game_state.score}")
                                

                                flag.carrier = None
                                flag.pos = FLAG_POS 

                                if self.game_state.score[p_id] >= 2:
                                    print(f"¡JUGADOR {p_id} GANA LA PARTIDA!")
                                    self.game_state.status = "FINISHED"
                                    self.game_state.winner = p.name
                                    self.game_end_time = time.time() 

                                    duration = time.time() - self.start_time 

                                    self.spring.save_game_data(
                                        duration, 
                                        self.game_state.players, 
                                        self.game_state.score
                                    )
                        
                        elif flag.carrier is None:
                            if (target_x, target_y) == flag.pos:
                                flag.carrier = p_id
                                print(f"Jugador {p_id} cogió la bandera.")

                # Enviar update
                self.broadcast({"type": "update", "state": self.game_state.to_dict()}) 

            except Exception as e:
                print(f"[ERROR] {e}")
                break

        #Manejamos la desconexión  de un jugador.

        print(f"[SERVIDOR] Jugador {p_id} desconectado")
        
        if self.game_state.flag.carrier == p_id:
            self.game_state.flag.carrier = None
            self.game_state.flag.pos = FLAG_POS 

        if p_id in self.game_state.players: 
            del self.game_state.players[p_id]
            
        if conn in self.clients: 
            self.clients.remove(conn)
        conn.close()
        
        self.broadcast({"type": "update", "state": self.game_state.to_dict()})

    def broadcast(self, msg):
        try:
            msg_json = json.dumps(msg)
            data = msg_json.encode()
            
            for c in self.clients:
                try:
                    c.send(data)
                except:
                    pass
        except:
            pass