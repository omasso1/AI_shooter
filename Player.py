from __future__ import annotations
import Map
import pygame
import globals
import math
import random
from Projectile import Projectile
from typing import List
from typing import Dict
from typing import Callable
import StateMachine
from common import *


class Player:
    radius = 10
    low_railgun_ammo = 1
    low_rocket_ammo = 2
    enough_ammo_rocket = 3
    enough_ammo_railgun = 2
    low_hp = 30
    hp_enough = 60
    distance_to_choose_rocket = 400 

    def __init__(self, map:Map.Map, position, color, celx,cely,id) -> None:
        self.map:Map.Map = map
        self.Position_in_grid:pygame.Vector2 = pygame.Vector2(position[0], position[1])
        self.Position_in_game = pygame.Vector2(
            (self.Position_in_grid[0] * self.map.cellSize) + self.map.cellSize / 2,
            (self.Position_in_grid[1] * self.map.cellSize) + self.map.cellSize / 2
        )

        self.walk_route = self.A_Star(self.map.grid[position[0]][position[1]], self.map.grid[cely][celx])
        self.walk_route.insert(0, [self.Position_in_game.x, self.Position_in_game.y])
        self.health = 100
        self.armor = 0
        self.railgun_ammo = 3
        self.rocket_ammo = 4
        self.speed = 4
        self.min_speed = 1
        self.velocity = pygame.Vector2(0,0)
        self.color = color
        self.last_points = [0,1]
        self.direction = pygame.Vector2(1, 0)
        self.eye_direction = pygame.Vector2(1,0)
        self.is_walking = False
        self.last_time_shoot = pygame.time.get_ticks()
        self.shoot_primary_cooldown = 3000
        self.shoot_secondary_cooldown = 3000
        self.FOV = globals.max_fov/2
        self.is_casting_primary = False
        self.started_casting_time = pygame.time.get_ticks()
        #for debug
        self.id  = id
        self.stateMachine:StateMachine.StateMachine = StateMachine.StateMachine(self)
        self.init_states()
        self.player_in_fov:List[Player] = []
        self.goal_reached = False
        self.target_to_shoot:Player = None

    def setTarget(self, target:Map.Node) -> None:
        self.walk_route = self.A_Star(self.map.coord_to_cell(self.Position_in_game), target)
        #self.walk_route.insert(0, [self.Position_in_game.x, self.Position_in_game.y])
        self.last_points=[0,1]
        if len(self.walk_route) == 0:
            pass
        self.goal_reached = False

    def looking_for_enemy(self, deltaTime) -> None:
        if self.goal_reached:
            new_coords = random.choice(self.map.empty_cells)
            newTarget = self.map.grid[new_coords[0]][new_coords[1]]
            self.setTarget(newTarget)
        self.move(deltaTime)
        self.eye_direction = self.direction.copy()
        #self.eye_direction.rotate_ip(30 * deltaTime)

    def setup_shooting(self) -> None:
        self.target_to_shoot = self.choose_target_to_shoot()
        if (self.Position_in_game - self.target_to_shoot.Position_in_game).length() <= self.distance_to_choose_rocket:
            self.stateMachine.change_current_state("StrafeRocket")
        else:
            self.stateMachine.change_current_state("StrafeRailgun")
   

    def strafe_rocket(self, deltaTime) -> None:
        self.shoot_rocket()
        if self.goal_reached:
            self.setTarget(self.random_cell_nearby())
        self.move(deltaTime)
        self.eye_direction = (self.target_to_shoot.Position_in_game - self.Position_in_game).normalize()
        pass

    def strafe_railgun(self, deltaTime) -> None:
        self.shoot_railgun()
        if self.goal_reached:
            self.setTarget(self.random_cell_nearby())
        self.move(deltaTime)
        self.eye_direction = (self.target_to_shoot.Position_in_game - self.Position_in_game).normalize()

    def find_hp(self) -> None:
        pass

    def run_for_hp_shoot(self, deltaTime) -> None:
        pass

    def find_ammo(self) -> None:
        pass

    def go_for_ammo(self, deltaTime) -> None:
        pass

    def go_for_hp(self, deltaTime) -> None:
        pass

    ######### transitions
    def low_hp_some_ammo_railgun(self) -> bool:
        return self.is_hp_low() and self.is_low_railgun()
    
    def low_hp_some_ammo_rocket(self) -> bool:
        return self.is_hp_low() and self.is_low_rocket()
    
    def StrafeRocket_to_StrafeRailgun(self) -> bool:
        return not self.is_low_railgun() and self.is_zero_rocket()

    def StrafeRailgun_to_StrafeRocket(self) -> bool:
        return not self.is_low_rocket() and self.is_zero_railgun()
    
    def both_ammo_zero(self) -> bool:
        return self.is_zero_railgun() and self.is_zero_rocket()
    
    def enemy_dead(self) -> bool:
        #TODO: CHANGE THAT LOGIC
        return self.is_any_player_in_fov() 
    
    def enemy_dead_low_hp(self) -> bool:
        return self.enemy_dead() and self.is_hp_low()
    
    def enemy_dead_low_ammo(self) -> bool:
        return self.enemy_dead() and (self.is_low_railgun() or self.is_low_rocket()) 
    
    def enemy_found_some_ammo(self) -> bool:
        return self.is_any_player_in_fov() and self.is_enough_railgun() and self.is_enough_rocket()
    
    def both_ammo_enough(self) -> bool:
        return self.is_enough_railgun() and self.is_enough_rocket()
    
    def hp_low_high_ammo(self) -> bool:
        return self.is_hp_low() and self.both_ammo_enough()
    
    def ammo_low_high_hp(self) -> bool:
        return (self.is_low_railgun() or self.is_low_rocket()) and self.is_hp_enough()

    def random_cell_nearby(self) -> Map.Node:
        found_empty_cell = False
        while not found_empty_cell:
            newY = int(clamp(self.Position_in_grid.y + int(random.random() * 6) - 3, 0, self.map.mapSize - 1))
            newX = int(clamp(self.Position_in_grid.x + int(random.random() * 6) - 3, 0, self.map.mapSize - 1))

            if self.map.grid[newY][newX].type == Map.EMPTY:
                return self.map.grid[newY][newX]
            
    def prepare_strafe(self) -> None:
        self.setTarget(self.random_cell_nearby())

    def init_states(self) -> None:
        self.stateMachine.add_state("LookingForEnemy", None, self.looking_for_enemy)
        self.stateMachine.add_state("SetupShooting", self.setup_shooting, None)
        self.stateMachine.add_state("StrafeRocket", self.prepare_strafe, self.strafe_rocket)
        self.stateMachine.add_state("StrafeRailgun", self.prepare_strafe, self.strafe_railgun)
        self.stateMachine.add_state("RunForHPShooting", self.find_hp, self.run_for_hp_shoot)
        self.stateMachine.add_state("RunForAmmo", self.find_ammo, self.go_for_ammo)
        self.stateMachine.add_state("RunForHP", self.find_hp, self.go_for_hp)
        self.stateMachine.add_transition(self.is_any_player_in_fov, "LookingForEnemy", "SetupShooting")
        self.stateMachine.add_transition(self.low_hp_some_ammo_railgun, "StrafeRailgun", "RunForHPShooting")
        self.stateMachine.add_transition(self.low_hp_some_ammo_rocket, "StrafeRailgun", "RunForHPShooting")
        self.stateMachine.add_transition(self.StrafeRailgun_to_StrafeRocket, "StrafeRailgun", "StrafeRocket")
        self.stateMachine.add_transition(self.StrafeRocket_to_StrafeRailgun, "StrafeRocket", "StrafeRailgun")
        self.stateMachine.add_transition(self.enemy_dead_low_hp, "RunForHPShooting", "RunForHP")
        self.stateMachine.add_transition(self.enemy_dead_low_hp, "StrafeRailgun", "RunForHP")
        self.stateMachine.add_transition(self.enemy_dead_low_hp, "StrafeRocket", "RunForHP")
        self.stateMachine.add_transition(self.enemy_dead_low_ammo, "RunForHPShooting", "RunForAmmo")
        self.stateMachine.add_transition(self.enemy_dead_low_ammo, "StrafeRailgun", "RunForAmmo")
        self.stateMachine.add_transition(self.enemy_dead_low_ammo, "StrafeRocket", "RunForAmmo")
        self.stateMachine.add_transition(self.both_ammo_zero, "StrafeRailgun", "RunForAmmo")
        self.stateMachine.add_transition(self.both_ammo_zero, "StrafeRocket", "RunForAmmo")
        self.stateMachine.add_transition(self.enemy_found_some_ammo, "RunForAmmo", "SetupShooting")
        self.stateMachine.add_transition(self.enemy_found_some_ammo, "RunForHP", "SetupShooting")
        self.stateMachine.add_transition(self.both_ammo_enough, "RunForHP", "LookingForEnemy")
        self.stateMachine.add_transition(self.both_ammo_enough, "RunForAmmo", "LookingForEnemy")
        self.stateMachine.add_transition(self.ammo_low_high_hp, "RunForHP", "RunForAmmo")
        self.stateMachine.add_transition(self.hp_low_high_ammo, "RunForAmmo", "RunForHP")
        self.stateMachine.change_current_state("LookingForEnemy")


    def draw(self) -> None:
        if self.is_casting_primary:
            pygame.draw.circle(self.map.WORLD, globals.CASTING_COLOR, self.Position_in_game, self.radius/2)
        for i in self.walk_route:
            pygame.draw.circle(self.map.WORLD, [c/2 for c in self.color], [i[0], i[1]], self.radius)


        pygame.draw.circle(self.map.WORLD, self.color, self.Position_in_game,self.radius)
        
        #FOV debug
        fov_straight = self.Position_in_game + self.eye_direction *1000
        fov_left = self.Position_in_game + self.eye_direction.rotate(-self.FOV)*1000
        fov_right = self.Position_in_game + self.eye_direction.rotate(self.FOV)*1000

        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_left.x, fov_left.y), 4)
        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_right.x, fov_right.y), 4)
        pygame.draw.line(self.map.WORLD, self.color, self.Position_in_game, (fov_straight.x, fov_straight.y), 3)


    def is_low_railgun(self) -> bool:
        return self.railgun_ammo <= self.low_railgun_ammo
    
    def is_low_rocket(self) -> bool:
        return self.rocket_ammo <= self.low_rocket_ammo
    
    def is_zero_railgun(self) -> bool:
        return self.railgun_ammo == 0
    
    def is_zero_rocket(self) -> bool:
        return self.rocket_ammo == 0
    
    def is_hp_low(self) -> bool:
        return self.health <= self.low_hp

    def is_enough_railgun(self) -> bool:
        return self.railgun_ammo >= self.enough_ammo_railgun
    
    def is_enough_rocket(self) -> bool:
        return self.rocket_ammo >= self.enough_ammo_rocket
    
    def is_hp_enough(self) -> bool:
        return self.health >= self.hp_enough

    def update(self, deltaTime) -> None:
        #self.is_any_player_in_fov()
        self.check_if_hit()
        #self.collect_supply()
        #self.move(deltaTime)
        self.stateMachine.check_state_change()
        self.stateMachine.behave(deltaTime)

    def is_any_player_in_fov(self) -> bool:
        fov_left = self.eye_direction.rotate(-self.FOV)
        fov_right = self.eye_direction.rotate(self.FOV)
        self.player_in_fov:List[Player] = []
        for player in globals.players:
            if player is not self and self.is_inside_view_cone(self.Position_in_game,fov_left, fov_right,player.Position_in_game) and not self.is_player_behind_wall(player):
                self.player_in_fov.append(player)
        return len(self.player_in_fov) > 0

    def choose_target_to_shoot(self) -> Player:
        return self.get_closer_player(self.player_in_fov)

    def is_player_behind_wall(self,player:Player):
        sighth_line = Segment(self.Position_in_game.x, self.Position_in_game.y, player.Position_in_game.x, player.Position_in_game.y) 
        for obstacle in self.map.obstacles:
            for line in obstacle.lines:
                if line.intersects(sighth_line):
                    return True
        return False


    def is_inside_view_cone(self,starting_point, fov_left, fov_right, point_to_test):
        vector_to_point = pygame.Vector2(point_to_test[0] - starting_point[0], point_to_test[1] - starting_point[1]).normalize()
        return fov_left.cross(vector_to_point) * fov_left.cross(fov_right) >= 0 and fov_right.cross(vector_to_point) * fov_right.cross(fov_left) >= 0

    def get_closer_player(self, players:List[Player]):
        closest_dist = 9999999999
        closest_player = None
        for player in players:
            dist = (player.Position_in_game - self.Position_in_game).length_squared()
            if dist < closest_dist:
                closest_dist = dist
                closest_player = player
        return closest_player


    def shoot_railgun(self) -> None:
        if not self.is_casting_primary and self.railgun_ammo > 0 :
            self.started_casting_time = pygame.time.get_ticks()
            self.is_casting_primary = True
        else:
            cast = pygame.time.get_ticks()
            if cast - self.started_casting_time > globals.PRIMARY_CAST_TIME:
                timer = pygame.time.get_ticks()
                if self.railgun_ammo > 0 and timer - self.last_time_shoot > self.shoot_primary_cooldown:
                    enemy_position = self.target_to_shoot.Position_in_game
                    direction_to_shoot = (enemy_position - self.Position_in_game).normalize()
                    angle = math.atan2(direction_to_shoot.y, direction_to_shoot.x)
                    #angle += math.radians(random.randint(-5, 5))
                    globals.projectiles.append(Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle,self, True))
                    self.railgun_ammo -= 1
                    self.is_casting_primary = False
                    self.last_time_shoot = timer
                self.started_casting_time = cast

    def shoot_rocket(self) -> None:
        timer = pygame.time.get_ticks()
        if self.rocket_ammo > 0 and timer - self.last_time_shoot > self.shoot_secondary_cooldown:
            enemy_position = self.target_to_shoot.Position_in_game
            direction_to_shoot = (enemy_position - self.Position_in_game).normalize()
            angle = math.atan2(direction_to_shoot.y, direction_to_shoot.x)
            globals.projectiles.append(
                Projectile(self.map.WORLD, self.Position_in_game.x, self.Position_in_game.y, angle,self, False))
            self.rocket_ammo -= 1
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
                    self.railgun_ammo += supply.value
                elif supply.is_secondary_ammo:
                    self.rocket_ammo += supply.value
                elif supply.is_health:
                    self.health += supply.value
                elif supply.is_armor:
                    self.armor += supply.value
                globals.supplies.remove(supply)

    def move(self,deltaTime):
        first_last_point_number = self.last_points[0]
        second_last_point_number = self.last_points[1]
        if first_last_point_number < len(self.walk_route) and second_last_point_number < len(self.walk_route):
            #point_a = pygame.Vector2(self.walk_route[self.last_points[0]][0], self.walk_route[self.last_points[0]][1])
            point_a = self.Position_in_game
            point_b = pygame.Vector2(self.walk_route[self.last_points[1]][0], self.walk_route[self.last_points[1]][1])
            if (point_b - point_a).length() > 0:
                self.direction = pygame.Vector2.normalize(point_b - point_a)
                self.velocity = self.speed * self.direction
                self.is_walking = True
            
        if self.is_walking:
            self.Position_in_game += self.velocity

        if self.last_points[1] < len(self.walk_route):
            check_margin = 4
            point_travel = self.walk_route[self.last_points[1]]
            if point_travel[0]-check_margin <= self.Position_in_game.x <= point_travel[0]+check_margin:
                if point_travel[1]-check_margin <= self.Position_in_game.y <= point_travel[1]+check_margin:
                    self.is_walking = False
                    self.last_points[0] += 1
                    self.last_points[1] += 1


        if self.last_points[0] == len(self.walk_route) - 1:
            self.goal_reached = True
            self.is_walking = False

    def A_Star(self, start:Map.Node, goal:Map.Node):
        def reconstruct_path(cameFrom:Dict[Map.Node, Map.Node], current:Map.Node):
            total_path:List[List[float]] = [[current.worldX, current.worldY]]
            while current in cameFrom:
                current = cameFrom[current]
                total_path.insert(0,[current.worldX, current.worldY])
            return total_path  
        
        def init_dict() -> Dict[Map.Node, float]:
            temp = {}
            for row in self.map.grid:
                for node in row:
                    temp[node] = 10000000000.0
            return temp
        

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
                return reconstruct_path(cameFrom, current)

            openSet.pop(0)
            for tuple in current.neighbours:
                neighbor = tuple[0]
                weight = tuple[1]
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



