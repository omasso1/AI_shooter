from typing import List
from Supply import Supply
from Player import Player
from Projectile import Projectile

supplies: List[Supply] = []
projectiles: List[Projectile] = []
max_fov = 90
max_player = 3
players: List[Player] = []
WIDTH = 806
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 205)
GREEN = (0, 205, 0)
PURPLE = (148, 0, 211)
BROWN = (128, 0, 0)
PRIMARY_AMMO_COLOR = (175, 155, 96)
SECONDARY_AMMO_COLOR = (138, 127, 128)
ARMOR_COLOR = (216, 216, 216)
HEALTH_COLOR =(35, 64, 142)

PLAYER_COLORS = [BLUE, GREEN, PURPLE, BROWN]

