import pygame
import socket
import threading
import json
import sys
import time
from .settings import *

from .types.game_state import GameState

class GameClient:
    def __init__(self, server_ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_id = None
        self.state = GameState()
        self.connected = False
        self.server_ip = server_ip
        self.game_started = False 
        self.countdown_value = 0 
        self.waiting_for_players = True 

        self.visual_players = {}

        self.last_move_time = 0
        self.move_delay = 100
        self.player_name = None

    def connect(self):
        try:
            self.sock.connect((self.server_ip, PORT))
            threading.Thread(target=self.receive_loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False

    def receive_loop(self):
        while True:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data: break

                msg = json.loads(data.decode('utf-8'))
                
                msg_type = msg.get("type")

                if msg_type == "init":
                    self.connected = True
                    self.my_id = msg["id"]
                    print(f"[TERMINAL] Conectado. ID: {self.my_id}. Esperando rival...")

                    self.send_name(self.player_name)

                elif msg_type == "countdown":
                    self.waiting_for_players = False
                    self.countdown_value = msg["value"]
                    print(f"[TERMINAL] Cuenta atrás: {self.countdown_value}")

                elif msg_type == "game_start":
                    self.game_started = True
                    self.countdown_value = 0

                    if "state" in msg:
                        self.state.update(msg["state"])

                    print(f"[TERMINAL] ¡JUEGO INICIADO!")

                elif msg_type == "update":
                    self.state.update(msg["state"])

                for pid, player_obj in self.state.players.items():
                    if pid not in self.visual_players:
                        gx, gy = player_obj.pos
                        self.visual_players[pid] = {'x': gx * GRID_CELL, 'y': gy * GRID_CELL}

            except json.JSONDecodeError as e:
                print(e)
                pass
            except Exception as e:
                print(e)
                break

    def send_action(self, action):
        if self.connected and self.game_started:
            try:
                mensaje = json.dumps({"action": action})
                self.sock.send(mensaje.encode('utf-8'))
            except Exception as e:
                print(e)
                pass

    def send_name(self, msg):
        if self.connected:
            try:
                mensaje = json.dumps({"name": msg})
                self.sock.send(mensaje.encode('utf-8'))
            except Exception as e:
                print(e)
                pass

    def run_game(self, title_suffix=""):
        pygame.init()
        screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(f"Cliente {self.my_id}")
        clock = pygame.time.Clock()

        font = pygame.font.SysFont("Arial", 60, bold=True)
        font_small = pygame.font.SysFont("Arial", 30)
        self.font_score = pygame.font.SysFont("Arial", 20, bold=True)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
            if self.game_started and self.state.status == "PLAYING": 
                current_time = pygame.time.get_ticks()
                if current_time - self.last_move_time > self.move_delay:
                    keys = pygame.key.get_pressed()
                    dx, dy = 0, 0
                    if keys[pygame.K_w]: dx, dy = 0, -1
                    elif keys[pygame.K_s]: dx, dy = 0, 1
                    elif keys[pygame.K_a]: dx, dy = -1, 0
                    elif keys[pygame.K_d]: dx, dy = 1, 0
                    
                    if dx != 0 or dy != 0:
                        self.send_action((dx, dy))
                        self.last_move_time = current_time

            screen.fill(COLORES["BG"])
            
            if self.waiting_for_players:
                text = font_small.render("Esperando jugadores...", True, COLORES["TEXT"])
                screen.blit(text, (ANCHO//2 - text.get_width()//2, ALTO//2))
            
            elif not self.game_started and self.countdown_value > 0:
                self.draw_grid(screen)
                text = font.render(str(self.countdown_value), True, (255, 0, 0))
                screen.blit(text, (ANCHO//2 - text.get_width()//2, ALTO//2 - text.get_height()//2))
            
            else:
                self.draw_grid(screen)
                self.draw_spawn_points(screen)
                self.draw_flag(screen)
                self.draw_players(screen)

                if self.state.status == "FINISHED":
                    self.draw_game_over(screen, font) 
                    pygame.display.flip()
                    
                    time.sleep(5)

                    print("Juego terminado. Cerrando cliente.")
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(FPS)

    def draw_grid(self, screen):
        for x in range(0, GRID_W):
            for y in range(0, GRID_H):
                pygame.draw.rect(screen, COLORES["GRID-CELL-1"], 
                               (x * GRID_CELL, y * GRID_CELL, GRID_CELL, GRID_CELL))
                pygame.draw.rect(screen, COLORES["GRID-CELL-2"], 
                               (x * GRID_CELL, y * GRID_CELL, GRID_CELL, GRID_CELL), 1)

    def draw_spawn_points(self, screen):
        for i, (gx, gy) in enumerate(SPAWN_POINTS):
            x_px = gx * GRID_CELL
            y_px = gy * GRID_CELL
            color = PLAYER_PALETTE[i % len(PLAYER_PALETTE)]
            rect = pygame.Rect(x_px, y_px, GRID_CELL, GRID_CELL)
            pygame.draw.rect(screen, color, rect, width=4, border_radius=5)

    def draw_players(self, screen):
        LERP_FACTOR = 0.4
        
        for pid, player in self.state.players.items():
            
            gx, gy = player.pos 
            color = player.color
            
            target_px = gx * GRID_CELL
            target_py = gy * GRID_CELL

            if pid not in self.visual_players:
                self.visual_players[pid] = {'x': target_px, 'y': target_py}

            vis = self.visual_players[pid]
            vis['x'] += (target_px - vis['x']) * LERP_FACTOR
            vis['y'] += (target_py - vis['y']) * LERP_FACTOR
            
            draw_x, draw_y = int(vis['x']), int(vis['y'])

            pygame.draw.rect(screen, color, (draw_x, draw_y, GRID_CELL, GRID_CELL), border_radius=4)

            puntos = self.state.score.get(pid, 0)
            
            text_surf = self.font_score.render(f"{puntos}", True, (255, 255, 255))
            text_x = draw_x + (GRID_CELL // 2) - (text_surf.get_width() // 2)
            text_y = draw_y + (GRID_CELL // 2) - (text_surf.get_height() // 2)
            screen.blit(text_surf, (text_x, text_y))

        active_ids = list(self.state.players.keys())
        for pid in list(self.visual_players.keys()):
            if pid not in active_ids:
                del self.visual_players[pid]

    def draw_flag(self, screen):
        flag = self.state.flag 
        
        gx, gy = flag.pos 
        x_px = gx * GRID_CELL
        y_px = gy * GRID_CELL
        color = flag.color

        offset_y = 0
        if flag.carrier is not None:
            offset_y = -15 

        pygame.draw.line(screen, (200, 200, 200), 
                        (x_px + 5, y_px + 5 + offset_y), 
                        (x_px + 5, y_px + 30 + offset_y), 3)

        puntos = [
            (x_px + 5, y_px + 5 + offset_y),
            (x_px + 5, y_px + 20 + offset_y),
            (x_px + 25, y_px + 12 + offset_y)
        ]
        pygame.draw.polygon(screen, color, puntos)

    def draw_game_over(self, screen, font_big):
        overlay = pygame.Surface((ANCHO, ALTO))
        overlay.set_alpha(180) 
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))


        winner_name = self.state.winner if self.state.winner else "Desconocido"
        
        txt_ganador = font_big.render(f"¡GANADOR!", True, (255, 215, 0))
        txt_nombre = font_big.render(f"{winner_name}", True, (255, 255, 255))
        
        rect_ganador = txt_ganador.get_rect(center=(ANCHO//2, ALTO//2 - 40))
        rect_nombre = txt_nombre.get_rect(center=(ANCHO//2, ALTO//2 + 40))
        
        screen.blit(txt_ganador, rect_ganador)
        screen.blit(txt_nombre, rect_nombre)

        font_s = pygame.font.SysFont("Arial", 20)
        txt_cerrar = font_s.render("Cerrando aplicación...", True, (200, 200, 200))
        screen.blit(txt_cerrar, (ANCHO//2 - txt_cerrar.get_width()//2, ALTO - 50))