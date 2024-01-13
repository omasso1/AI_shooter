import pygame


class Supply:
    def __init__(self, is_armor, is_primary_ammo, is_secondary_ammo, is_health, position:pygame.Vector2, World:pygame.Surface):
        self.is_armor = is_armor
        self.is_primary_ammo = is_primary_ammo
        self.is_secondary_ammo = is_secondary_ammo
        self.is_health = is_health
        self.position = position
        self.color = (0,0,0)
        self.value = 0
        self.radius = 6
        self.WORLD: pygame.Surface = World
        if self.is_primary_ammo:
            self.color = (0,255,255)
            self.value = 10
        elif self.is_secondary_ammo:
            self.color = (255, 0, 255)
            self.value = 10
        elif self.is_armor:
            self.color = (125,125,125)
            self.value = 50
        elif self.is_health:
            self.color = (255,70,70)
            self.value = 25

    def draw(self):
        pygame.draw.circle(self.WORLD, self.color, self.position, self.radius)