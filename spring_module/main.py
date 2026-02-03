import requests
import json
import threading

API_BASE_URL = "http://localhost:8080/api"

class SpringModule:
    def __init__(self, game_server):
        self.server = game_server

    def save_game_data(self, duration, players_dict, scores_dict):
        threading.Thread(target=self._process_and_send, args=(duration, players_dict, scores_dict)).start()

    def _process_and_send(self, duration, players_dict, scores_dict):
        print("[SPRING] Iniciando guardado de JUGADORES...")

        try:
            for p_id, player_obj in players_dict.items():
                
                player_payload = {
                    "nombre": str(player_obj.name), 
                    "email": f"{str(player_obj.name).lower()}@email.com"
                }

                try:
                    resp = requests.post(f"{API_BASE_URL}/jugadores", json=player_payload)
                    
                    if resp.status_code == 200 or resp.status_code == 201:
                        data = resp.json()
                        real_id = data.get("id", "Desconocido")
                        print(f" Jugador '{player_obj.name}' guardado. ID Base de Datos: {real_id}")
                    else:
                        print(f" Spring rechazó al jugador '{player_obj.name}': {resp.status_code} - {resp.text}")

                except Exception as e:
                    print(f"Error conectando para guardar jugador {player_obj.name}: {e}")

        except Exception as e:
            print(f"Error general en el módulo Spring: {e}")