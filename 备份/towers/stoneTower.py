import pygame
from .tower import Tower
import os
import math
from menu.menu import Menu


menu_bg = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "menu.png")).convert_alpha(), (120, 70))
upgrade_btn = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "upgrade.png")).convert_alpha(), (50, 50))


tower_imgs = []
archer_imgs = []
# load archer tower images
for x in range(7, 10):
    tower_imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/archer_towers/archer_1", str(x) + ".png")).convert_alpha(),
        (90, 90)))

# load rock image
for x in range(15, 16):
    archer_imgs.append(
        pygame.image.load(os.path.join("game_assets/stone_towers", str(x) + ".png")).convert_alpha())
    rock_img = archer_imgs[0]


class StoneTower(Tower):
    def __init__(self, x,y):
        super().__init__(x, y)
        self.tower_imgs = tower_imgs[:]
        self.archer_imgs = archer_imgs[:]
        self.archer_count = 0
        self.range = 200
        self.original_range = self.range
        self.inRange = False
        self.left = True
        self.price = [1500, 4000, "MAX"]
        self.damage = 1
        self.original_damage = self.damage
        self.attack_speed = 60  # 攻速
        self.projectiles = []  # 存储弹道
        self.width = self.height = 90
        self.moving = False
        self.name = "stone"
        self.attack_type = "physical"

        self.menu = Menu(self, self.x, self.y, menu_bg, self.price)
        self.menu.add_btn(upgrade_btn, "Upgrade")

        self.time_elapsed = 0  # 用于石头上下运动的时间变量
        self.attack_count = 0  # 攻击计数器
        self.attack_speed = 60  # 攻速（帧数，60 表示 1 秒攻击一次）

    def get_upgrade_cost(self):
        """
        gets the upgrade cost
        :return: int
        """
        return self.menu.get_item_cost()

    def draw(self, win):
        """
        draw the arhcer tower and animated archer
        :param win: surface
        :return: int
        """
        super().draw_radius(win)
        super().draw(win)

        # 使用正弦函数计算石头的上下偏移量
        self.time_elapsed += 1
        rock_offset = int(15 * math.sin(self.time_elapsed / 20))

        # 计算石头的位置
        rock_x = self.x + self.width // 2 - rock_img.get_width() // 2
        rock_y = self.y - rock_img.get_height() + rock_offset
        win.blit(rock_img, (rock_x, rock_y))

    def change_range(self, r):
        """
        change range of archer tower
        :param r: int
        :return: None
        """
        self.range = r

    def attack(self, enemies):
        """
        攻击范围内的敌人
        :param enemies: 敌人列表
        :return: int (获得的金钱)
        """
        self.attack_count += 1  # 每帧递增攻击计数器
        if self.attack_count < self.attack_speed:
            return 0  # 未达到攻速要求，不进行攻击

        # 攻击逻辑
        money = 0
        self.attack_count = 0  # 重置攻击计数器
        self.inRange = False
        enemy_closest = []

        # 检测范围内的敌人
        for enemy in enemies:
            x, y = enemy.x, enemy.y
            dis = math.sqrt((self.x - enemy.img.get_width() / 2 - x) ** 2 +
                            (self.y - enemy.img.get_height() / 2 - y) ** 2)
            if dis < self.range:
                self.inRange = True
                enemy_closest.append(enemy)

        # 按照路径位置排序，优先攻击最近的敌人
        enemy_closest.sort(key=lambda x: x.path_pos)

        # 对第一个敌人进行攻击
        if len(enemy_closest) > 0:
            first_enemy = enemy_closest[0]
            if first_enemy.hit(self.damage):
                money += first_enemy.money
                enemies.remove(first_enemy)

        return money
