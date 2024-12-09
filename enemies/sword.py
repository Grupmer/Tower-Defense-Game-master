import pygame
import os
from .enemy import Enemy

imgs = []
for x in range(20):
    add_str = str(x)
    if x < 10:
        add_str = "0" + add_str
    imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/enemies/8", "8_enemies_1_run_0" + add_str + ".png")).convert_alpha(),
        (85, 85)))


class Sword(Enemy):

    def __init__(self):
        super().__init__()
        self.name = "sword"
        self.money = 200
        self.imgs = imgs[:]
        self.max_health = 400
        self.health = self.max_health

        self.armor = 20
        self.magic_resistance = 0.2



