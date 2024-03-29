import pygame
import globals
from typing import List
import Player
import Map
import random
from Supply import Supply


class Game:
    i=4
    def __init__(self) -> None:
        self.WIDTH = globals.WIDTH
        self.HEIGHT = self.WIDTH
        self._init()
        self.map:Map.Map = Map.Map(self.WORLD)
        globals.players.append(Player.Player(self.map, [1, 1], globals.BLUE, 1,10,1))
        globals.players.append(Player.Player(self.map, [21, 21], globals.GREEN,18,16,2))
        globals.players.append(Player.Player(self.map, [1, 23], globals.PURPLE,1,21,3))
        globals.players.append(Player.Player(self.map, [24, 1], globals.BROWN,1,21,4))
        self.running:bool = True
        self.CLOCK = pygame.time.Clock()
        self.BACKGROUND = globals.WHITE
        self.last_supplies_drop = pygame.time.get_ticks()
        self.supplies_cooldown = 10000

    def _init(self):
        pygame.init()
        pygame.display.set_caption('projekt 2')
        self.WORLD = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def _create_supplies(self):
        timer = pygame.time.get_ticks()
        if timer - self.last_supplies_drop > self.supplies_cooldown:
            empty_cells = self.map.empty_cells
            if len(empty_cells) > 0:
                #wykomentowany arrmor
                #position = self.random_spot_for_supply_in_game_units(empty_cells)
                #globals.supplies.append(Supply(True, False, False, False, position, self.WORLD))
                position = self.random_spot_for_supply_in_game_units(empty_cells)
                globals.supplies.append(Supply(False, True, False, False, position, self.WORLD))
                position = self.random_spot_for_supply_in_game_units(empty_cells)
                globals.supplies.append(Supply(False, False, True, False, position, self.WORLD))
                position = self.random_spot_for_supply_in_game_units(empty_cells)
                globals.supplies.append(Supply(False, False, False, True, position, self.WORLD))
                self.last_supplies_drop = timer

    def random_spot_for_supply_in_game_units(self, empty_cells):
        random_spot = random.choice(empty_cells)
        position = pygame.Vector2((random_spot[1] * self.map.cellSize)+self.map.cellSize/2, (random_spot[0] * self.map.cellSize)+self.map.cellSize/2)
        empty_cells.remove(random_spot)
        return position

    def _update(self) -> None:
        deltaTime = self.CLOCK.tick(60)
        for player in globals.players:
            player.update(deltaTime)

    def _respawnPlayerIfNeeded(self):
        if len(globals.players) < globals.max_player:
            self.i +=1
            random_spot = random.choice(self.map.empty_cells)
            colors = []
            for player in globals.players:
                colors.append(player.color)
            colors_to_choose = []
            for element in globals.PLAYER_COLORS:
                if element not in colors:
                    colors_to_choose.append(element)

            globals.players.append(Player.Player(self.map, random_spot, random.choice(colors_to_choose), 18, 16,self.i))


    def _draw(self) -> None:
        self.WORLD.fill(self.BACKGROUND)
        self.map.draw()
        deltaTime = self.CLOCK.tick(60)
        for player in globals.players:
            player.draw()
        for supply in globals.supplies:
            supply.draw()
        for projectile in globals.projectiles:
            projectile.draw(deltaTime)

        pygame.display.update()

    def _pollEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        

    def mainLoop(self) -> None:
        while self.running:
            self._pollEvents()
            self._respawnPlayerIfNeeded()
            self._create_supplies()
            self._update()
            self._draw()
        