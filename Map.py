import pygame
from typing import List
import csv


class Node:
    def __init__(self, x: int, y: int, value: int, size: float, World: pygame.surface) -> None:
        self.value = value
        self.x = x
        self.y = y
        self.WORLD = World
        self.size = int(size)
        self.color = (255, 0, 0) if value == "1" else (255, 255, 255)
        self.neighbours: List[Node] = []
        self.gCost = 9999999
        self.hCost = 9999999

    def draw(self) -> None:
        pygame.draw.rect(self.WORLD, self.color,
                         pygame.Rect(self.x * self.size, self.y * self.size, self.size, self.size))


class Map:
    def __init__(self, World:pygame.Surface) -> None:
        self.WORLD:pygame.Surface = World
        #size in cells, to include padding
        self.mapSize:int = 26
        self.cellSize:float = self.WORLD.get_width() / self.mapSize
        self.grid:List[List[Node]] = []
        self.empty_cells = []
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
                if tempArray[y][x] != "1":
                    self.empty_cells.append([y, x])
                self.grid[y].append(Node(x, y, tempArray[y][x], self.cellSize, self.WORLD))

        self.set_neighbours()

        #for y in range(self.mapSize):
        #    for x in range(self.mapSize):
        #        self.grid[y][x].set_neighbours()



    def set_neighbours(self):
        for y in range(self.mapSize):
            for x in range(self.mapSize):
                #top left
                if y - 1 >= 0 and  x-1>=0:
                    self.grid[y][x].neighbours.append(self.grid[y-1][x-1])
                #top
                if y - 1 >= 0:
                    self.grid[y][x].neighbours.append(self.grid[y-1][x])
                #top right
                if y - 1 >=0 and x+1 < self.mapSize:
                    self.grid[y][x].neighbours.append(self.grid[y-1][x+1])
                #right
                if x+1 < self.mapSize:
                    self.grid[y][x].neighbours.append(self.grid[y][x+1])
                #right bottom
                if y + 1 < self.mapSize and x+1 < self.mapSize:
                    self.grid[y][x].neighbours.append(self.grid[y+1][x+1])
                #bottom
                if y + 1 < self.mapSize:
                    self.grid[y][x].neighbours.append(self.grid[y+1][x])
                #bottom left
                if y + 1 < self.mapSize and x-1 >=0:
                    self.grid[y][x].neighbours.append(self.grid[y + 1][x-1])
                #left
                if x-1>=0:
                    self.grid[y][x].neighbours.append(self.grid[y][x-1])


    def draw(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.draw()

        