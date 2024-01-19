import pygame
import math
import globals
from typing import List
from common import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, screen, x, y,angle,shooter, is_primary,color):
        pygame.sprite.Sprite.__init__(self)
        self.shooter = shooter
        self.screen = screen
        self.position = pygame.Vector2(x, y)
        self.radius = 4
        self.speed = 35
        self.screen_width = globals.WIDTH
        self.color = color
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.is_primary_shoot = is_primary
        self.explosion = False
        self.damage = 100
        self.explosion_time = pygame.time.get_ticks()
        self.last_hit_time =  pygame.time.get_ticks()
        self.railgun_end_point = pygame.Vector2(self.position.x + self.dx*1000, self.position.y + self.dy *1000)
        self.railgun_time_last = pygame.time.get_ticks()
        self.hit_cooldown = 1000
        if not self.is_primary_shoot:
            self.color = (0, 0, 0)
            self.radius = 10
            self.speed = 20
            self.damage = 20

    def draw(self, deltaTime:float):
        self.is_wall_between()
        if not self.is_primary_shoot:
            if not self.explosion:
                self.update(deltaTime)
                pygame.draw.circle(self.screen, self.color, (self.position.x, self.position.y), self.radius)
            else:
                pygame.draw.circle(self.screen, self.color, (self.position.x, self.position.y), self.radius)
                timer = pygame.time.get_ticks()
                if timer - self.explosion_time > 2000:
                    globals.projectiles.remove(self)
        else:
            pygame.draw.line(self.screen, self.color, self.position, self.railgun_end_point, 3)
            timer = pygame.time.get_ticks()
            if timer - self.railgun_time_last > 1000:
                globals.projectiles.remove(self)

    def is_wall_between(self):
        sighth_line = Segment(self.position.x, self.position.y, self.railgun_end_point.x, self.railgun_end_point.y)
        all_intersection = []
        for obstacle in self.shooter.map.obstacles:
            for line in obstacle.lines:
                is_intersection, point = line.line_intersection(sighth_line)
                if is_intersection:
                    all_intersection.append(point)
        self.railgun_end_point = self.get_closest_intersection(all_intersection)

    def get_closest_intersection(self, all_intersection):
        if len(all_intersection) > 0:
            closest = None
            closest_dist = 99999999
            for line in all_intersection:
                temp = pygame.Vector2(line[0], line[1])
                dist = (self.position - temp).length()
                if dist < closest_dist:
                    closest_dist = dist
                    closest = temp
            return closest
        else:
            return self.railgun_end_point


    def update(self, deltaTime:float):
        if not self.is_primary_shoot:
            if self.is_out_of_border(self.screen_width,self.screen_width): # lub kiedy trafi w przeciwnika
                self.make_explosion()
                if not self.explosion:
                    globals.projectiles.remove(self)
            else:
                self.position.x += self.dx * deltaTime / 50.0
                self.position.y += self.dy * deltaTime / 50.0

    def make_explosion(self):
        self.explosion = True and not self.is_primary_shoot
        if self.explosion:
            self.color = (255, 255, 0)
            self.radius = 70
            self.explosion_time = pygame.time.get_ticks()

    def deal_damage(self):
        timer = pygame.time.get_ticks()
        if timer - self.last_hit_time > self.hit_cooldown:
            self.last_hit_time = timer
            return self.damage
        return 0

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


