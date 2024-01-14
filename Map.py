import pygame
from typing import List
from typing import Dict
import csv
import math

WALL = "1"

class Node:
    def __init__(self, x: int, y: int, type: str, size: float, World: pygame.surface) -> None:
        self.type = type
        self.x = x
        self.y = y
        self.WORLD = World
        self.size = int(size)
        self.worldX = self.x * self.size + self.size / 2
        self.worldY = self.y * self.size  + self.size / 2
        self.color = (255, 0, 0) if type == WALL else (255, 255, 255)
        self.neighbours: List[tuple[Node, float]] = []

    def draw(self) -> None:
        pygame.draw.rect(self.WORLD, self.color,
                         pygame.Rect(self.worldX - self.size / 2, self.worldY - self.size / 2, self.size, self.size))


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
                if tempArray[y][x] != WALL:
                    self.empty_cells.append([y, x])
                self.grid[y].append(Node(x, y, tempArray[y][x], self.cellSize, self.WORLD))

        self.set_neighbours()

        #for y in range(self.mapSize):
        #    for x in range(self.mapSize):
        #        self.grid[y][x].set_neighbours()



    def set_neighbours(self):
        sqrt2_weight = math.sqrt(2) * self.cellSize
        single_weight = self.cellSize
        for y in range(self.mapSize):
            for x in range(self.mapSize):
                if self.grid[y][x].type == WALL:
                    continue
                #top left
                if y - 1 >= 0 and  x-1>=0 and self.grid[y-1][x-1].type != WALL and self.grid[y-1][x].type != WALL and self.grid[y][x-1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y-1][x-1], sqrt2_weight))
                #top
                if y - 1 >= 0 and self.grid[y-1][x].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y-1][x], single_weight))
                #top right
                if y - 1 >=0 and x+1 < self.mapSize and self.grid[y-1][x+1].type != WALL and self.grid[y-1][x].type != WALL and self.grid[y][x+1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y-1][x+1], sqrt2_weight))
                #right
                if x+1 < self.mapSize and self.grid[y][x+1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y][x+1], single_weight))
                #right bottom
                if y + 1 < self.mapSize and x+1 < self.mapSize and self.grid[y+1][x+1].type != WALL and self.grid[y+1][x].type != WALL and self.grid[y][x+1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y+1][x+1], sqrt2_weight))
                #bottom
                if y + 1 < self.mapSize and self.grid[y+1][x].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y+1][x], single_weight))
                #bottom left
                if y + 1 < self.mapSize and x-1 >=0 and self.grid[y + 1][x-1].type != WALL and self.grid[y+1][x].type != WALL and self.grid[y][x-1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y + 1][x-1], sqrt2_weight))
                #left
                if x-1>=0 and self.grid[y][x-1].type != WALL:
                    self.grid[y][x].neighbours.append((self.grid[y][x-1], single_weight))


    def draw(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.draw()

    def coord_to_cell(self, coord:pygame.Vector2) -> Node:
        return self.grid[int(coord.y/self.cellSize)][int(coord.x/self.cellSize)]
        