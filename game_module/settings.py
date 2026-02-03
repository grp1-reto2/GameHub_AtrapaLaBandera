HOST = "localhost" 
PORT = 5555
BUFFER_SIZE = 4096

ANCHO = 600
ALTO = 600

GRID_W = 21
GRID_H = 21
GRID_CELL = 25
FPS = 30

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
COLORES = {
    "BG" : (16, 15, 15),
    "GRID-CELL-1": (87, 86, 83),
    "GRID-CELL-2": (64, 62, 60),
    "TEXT": (206, 205, 195),
    1: (67, 133, 190),
    2: (209, 77, 65),
}

PLAYER_PALETTE = [
    (67, 133, 190),  
    (209, 77, 65),   
    (135, 154, 57),
    (208, 162, 21)
]

SPAWN_POINTS = [
    (0, 0),                  
    (GRID_W - 1, GRID_H - 1),     
    (GRID_W - 1, 0),            
    (0, GRID_H - 1)          
]

FLAG_POS = (10,10)