import pygame
from .tower import Tower
import os
import math
from menu.menu import Menu


menu_bg = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "menu.png")).convert_alpha(), (120, 70))
upgrade_btn = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "upgrade.png")).convert_alpha(), (50, 50))


tower_imgs = []
ball_imgs = []
# load tower images
for x in range(2, 5):
    tower_imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/magic_towers", str(x) + ".png")).convert_alpha(),
        (90, 80)))

# load top image
for x in range(1, 2):
    ball_imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/magic_towers", str(x) + ".png")).convert_alpha(),
        (17.5, 28.2)))
ball_img = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/magic_towers", "50" + ".png")).convert_alpha(), (17, 17))


class MagicTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tower_imgs = tower_imgs[:]
        self.ball_imgs = ball_imgs[:]
        # self.archer_count = 0
        self.range = 220
        self.original_range = self.range
        self.inRange = False
        self.left = True
        self.price = [1500, 4000, "MAX"]
        self.damage = 45
        self.original_damage = self.damage
        self.projectiles = []  # 存储弹道
        self.width = self.height = 90
        self.moving = False
        self.name = "magic"
        self.attack_type = "magical"

        self.menu = Menu(self, self.x, self.y, menu_bg, self.price)
        self.menu.add_btn(upgrade_btn, "Upgrade")

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

        win.blit(self.ball_imgs[0], (self.x - 13, self.y - 50))

        # 绘制所有弹道
        for projectile in self.projectiles:
            projectile.draw(win)

    def change_range(self, r):
        """
        change range of archer tower
        :param r: int
        :return: None
        """
        self.range = r

    def attack(self, enemies):
        """
        攻击范围内的敌人，仅生成弹道
        :param enemies: 敌人列表
        """
        self.attack_count += 1
        if self.attack_count < self.attack_speed:
            return  # 未达到攻速要求，不生成弹道

        self.attack_count = 0  # 重置攻击计数器
        enemy_closest = []

        # 检测范围内的敌人
        for enemy in enemies:
            x, y = enemy.x, enemy.y
            dis = math.sqrt((self.x - enemy.img.get_width() / 2 - x) ** 2 +
                            (self.y - enemy.img.get_height() / 2 - y) ** 2)
            if dis < self.range:
                enemy_closest.append(enemy)

        # 优先攻击路径位置最靠前的敌人
        enemy_closest.sort(key=lambda x: x.path_pos)

        # 对第一个敌人生成弹道
        if enemy_closest:
            first_enemy = enemy_closest[0]
            new_projectile = Projectile(self.x - 13, self.y - 50, first_enemy, ball_img, self.damage)
            self.projectiles.append(new_projectile)

    def update_projectiles(self, enemies):
        """
        更新所有弹道的位置，并处理命中逻辑
        :param enemies: 敌人列表
        :return: int (通过击杀敌人获得的金钱)
        """
        money = 0
        for projectile in self.projectiles[:]:
            projectile.move()
            if projectile.hit_target:  # 如果弹道命中目标
                if projectile.target in enemies:
                    if projectile.target.hit_magic(projectile.damage):  # 使用魔法攻击
                        money += projectile.target.money  # 增加金钱奖励
                        enemies.remove(projectile.target)  # 移除敌人
                self.projectiles.remove(projectile)  # 移除已命中的弹道
        return money


class Projectile:
    def __init__(self, x, y, target, img, damage):
        """
        初始化弹道
        :param x: 弹道初始x坐标
        :param y: 弹道初始y坐标
        :param target: 目标敌人
        :param img: 弹道图像
        :param damage: 弹道伤害
        """
        self.x = x
        self.y = y
        self.target = target
        self.img = img
        self.damage = damage
        self.speed = 10  # 弹道速度
        self.hit_target = False  # 是否命中目标

    def move(self):
        """
        移动弹道，使其向目标移动
        """
        if self.target and self.target.health > 0:  # 检查目标是否有效
            # 瞄准敌人的中心点
            target_x = self.target.x
            target_y = self.target.y - self.target.img.get_height() // 2
            dir_x, dir_y = target_x - self.x, target_y - self.y
            dist = math.sqrt(dir_x ** 2 + dir_y ** 2)

            if dist > 0:
                dir_x, dir_y = dir_x / dist, dir_y / dist
                self.x += dir_x * self.speed
                self.y += dir_y * self.speed

            # 检测是否命中目标
            if dist < 10:  # 命中距离
                self.hit_target = True
        else:
            self.hit_target = True  # 如果目标无效，视为命中并移除

    def draw(self, win):
        """
        绘制弹道
        """
        win.blit(self.img, (self.x - self.img.get_width() // 2, self.y - self.img.get_height() // 2))
