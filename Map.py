import pygame
from typing import List
import csv

class Map:
    class Node:
        def __init__(self, x:int, y:int, value:int, size:float, World:pygame.surface) -> None:
            self.value = value
            self.x = x
            self.y = y
            self.WORLD = World
            self.size = int(size)
            self.color = (255,0,0) if value == "1" else (255, 255, 255)
            
            
        def draw(self) -> None:
            pygame.draw.rect(self.WORLD, self.color, pygame.Rect(self.x * self.size, self.y * self.size, self.size, self.size))
        

    def __init__(self, World:pygame.Surface) -> None:
        self.WORLD:pygame.Surface = World
        
        #size in cells, to include padding
        self.mapSize:int = 26
        self.cellSize:float = self.WORLD.get_width() / self.mapSize
        self.grid:List[List[Map.Node]] = []
        self._initGrid()
        
    def _initGrid(self) -> None:
        tempArray = []        
        with open('map.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for y, row in enumerate(spamreader):
                tempArray.append([])
                for value in row:
                    tempArray[y].append(value)

        for y in range(self.mapSize):
            self.grid.append([])
            for x in range(self.mapSize):
                self.grid[y].append(Map.Node(x, y,tempArray[y][x], self.cellSize, self.WORLD))       

        for y in range(self.mapSize):
            for x in range(self.mapSize):
                self.grid[y][x].evaluate()

        self.evaluate()

    def draw(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.draw()
        