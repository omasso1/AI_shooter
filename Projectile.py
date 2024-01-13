import pygame
import math
import globals
from typing import List


class Projectile(pygame.sprite.Sprite):
    def __init__(self, screen, x, y,angle, is_primary):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.position = pygame.Vector2(x, y)
        self.radius = 4
        self.speed = 20
        self.screen_width = 806
        self.color = (125, 125, 125)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.is_primary_shoot = is_primary
        self.explosion = False
        self.explosion_time = pygame.time.get_ticks()
        if not self.is_primary_shoot:
            self.color = (0, 0, 0)
            self.radius = 10

    def draw(self, deltaTime:float):
        if not self.explosion:
            self.update(deltaTime)
            pygame.draw.circle(self.screen, self.color, (self.position.x, self.position.y), self.radius)
        else:
            pygame.draw.circle(self.screen, self.color, (self.position.x, self.position.y), self.radius)
            timer = pygame.time.get_ticks()
            if timer - self.explosion_time > 2000:
                globals.projectiles.remove(self)

    def update(self, deltaTime:float):
        if self.is_out_of_border(self.screen_width,self.screen_width) or self.explosion: # lub kiedy trafi w przeciwnika
            self.make_explosion()
            self.color = (255,255,0)
            self.radius = 70
            self.explosion_time = pygame.time.get_ticks()
        self.position.x += self.dx * deltaTime / 50.0
        self.position.y += self.dy * deltaTime / 50.0

    def make_explosion(self):
        self.explosion = True
    #def check_collide_with_obstacles(self, obstacles: List[Obstacles]):
    #    for obstacle in obstacles:
    #        if self.position.distance_to(obstacle.position) <= self.radius + obstacle.radius:
    #            return True
    #    return False

    def is_out_of_border(self, width, height):
        return (self.position.x - self.radius < 0 or
                self.position.x + self.radius > width or
                self.position.y - self.radius < 0 or
                self.position.y + self.radius > height)

    #def check_collide_with_enemy(self, enemies: List[Enemy]):
    #    for enemy in enemies:
    #        if self.position.distance_to(enemy.position) <= self.radius + enemy.radius:
    #            return True, enemies.index(enemy)
    #    return False, -1

