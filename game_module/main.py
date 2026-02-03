import time 
from .server import GameServer
from .client import GameClient
from .settings import *

class Main:
    def __init__(self, name):
        self.server_instance = None
        self.name = name
        self.game = None

    def start_as_host(self):
        try: 
            print("[MANAGER] Iniciando servidor en segundo plano...")
            self.server_instance = GameServer() # Se crea la instancia del servidor.
            
            self.server_instance.start() # Inicia.
            
            print(f"[MANAGER] Servidor listo en IP: {self.server_instance.ip}")
        except OSError as e:
            print(f"[ERROR] No se pudo iniciar servidor: {e}")
            return False
        
        time.sleep(1) # Espera 1s, para tener tiempo a que se ejecute del todo el servidor.
        # Seguramente es demasiado, pero por si acaso.

        print("[MANAGER] Iniciando cliente del host...")
        target_ip = self.server_instance.ip if self.server_instance.ip else "127.0.0.1" # Se recoge la ip del servidor == "127.0.0.1"
        
        self.game = GameClient(target_ip) # Se crea la instancia el Cliente.
        
        if hasattr(self.game, 'player_name'): # Le pasamos el nombre.
            self.game.player_name = self.name

        if self.game.connect(): #Conectamos.
            print("[MANAGER] Cliente conectado. Abriendo ventana...")
            self.game.run_game()
        else:
            print("[ERROR] El cliente del host no pudo conectarse al servidor.")

    def start_as_client(self, ip):
        try:
            self.game = GameClient(ip)
            
            if hasattr(self.game, 'player_name'):
                self.game.player_name = self.name

            if self.game.connect():
                print("[MANAGER] Conectado. Abriendo ventana...")
                self.game.run_game()
            else:
                print("[ERROR] No se pudo conectar al servidor.")
        except Exception as e:
            print(f"[ERROR CRÍTICO] {e}")
            import traceback; traceback.print_exc()
    