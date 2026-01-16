import pygame
from core import EventManager, NetworkManager, StateManager
from network.nodes import ClientNode

from core.events import request_JoinServer

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock

event_manager = EventManager()

node = ClientNode("", 52001)
node.start()

net_manager = NetworkManager(ClientNode, event_manager)
event_manager.subscribe(request_JoinServer, net_manager.handle_event) #Subscribir net_manager al evento.

state_manager = StateManager()

