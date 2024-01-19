import pygame
import globals
from typing import List
from typing import Dict
import csv
import math
import Player
from common import *


WALL = 0
EMPTY = 1

class Node:
    def __init__(self, x: int, y: int, size: float, World: pygame.surface) -> None:
        self.type = WALL
        self.x = x
        self.y = y
        self.WORLD = World
        self.size = int(size)
        self.worldX = self.x * self.size + self.size / 2
        self.worldY = self.y * self.size  + self.size / 2
        self.color = globals.RED if type == WALL else globals.WHITE
        self.neighbours: List[tuple[Node, float]] = []

    def draw(self) -> None:
        #pygame.draw.rect(self.WORLD, self.color,
         #                pygame.Rect(self.worldX - self.size / 2, self.worldY - self.size / 2, self.size, self.size))
        #debug
        for neighbor in self.neighbours:
            pygame.draw.line(self.WORLD, (0,0,0), (self.worldX, self.worldY), (neighbor[0].worldX, neighbor[0].worldY))

class Obstacle:
    def __init__(self, points:List[pygame.Vector2], world:pygame.surface) -> None:
        self.points:List[pygame.Vector2] = points
        self.WORLD:pygame.surface = world
        self.color:tuple(int, int, int) = globals.OBSTACLE_COLOR
        self.lines:List[Segment] = []
        for i in range(len(self.points) - 1):
            self.lines.append(Segment(self.points[i].x, self.points[i].y, self.points[i+1].x, self.points[i+1].y))
        self.lines.append(Segment(self.points[len(self.points) - 1].x, self.points[len(self.points) - 1].y, self.points[0].x, self.points[0].y))

    def draw(self) -> None:
        pygame.draw.polygon(self.WORLD, self.color, self.points)

class Map:
    def __init__(self, World:pygame.Surface) -> None:
        self.WORLD:pygame.Surface = World
        #size in cells, to include padding
        self.mapSize:int = 26
        self.cellSize:float = self.WORLD.get_width() / self.mapSize
        self.grid:List[List[Node]] = []
        self.obstacles:List[Obstacle] = []
        self.empty_cells = []
        self._initGrid()
        
    def _initGrid(self) -> None:
        tempArray = []        
        for y in range(self.mapSize):
            self.grid.append([])
            for x in range(self.mapSize):
                self.grid[y].append(Node(x, y, self.cellSize, self.WORLD))
        v = pygame.Vector2
        
        self.obstacles.append(Obstacle([v(0, 0), v(0, 70), v(70, 0)], self.WORLD))
        self.obstacles.append(Obstacle([v(250, 100), v(100, 250), v(300, 300)], self.WORLD))
        self.obstacles.append(Obstacle([v(350,0), v(450, 0),v(450,20),v(370,20),v(370,130),v(450,130), v(450, 150), v(350,150)], self.WORLD))
        self.obstacles.append(Obstacle([v(570, 150), v(620,150), v(620,220), v(680,220), v(680,420), v(640,420),  v(600,360)], self.WORLD))
        self.obstacles.append(Obstacle([v(100, 400), v(150,400), v(150,470), v(250,470), v(250,400), v(300,400), v(325, 400), v(325,500), v(100,500)], self.WORLD))
        self.obstacles.append(Obstacle([v(450,400), v(530,410), v(530,510), v(600,610), v(540,640), v(400,520)], self.WORLD))
        self.obstacles.append(Obstacle([v(100,650), v(300, 600), v(400,700), v(260,700), v(230,690), v(100,690)], self.WORLD))
        self.obstacles.append(Obstacle([v(770,450),v(806, 450),v(806,650),v(770,650), v(770,580),v(690,580),v(690,550),v(770,550)], self.WORLD))
        self.obstacles.append(Obstacle([v(806,0), v(806,25), v(735,25), v(735,130), v(710,130), v(710,0)], self.WORLD))
        self.obstacles.append(Obstacle([v(610,700), v(635,700), v(635,806), v(610,806)], self.WORLD))

        self.set_neighbours(self.grid[3][0], [])


        #for y in range(self.mapSize):
        #    for x in range(self.mapSize):
        #        self.grid[y][x].set_neighbours()



    def set_neighbours(self, node:Node, visited:List[Node]):
        sqrt2_weight = math.sqrt(2) * self.cellSize
        single_weight = self.cellSize
        x = node.x
        y = node.y
        visited.append(node)
        
        def pDistance(targetX, targetY, lineX1, lineY1, lineX2, lineY2):
            A = targetX - lineX1
            B = targetY - lineY1
            C = lineX2 - lineX1
            D = lineY2 - lineY1

            dot = A * C + B * D
            len_sq = C * C + D * D
            param = -1
            if (len_sq != 0):
                param = dot / len_sq
            if (param < 0): 
                xx = lineX1
                yy = lineY1
            elif (param > 1):
                xx = lineX2
                yy = lineY2  
            else:
                xx = lineX1 + param * C
                yy = lineY1 + param * D
            

            dx = targetX - xx
            dy = targetY - yy
            return math.sqrt(dx * dx + dy * dy)
            
        def check_collision_with_obstacles(node1:Node, node2:Node):
            nonlocal self
            tooClose = False
            for obstacle in self.obstacles:
                for line in obstacle.lines:
                    nodeLine = Segment(node1.worldX, node1.worldY, node2.worldX, node2.worldY)
                    #check if obstacle is too close to nodes  
                    d1 = pDistance(node1.worldX, node1.worldY, line.x1, line.y1, line.x2, line.y2)
                    d2 = pDistance(node2.worldX, node2.worldY, line.x1, line.y1, line.x2, line.y2)
                    d3 = pDistance(line.x1, line.y1, nodeLine.x1, nodeLine.y1, nodeLine.x2, nodeLine.y2)
                    tooClose = tooClose or d1 < Player.Player.radius 
                    tooClose = tooClose or d2 < Player.Player.radius
                    tooClose = tooClose or d3 < Player.Player.radius
                    #check if lines intersect   
                    if line.intersects(nodeLine):
                        tooClose = True                    
            return tooClose

        #top left   
        if y - 1 >= 0 and x-1>=0:
            node2 = self.grid[y-1][x-1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, sqrt2_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)      
        #top
        if y - 1 >= 0 :
            node2 = self.grid[y-1][x]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, single_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #top right
        if y - 1 >=0 and x+1 < self.mapSize:
            node2 = self.grid[y-1][x + 1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, sqrt2_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #right
        if x+1 < self.mapSize:
            node2 = self.grid[y][x + 1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, single_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #right bottom
        if y + 1 < self.mapSize and x + 1 < self.mapSize:
            node2 = self.grid[y+1][x+1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, sqrt2_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #bottom
        if y + 1 < self.mapSize:
            node2 = self.grid[y+1][x]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, single_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #bottom left
        if y + 1 < self.mapSize and x-1 >=0:
            node2 = self.grid[y+1][x-1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, sqrt2_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        #left
        if x-1>=0:
            node2 = self.grid[y][x-1]
            if not check_collision_with_obstacles(node, node2):
                node.neighbours.append((node2, single_weight))
                if node2 not in visited:
                    self.set_neighbours(node2, visited)
        if len(node.neighbours) > 0:
            self.empty_cells.append([node.y, node.x])
            node.type = EMPTY


    def draw(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.draw()
        for obstacle in self.obstacles:
            obstacle.draw()

    def coord_to_cell(self, coord:pygame.Vector2) -> Node:
        return self.grid[int(coord.y/self.cellSize)][int(coord.x/self.cellSize)]
        