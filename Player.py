import Game
import Map
import math
import pygame
import random
import time

class Player:
    def __init__(self, map:Map.Map, position, color) -> None:
        self.map:Map.Map = map
        self.cellSize = map.cellSize
        self.Position_in_grid = position
        self.Position_in_game = pygame.Vector2(
            (self.Position_in_grid[1] * self.cellSize) + self.cellSize/2,
            (self.Position_in_grid[0] * self.cellSize) + self.cellSize / 2
        )

        self.walk_route = [
            [self.Position_in_game.x,self.Position_in_game.y],[150,100],[300,500],[700,300],[200,500]
        ]
        self.radius = 10
        self.speed = 4
        self.min_speed = 1
        self.velocity = pygame.Vector2(0,0)
        self.color = color
        self.last_points = [0,1]
        self.direction = pygame.Vector2(0, 0)
        self.is_walking = False

    def draw(self) -> None:
        pygame.draw.circle(self.map.WORLD, self.color, self.Position_in_game,self.radius)
        for i in self.walk_route:
            pygame.draw.circle(self.map.WORLD, (0, 0, 0), [i[0], i[1]], self.radius)

    def update(self, deltaTime) -> None:
        self.move(deltaTime)
        pass

    def move(self,deltaTime):
        first_last_point_number = self.last_points[0]
        second_last_point_number = self.last_points[1]
        if first_last_point_number < len(self.walk_route) and second_last_point_number < len(self.walk_route) and not self.is_walking:
            point_a = pygame.Vector2(self.walk_route[self.last_points[0]][0], self.walk_route[self.last_points[0]][1])
            point_b = pygame.Vector2(self.walk_route[self.last_points[1]][0], self.walk_route[self.last_points[1]][1])
            self.direction = pygame.Vector2.normalize(point_b - point_a)
            #self.speed = min(self.min_speed, self.direction.length())
            self.velocity = self.speed * self.direction
            self.is_walking = True

        if self.is_walking:
            self.Position_in_game += self.velocity

        if self.last_points[1] < len(self.walk_route):
            check_margin = 2
            point_travel = self.walk_route[self.last_points[1]]
            if point_travel[0]-check_margin <= self.Position_in_game.x <= point_travel[0]+check_margin:
                if point_travel[1]-check_margin <= self.Position_in_game.y <= point_travel[1]+check_margin:
                    self.is_walking = False
                    self.last_points[0] += 1
                    self.last_points[1] += 1





