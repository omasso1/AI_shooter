import Map
import pygame
import globals
import math
from Projectile import Projectile
from typing import List
from typing import Dict


class Player:
    radius = 10
    def __init__(self, map:Map.Map, position, color, celx,cely) -> None:
        self.map:Map.Map = map
        self.Position_in_grid = position
        self.Position_in_game = pygame.Vector2(
            (self.Position_in_grid[1] * self.map.cellSize) + self.map.cellSize / 2,
            (self.Position_in_grid[0] * self.map.cellSize) + self.map.cellSize / 2
        )

        self.walk_route = self.A_Star(self.map.grid[position[0]][position[1]], self.map.grid[cely][celx])
        print(self.map.grid[cely][celx].type)
        self.walk_route.insert(0, [self.Position_in_game.x, self.Position_in_game.y])
        print(self.walk_route)
        self.health = 100
        self.armor = 0
        self.primary_ammo = 20
        self.secondary_ammo = 4  
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
        self.FOV = globals.max_fov/2

  

    def draw(self) -> None:
        pygame.draw.circle(self.map.WORLD, self.color, self.Position_in_game,self.radius)
        for i in self.walk_route:
            pygame.draw.circle(self.map.WORLD, (0, 0, 0), [i[0], i[1]], self.radius)

        #FOV debug
        fov_straight = self.Position_in_game + self.direction *1000
        fov_left = self.Position_in_game + self.direction.rotate(-self.FOV)*1000
        fov_right = self.Position_in_game + self.direction.rotate(self.FOV)*1000

        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_left.x, fov_left.y), 4)
        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_right.x, fov_right.y), 4)
        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_straight.x, fov_straight.y), 3)


    def update(self, deltaTime) -> None:
        self.is_any_player_in_fov()
        self.check_if_hit()
        self.collect_supply()
        self.move(deltaTime)

    def is_any_player_in_fov(self):
        fov_left = self.direction.rotate(-self.FOV)
        fov_right = self.direction.rotate(self.FOV)
        player_in_fov = []
        for player in globals.players:
            if player != self and self.is_inside_view_cone(self.Position_in_game,fov_left, fov_right,player.Position_in_game) and  not self.is_player_behind_wall(player):
                player_in_fov.append(player)

        player_to_shoot = self.get_closer_player(player_in_fov)
        if player_to_shoot is not None and not self.is_walking:
            direction = (player_to_shoot.Position_in_game - self.Position_in_game)
            angle = self.direction.angle_to(direction)
            self.direction = self.direction.rotate(angle)
            self.shoot_primary()

    def is_player_behind_wall(self,player):
        direction = (player.Position_in_game - self.Position_in_game).normalize()/2
        position = self.Position_in_game + direction
        while 0 <= position.x <= globals.WIDTH and 0 <= position.y <= globals.WIDTH:
            color = pygame.Surface.get_at(self.map.WORLD,(int(position.x), int(position.y)))
            if color == (255, 0, 0):
                return True
            position += direction

    def is_inside_view_cone(self,starting_point, fov_left, fov_right, point_to_test):
        vector_to_point = pygame.Vector2(point_to_test[0] - starting_point[0], point_to_test[1] - starting_point[1]).normalize()
        return fov_left.cross(vector_to_point) * fov_left.cross(fov_right) >= 0 and fov_right.cross(vector_to_point) * fov_right.cross(fov_left) >= 0

    def get_closer_player(self, players):
        closest_dist = 9999999
        closest_player = None
        for player in players:
            dist = (player.Position_in_game - self.Position_in_game).length()
            if dist < closest_dist:
                closest_dist = dist
                closest_player = player
        return closest_player


    def shoot_primary(self) -> None:
        timer = pygame.time.get_ticks()
        if self.primary_ammo > 0 and timer - self.last_time_shoot > self.shoot_primary_cooldown:
            angle = math.atan2(self.direction.y, self.direction.x)
            globals.projectiles.append(Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle,self, True))
            self.primary_ammo -= 1
            self.last_time_shoot = timer

    def shoot_secondary(self) -> None:
        timer = pygame.time.get_ticks()
        if self.secondary_ammo > 0 and timer - self.last_time_shoot > self.shoot_secondary_cooldown:
            angle = math.atan2(self.direction.y, self.direction.x)
            globals.projectiles.append(
                Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle,self, False))
            self.secondary_ammo -= 1
            self.last_time_shoot = timer

    def check_if_hit(self):
        for projectile in globals.projectiles:
            if self.Position_in_game.distance_to(projectile.position) <= self.radius + projectile.radius and projectile.shooter != self:
                if projectile.is_primary_shoot:
                    self.health -= 5
                else:
                    projectile.make_explosion()
                    self.health -= 30
                globals.projectiles.remove(projectile)
        if self.health <= 0:
            globals.players.remove(self)

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
            if (point_b - point_a).length() > 0:
                self.direction = pygame.Vector2.normalize(point_b - point_a)
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

    def A_Star(self, start:Map.Node, goal:Map.Node):
        def reconstruct_path(cameFrom:Dict[Map.Node, Map.Node], current:Map.Node):
            total_path:List[List[float]] = [[current.worldX, current.worldY]]
            while current in cameFrom:
                current = cameFrom[current]
                total_path.insert(0,[current.worldX, current.worldY])
            #print(total_path)
            return total_path  
        
        def init_dict() -> Dict[Map.Node, float]:
            temp = {}
            for row in self.map.grid:
                for node in row:
                    temp[node] = 10000000000.0
            return temp
        
        def printOpenSet(openSet, fScore):
            for item in openSet:
                print(item.worldX, item.worldY, fScore[item])

        h = lambda a,b:  math.sqrt((a.worldX - b.worldX) ** 2 + (a.worldY - b.worldY) ** 2)
        openSet:List[Map.Node] = [start]

        cameFrom:dict = {}
        gScore:Dict[Map.Node, float] = init_dict()
        gScore[start] = 0

        fScore:Dict[Map.Node, float] = init_dict() 
        fScore[start] = h(goal, start)
        while len(openSet) > 0:
            current = openSet[0]
            if current is goal:
                print("goal reached")
                return reconstruct_path(cameFrom, current)

            openSet.pop(0)
            for tuple in current.neighbours:
                neighbor = tuple[0]
                weight = tuple[1]
                if neighbor.type == Map.WALL:
                    print("wall")
                tentative_gScore = gScore[current] + weight
                if tentative_gScore < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentative_gScore
                    fScore[neighbor] = tentative_gScore + h(goal, neighbor)
                    if neighbor not in openSet:
                        openSet.append(neighbor)

                    #correct neighbor in place in queue
                    neighborIndex = None
                    for i, item in enumerate(openSet):
                        if item is neighbor:
                            neighborIndex = i
                    if neighborIndex is not None:
                        openSet.pop(neighborIndex)
                        openSet.insert(0, neighbor)
                        for i in range(len(openSet) - 1):
                            if fScore[openSet[i]] > fScore[openSet[i+1]]:
                                temp = openSet[i]
                                openSet[i] = openSet[i+1]
                                openSet[i+1] = temp
                    
   
        return []



