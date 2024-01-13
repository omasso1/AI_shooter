import pygame
from typing import List
import Player
import Map

    
class Game:
    def __init__(self) -> None:
        self.WIDTH = 800
        self.HEIGHT = self.WIDTH
        self._init()
        
        self.players:List[Player.Player] = []
        self.map:Map.Map = Map.Map(self.WORLD)
        self.running:bool = True
        self.CLOCK = pygame.time.Clock()
        self.BACKGROUND = (255,255,255)

    def _init(self):
        pygame.init()
        pygame.display.set_caption('projekt 2')
        self.WORLD = pygame.display.set_mode((self.WIDTH, self.HEIGHT))


    def _update(self) -> None:
        deltaTime = self.CLOCK.tick(60)
        for player in self.players:
            player.update(deltaTime)


    def _draw(self) -> None:
        self.WORLD.fill(self.BACKGROUND)
        self.map.draw()
        for player in self.players:
            player.draw()
        pygame.display.update()

    def _pollEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        

    def mainLoop(self) -> None:
        while self.running:
            self._pollEvents()
            self._update()
            self._draw()
        