import Map
import pygame
import globals
import math
from Projectile import Projectile

class Player:
    def __init__(self, map:Map.Map, position, color) -> None:
        self.map:Map.Map = map
        self.Position_in_grid = position
        self.Position_in_game = pygame.Vector2(
            (self.Position_in_grid[1] * self.map.cellSize) + self.map.cellSize/2,
            (self.Position_in_grid[0] * self.map.cellSize) + self.map.cellSize / 2
        )
        self.walk_route = [
            [self.Position_in_game.x,self.Position_in_game.y],[150,100],[300,500],[700,300],[200,500], [50,75],[600,255],[800,800]
        ]
        self.health = 100
        self.armor = 0
        self.primary_ammo = 20
        self.secondary_ammo = 4
        self.radius = 10
        self.speed = 4
        self.min_speed = 1
        self.velocity = pygame.Vector2(0,0)
        self.color = color
        self.last_points = [0,1]
        self.direction = pygame.Vector2(0, 0)
        self.is_walking = False
        self.last_time_shoot = pygame.time.get_ticks()
        self.shoot_primary_cooldown = 300
        self.shoot_secondary_cooldown = 3000

    def draw(self) -> None:
        pygame.draw.circle(self.map.WORLD, self.color, self.Position_in_game,self.radius)
        for i in self.walk_route:
            pygame.draw.circle(self.map.WORLD, (0, 0, 0), [i[0], i[1]], self.radius)

    def update(self, deltaTime) -> None:
        self.shoot_secondary()
        self.collect_supply()
        self.move(deltaTime)

    def shoot_primary(self) -> None:
        timer = pygame.time.get_ticks()
        #narazie zostawiam, ze strzelam tam gdzie idzie
        if self.primary_ammo > 0 and timer - self.last_time_shoot > self.shoot_primary_cooldown:
            angle = math.atan2(self.direction.y, self.direction.x)
            globals.projectiles.append(Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle, True))
            self.primary_ammo -= 1
            self.last_time_shoot = timer

    def shoot_secondary(self) -> None:
        timer = pygame.time.get_ticks()
        # narazie zostawiam, ze strzelam tam gdzie idzie
        if self.secondary_ammo > 0 and timer - self.last_time_shoot > self.shoot_secondary_cooldown:
            angle = math.atan2(self.direction.y, self.direction.x)
            globals.projectiles.append(
                Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle, False))
            self.secondary_ammo -= 1
            self.last_time_shoot = timer

    def check_if_hit(self):
        for projectile in globals.projectiles:
            if self.Position_in_game.distance_to(projectile.position) <= self.radius + projectile.radius:
                if projectile.is_primary_shoot:
                    self.health -= 5
                else:
                    projectile.make_explosion()
                    self.health -= 30
                globals.projectiles.remove(projectile)

    def collect_supply(self):
        for supply in globals.supplies:
            if self.Position_in_game.distance_to(supply.position) <= self.radius + supply.radius:
                if supply.is_primary_ammo:
                    self.primary_ammo += supply.value
                elif supply.is_secondary_ammo:
                    self.secondary_ammo += supply.value
                elif supply.is_health:
                    self.health += supply.value
                elif supply.is_armor:
                    self.armor += supply.value
                globals.supplies.remove(supply)

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





