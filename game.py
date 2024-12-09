import pygame
import os
from enemies.scorpion import Scorpion
from enemies.club import Club
from enemies.wizard import Wizard
from enemies.sword import Sword
from towers.archerTower import ArcherTowerLong, ArcherTowerShort
from towers.stoneTower import StoneTower
from towers.magicTower import MagicTower
from towers.supportTower import DamageTower, RangeTower
from menu.menu import VerticalMenu, PlayPauseButton, ActionButton
import pickle
import time
import random
pygame.font.init()
pygame.init()

TIME_DISTANCE = 6

path = [(-10, 250),(100, 250), (190, 302), (200, 302), (553, 302), (607, 217), (641, 105), (717, 57), (814, 83), (852, 222), (900, 272), (973, 284), (1100, 366), (1100, 437), (1022, 513), (814, 513), (650, 580), (580, 580), (148, 580), (43, 520), (-10, 367), (-70, 367), (-100, 367)]

lives_img = pygame.image.load(os.path.join("game_assets","heart.png")).convert_alpha()
star_img = pygame.image.load(os.path.join("game_assets","star.png")).convert_alpha()
side_img = pygame.transform.scale(pygame.image.load(os.path.join("game_assets","side.png")).convert_alpha(), (120, 500))

buy_archer = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "ico_8.png")).convert_alpha(), (75, 75))
buy_archer_2 = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "buy_archer_2.png")).convert_alpha(), (75, 75))
buy_damage = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "buy_damage.png")).convert_alpha(), (75, 75))
buy_range = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "buy_range.png")).convert_alpha(), (75, 75))
buy_stone = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "ico_11.png")).convert_alpha(), (75, 75))
buy_magic = pygame.transform.scale(pygame.image.load(os.path.join("game_assets/menu", "ico_16.png")).convert_alpha(), (75, 75))

# Music, Game pause, restart button at the lower left corner
play_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))
pause_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_pause.png")).convert_alpha(), (75, 75))
sound_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_sound.png")).convert_alpha(), (75, 75))
sound_btn_off = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_sound_off.png")).convert_alpha(), (75, 75))
restart_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_restart.png")).convert_alpha(), (75, 75))

# Algorithm button at the the lower mid-left corner
greedy_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))
dp_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))
q_train_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))
q_play_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))

# backgrouund
wave_bg = pygame.transform.scale(pygame.image.load(os.path.join("game_assets","wave.png")).convert_alpha(), (225, 75))

# Grouping of towers
attack_tower_names = ["archer", "archer2", "stone", "magic"]
attack_tower_with_bullet = ["stone", "magic"]
support_tower_names = ["range", "damage"]

# load music
pygame.mixer.music.load(os.path.join("game_assets", "music2.wav"))

# waves are in form
# frequency of enemies
# (# scorpions, # wizards, # clubs, # swords)
waves = [
    [2, 2, 1, 1],
    [50, 0, 0],
    [100, 0, 0],
    [0, 20, 0],
    [0, 50, 0, 1],
    [0, 100, 0],
    [20, 100, 0],
    [50, 100, 0],
    [100, 100, 0],
    [0, 0, 50, 3],
    [20, 0, 100],
    [20, 0, 150],
    [200, 100, 200],
]


class Game:
    def __init__(self, win):
        self.width = 1350
        self.height = 700
        self.win = win
        self.enemys = []
        self.attack_towers = []
        self.support_towers = []
        self.lives = 10
        self.money = 3000
        self.bg = pygame.image.load(os.path.join("game_assets", "bg.png"))
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        self.timer = time.time()
        self.life_font = pygame.font.SysFont("comicsans", 45)
        self.selected_tower = None
        self.menu = VerticalMenu(self.width - side_img.get_width() + 70, 250, side_img)
        self.menu.add_btn(buy_archer, "buy_archer", 300)
        self.menu.add_btn(buy_archer_2, "buy_archer_2", 750)
        self.menu.add_btn(buy_stone, "buy_stone", 800)
        self.menu.add_btn(buy_magic, "buy_magic", 500)
        self.moving_object = None
        self.wave = 0
        self.current_wave = waves[self.wave][:]
        self.pause = True
        self.music_on = True
        self.playPauseButton = PlayPauseButton(play_btn, pause_btn, 10, self.height - 85)
        self.soundButton = PlayPauseButton(sound_btn, sound_btn_off, 90, self.height - 85)
        self.restartButton = ActionButton(restart_btn, 170, self.height - 85)
        self.valid_positions = [(117, 113), (544, 160), (1070, 160),  (899, 564), (485, 612)]

    def gen_enemies(self):
        """
        generate the next enemy or enemies to show
        :return: enemy
        """
        if sum(self.current_wave) == 0:
            if len(self.enemys) == 0:
                self.wave += 1
                self.current_wave = waves[self.wave]
                self.pause = True
                self.playPauseButton.paused = self.pause
        else:
            wave_enemies = [Scorpion(), Wizard(), Club(), Sword()]
            for x in range(len(self.current_wave)):
                if self.current_wave[x] != 0:
                    self.enemys.append(wave_enemies[x])
                    self.current_wave[x] = self.current_wave[x] - 1
                    break

    def point_to_line(self, tower):
        """
        returns if you can place tower based on distance from
        path
        :param tower: Tower
        :return: Bool
        """
        # find two closest points
        return True

    def get_tower_cost(self, tower_name):
        """
        补丁，用来获取塔价格
        """
        name_cost_mapping = {
            "archer": 300,
            "archer_2": 750,
            "damage": 1000,
            "range": 1000,
            "stone": 800,
            "magic": 500,
        }
        return name_cost_mapping.get(tower_name, 0)

    def is_valid_position(self, x, y, threshold=80):
        for pos in self.valid_positions:
            if abs(x - pos[0]) < threshold and abs(y - pos[1]) < threshold:
                return pos
        return None

    def reset_game(self):
        self.lives = 10
        self.money = 3000
        self.attack_towers = []
        self.support_towers = []
        self.enemys = []
        self.wave = 0
        self.pause = True
        self.moving_object = None

    def add_tower(self, name):
        """
        准备放置塔，由用户点击地图第二次来完成放置
        """
        x, y = pygame.mouse.get_pos()
        name_list = ["buy_archer", "buy_archer_2", "buy_damage", "buy_range", "buy_stone", "buy_magic"]
        object_list = [
            ArcherTowerLong(x, y),
            ArcherTowerShort(x, y),
            DamageTower(x, y),
            RangeTower(x, y),
            StoneTower(x, y),
            MagicTower(x, y)
        ]

        try:
            obj = object_list[name_list.index(name)]
            self.moving_object = obj
            obj.moving = True
        except ValueError:
            print(f"{name} 不是一个有效的塔名称！")

    def place_tower(self, pos):
        if self.moving_object is None:
            return

        x, y = pos
        # 检查是否点击在合法位置
        valid_pos = self.is_valid_position(x, y)
        if not valid_pos:
            print("请选择一个合法的位置放置塔！")
            self.moving_object = None
            return

        # 检查是否与现有塔重叠
        tower_list = self.attack_towers + self.support_towers
        for tower in tower_list:
            if tower.x == valid_pos[0] and tower.y == valid_pos[1]:
                print("该位置已被其他塔占据！")
                self.moving_object = None
                return

        # 获取塔的成本
        cost = self.get_tower_cost(self.moving_object.name)
        if self.money < cost:
            print("金钱不足，无法放置该塔！")
            self.moving_object = None
            return

        # 放置塔
        self.moving_object.x, self.moving_object.y = valid_pos
        if self.moving_object.name in attack_tower_names:
            self.attack_towers.append(self.moving_object)
            self.money -= cost
        elif self.moving_object.name in support_tower_names:
            self.support_towers.append(self.moving_object)
            self.money -= cost
        else:
            print("未知的塔类型！")
            self.moving_object = None
            return

        # 放置成功，清除选中状态
        self.moving_object.moving = False
        self.moving_object = None
        self.selected_tower_type = None

    def update_game_state(self):
        """
        更新敌人和塔的位置，处理攻击和检查游戏结束
        """
        # loop through enemies
        to_del = []
        for en in self.enemys:
            en.move()
            if en.x < -15:
                to_del.append(en)

        # delete all enemies off the screen
        for d in to_del:
            self.lives -= 1
            self.enemys.remove(d)

        # loop through attack towers
        for tw in self.attack_towers:
            if tw.name in attack_tower_with_bullet:  # 仅处理带有弹道的塔
                tw.attack(self.enemys)  # 仅生成弹道，不处理命中和伤害
                self.money += tw.update_projectiles(self.enemys)  # 更新弹道并处理命中

            else:  # 非弹道塔的直接攻击逻辑
                self.money += tw.attack(self.enemys)

        # loop through support towers
        for tw in self.support_towers:
            tw.support(self.attack_towers)

        # if you lose
        if self.lives <= 0:
            print("You Lose")
            pygame.time.delay(3000)
            pygame.quit()
            exit()

    def draw(self, update=True):
        self.win.blit(self.bg, (0, 0))

        # draw placement rings
        if self.moving_object:
            for tower in self.attack_towers:
                tower.draw_placement(self.win)

            for tower in self.support_towers:
                tower.draw_placement(self.win)

            self.moving_object.draw_placement(self.win)

        # draw attack towers
        for tw in self.attack_towers:
            tw.draw(self.win)

        # draw support towers
        for tw in self.support_towers:
            tw.draw(self.win)

        # draw enemies
        for en in self.enemys:
            en.draw(self.win)

        # redraw selected tower
        if self.selected_tower:
            self.selected_tower.draw(self.win)

        # draw moving object
        if self.moving_object:
            self.moving_object.draw(self.win)

        # draw menu
        self.menu.draw(self.win)

        # draw play pause button
        self.playPauseButton.draw(self.win)

        # draw music toggle button
        self.soundButton.draw(self.win)

        # draw restart button
        self.restartButton.draw(self.win)

        # draw lives
        text = self.life_font.render(str(self.lives), 1, (255, 255, 255))
        life = pygame.transform.scale(lives_img, (50, 50))
        start_x = self.width - life.get_width() - 10

        self.win.blit(text, (start_x - text.get_width() - 10, 5))
        self.win.blit(life, (start_x, 10))

        # draw money
        text = self.life_font.render(str(self.money), 1, (255, 255, 255))
        money = pygame.transform.scale(star_img, (50, 50))
        start_x = self.width - life.get_width() - 10

        self.win.blit(text, (start_x - text.get_width() - 10, 63))
        self.win.blit(money, (start_x, 65))

        # draw wave
        self.win.blit(wave_bg, (TIME_DISTANCE, TIME_DISTANCE))
        text = self.life_font.render("Wave #" + str(self.wave), 1, (255, 255, 255))
        self.win.blit(text, (10 + wave_bg.get_width()/2 - text.get_width()/2, 14))

        if update:
            pygame.display.update()

    def run(self):
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(60)

            if not self.pause:
                # 生成敌人
                # 0.33, 0.5
                if time.time() - self.timer >= random.uniform(TIME_DISTANCE, TIME_DISTANCE):
                    self.timer = time.time()
                    self.gen_enemies()

            pos = pygame.mouse.get_pos()

            # Handle moving towers (if any)
            if self.moving_object:
                self.moving_object.move(pos[0], pos[1])
                tower_list = self.attack_towers + self.support_towers
                collide = False
                for tower in tower_list:
                    if tower.collide(self.moving_object):
                        collide = True
                        tower.place_color = (255, 0, 0, 100)
                        self.moving_object.place_color = (255, 0, 0, 100)
                    else:
                        tower.place_color = (0, 0, 255, 100)
                        if not collide:
                            self.moving_object.place_color = (0, 0, 255, 100)

            # Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.moving_object:
                        # 如果正在放置塔，点击地图尝试放置
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # 检查是否点击了菜单中的塔
                        side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                        if side_menu_button:
                            # 选择塔类型
                            self.selected_tower_type = side_menu_button
                            self.add_tower(self.selected_tower_type)
                            continue  # 防止后续点击处理

                        # 检查是否点击了控制按钮
                        if self.playPauseButton.click(pos[0], pos[1]):
                            self.pause = not self.pause
                            self.playPauseButton.paused = self.pause

                        elif self.soundButton.click(pos[0], pos[1]):
                            self.music_on = not self.music_on
                            self.soundButton.paused = self.music_on
                            if self.music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()

                        if self.restartButton.click(pos[0], pos[1]):
                            self.reset_game()

                        # look if you clicked on attack tower or support tower
                        btn_clicked = None
                        if self.selected_tower:
                            btn_clicked = self.selected_tower.menu.get_clicked(pos[0], pos[1])
                            if btn_clicked:
                                if btn_clicked == "Upgrade":
                                    cost = self.selected_tower.get_upgrade_cost()
                                    if self.money >= cost:
                                        self.money -= cost
                                        self.selected_tower.upgrade()
                                    else:
                                        print("没有足够的金钱进行升级")

                        if not (btn_clicked):
                            for tw in self.attack_towers:
                                if tw.click(pos[0], pos[1]):
                                    tw.selected = True
                                    self.selected_tower = tw
                                else:
                                    tw.selected = False

                            # look if you clicked on support tower
                            for tw in self.support_towers:
                                if tw.click(pos[0], pos[1]):
                                    tw.selected = True
                                    self.selected_tower = tw
                                else:
                                    tw.selected = False

            # update game state
            if not self.pause:
                self.update_game_state()

            # draw all elements
            self.draw()

        pygame.quit()


from algorithm.greedy import improved_greedy_placement()
from algorithm.dp import *


class Game_dp(Game):
    def __init__(self, win):
        super().__init__(win)
        self.greedyButton = ActionButton(greedy_btn, 330, self.height - 85)
        self.dpButton = ActionButton(dp_btn, 410, self.height - 85)

    def draw(self):
        super().draw(update=False)

        self.greedyButton.draw(self.win)
        self.dpButton.draw(self.win)

        pygame.display.update()

    def run(self):
        """
        运行传统游戏。有两个额外的按钮可以运行传统算法，并自动放置防御塔。
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(60)

            if not self.pause:
                # 生成敌人
                # 0.33, 0.5
                if time.time() - self.timer >= random.uniform(TIME_DISTANCE, TIME_DISTANCE):
                    self.timer = time.time()
                    self.gen_enemies()

            pos = pygame.mouse.get_pos()

            # Handle moving towers (if any)
            if self.moving_object:
                self.moving_object.move(pos[0], pos[1])
                tower_list = self.attack_towers + self.support_towers
                collide = False
                for tower in tower_list:
                    if tower.collide(self.moving_object):
                        collide = True
                        tower.place_color = (255, 0, 0, 100)
                        self.moving_object.place_color = (255, 0, 0, 100)
                    else:
                        tower.place_color = (0, 0, 255, 100)
                        if not collide:
                            self.moving_object.place_color = (0, 0, 255, 100)

            # Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.moving_object:
                        # 如果正在放置塔，点击地图尝试放置
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # 检查是否点击了菜单中的塔
                        side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                        if side_menu_button:
                            # 选择塔类型
                            self.selected_tower_type = side_menu_button
                            self.add_tower(self.selected_tower_type)
                            continue  # 防止后续点击处理

                        # 检查是否点击了控制按钮
                        if self.playPauseButton.click(pos[0], pos[1]):
                            self.pause = not self.pause
                            self.playPauseButton.paused = self.pause

                        elif self.soundButton.click(pos[0], pos[1]):
                            self.music_on = not (self.music_on)
                            self.soundButton.paused = self.music_on
                            if self.music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()

                        if self.restartButton.click(pos[0], pos[1]):
                            self.reset_game()

                        # Function button
                        if self.dpButton.click(pos[0], pos[1]):
                            dp_positions, dp_names = improved_greedy_placement()

                        if self.greedyButton.click(pos[0], pos[1]):
                            pass

                        # look if you clicked on attack tower or support tower
                        btn_clicked = None
                        if self.selected_tower:
                            btn_clicked = self.selected_tower.menu.get_clicked(pos[0], pos[1])
                            if btn_clicked:
                                if btn_clicked == "Upgrade":
                                    cost = self.selected_tower.get_upgrade_cost()
                                    if self.money >= cost:
                                        self.money -= cost
                                        self.selected_tower.upgrade()
                                    else:
                                        print("没有足够的金钱进行升级")

                        if not (btn_clicked):
                            for tw in self.attack_towers:
                                if tw.click(pos[0], pos[1]):
                                    tw.selected = True
                                    self.selected_tower = tw
                                else:
                                    tw.selected = False

                            # look if you clicked on support tower
                            for tw in self.support_towers:
                                if tw.click(pos[0], pos[1]):
                                    tw.selected = True
                                    self.selected_tower = tw
                                else:
                                    tw.selected = False

            # update game state
            if not self.pause:
                self.update_game_state()

            # draw all elements
            self.draw()

        pygame.quit()


class Game_q(Game):
    def __init__(self, win):
        super().__init__(win)
        # 将qButton的action指定为self.run_q_learning
        self.qTrainButton = ActionButton(q_train_btn, 330, self.height - 85)
        self.qPlayButton = ActionButton(q_play_btn, 410, self.height - 85)
        self.valid_positions = [(117, 113), (544, 160), (1070, 160),  (899, 564), (485, 612)]
        self.tick_counter = 0  # 初始化tick计数器

        # Q-learning相关参数
        self.alpha = 0.1
        self.gamma = 1.0
        self.epsilon = 1.0  # 初始探索率
        self.epsilon_decay = 0.999  # 每个episode结束后降低epsilon
        self.min_epsilon = 0.01
        self.num_training_episodes = 200  # 训练的回合数，可根据需要调整
        self.training_tick_speed = 6000  # 训练时每秒tick数（越大越快）
        self.policy_tick_speed = 60  # 展示时的tick速度
        self.Q = {}  # Q表: Q[(wave, discretized_money, built_positions)][action] = q_value
        self.effective_states = []  # 用于记录有效放置的状态和动作

        self.actions = self.generate_actions()  # 生成所有动作
        self.training_done = False  # 标记训练结束
        self.policy_mode = False  # 是否处于演示模式

    def place_tower(self, pos):
        if self.moving_object is None:
            return

        x, y = pos
        valid_pos = self.is_valid_position(x, y)
        if not valid_pos:
            self.moving_object = None
            return

        tower_list = self.attack_towers + self.support_towers
        for tower in tower_list:
            if tower.x == valid_pos[0] and tower.y == valid_pos[1]:
                self.moving_object = None
                return

        cost = self.get_tower_cost(self.moving_object.name)
        if self.money < cost:
            self.moving_object = None
            return

        self.moving_object.x, self.moving_object.y = valid_pos
        if self.moving_object.name in attack_tower_names:
            self.attack_towers.append(self.moving_object)
            self.money -= cost
        elif self.moving_object.name in support_tower_names:
            self.support_towers.append(self.moving_object)
            self.money -= cost
        else:
            self.moving_object = None
            return

        self.moving_object.moving = False
        self.moving_object = None
        self.selected_tower_type = None

    def generate_actions(self):
        """
        动作空间：共16种
        0: do nothing
        1~5: 在valid_positions对应位置放archer
        6~10: 在valid_positions对应位置放stone
        11~15: 在valid_positions对应位置放magic
        """
        actions = []
        actions.append(("none", None))  # 0
        for i, pos in enumerate(self.valid_positions):
            actions.append(("archer", pos))
        for i, pos in enumerate(self.valid_positions):
            actions.append(("stone", pos))
        for i, pos in enumerate(self.valid_positions):
            actions.append(("magic", pos))
        return actions

    def get_state(self):
        """
        将状态简化为 (wave, discretized_money, built_positions)
        - discretized_money: 金钱离散化为200一档
        - built_positions: 5个可建造位置是否已经造了塔的二元状态
        """
        discretized_money = self.money // 200  # 离散化金钱
        built_positions = tuple(
            1 if any((tower.x, tower.y) == pos for tower in self.attack_towers + self.support_towers) else 0
            for pos in self.valid_positions
        )
        return (self.wave, self.lives, discretized_money, built_positions)

    def get_q_value(self, state, action):
        return self.Q.get((state, action), 0.0)

    def set_q_value(self, state, action, value):
        self.Q[(state, action)] = value

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, len(self.actions)-1)
        else:
            q_values = [(self.get_q_value(state, a_idx), a_idx) for a_idx in range(len(self.actions))]
            q_values.sort(key=lambda x: x[0], reverse=True)
            return q_values[0][1]

    def compute_value_from_q_values(self, state):
        q_values = [self.get_q_value(state, a_idx) for a_idx in range(len(self.actions))]
        if len(q_values) == 0:
            return 0.0
        return max(q_values)

    def take_action(self, action_idx):
        action = self.actions[action_idx]
        if action[0] == "none":
            # 不做任何事
            return 0  # 不产生额外cost_penalty

        tower_type = action[0]
        pos = action[1]

        pre_money = self.money
        pre_tower_count = len(self.attack_towers) + len(self.support_towers)

        # 模拟玩家放塔的流程：
        # 1. 点击菜单按钮选择塔（add_tower）
        # 2. 点击地图放置塔（place_tower）
        # 注意：add_tower会设置self.moving_object
        name_map = {
            "archer": "buy_archer",
            "stone": "buy_stone",
            "magic": "buy_magic"
        }

        # 如果出现tower_type不在name_map中，则不支持该动作
        if tower_type not in name_map:
            # 未知塔类型，给点惩罚
            return -50

        """
        # 检查是否该位置已经有塔
        if pos in self.valid_positions:
            index = self.valid_positions.index(pos)
            if any((tower.x, tower.y) == pos for tower in self.attack_towers + self.support_towers):
                # 已经有塔，给惩罚
                return -50
        """

        # 添加塔（相当于玩家点击菜单中相应塔的按钮）
        self.add_tower(name_map[tower_type])

        # 此时self.moving_object应该是选中的塔
        # 在选定pos放置塔（相当于玩家在地图上点一下）
        self.place_tower(pos)

        post_money = self.money
        post_tower_count = len(self.attack_towers) + len(self.support_towers)

        if post_tower_count > pre_tower_count:
            # 成功放置塔
            cost = pre_money - post_money
            cost_penalty = cost * 0.1

            # 记录有效放置的状态和动作
            current_state = self.get_state()
            self.effective_states.append((current_state, action_idx))

            return -cost_penalty
        else:
            # 放塔失败（不可建造位置或没钱）
            # 给一定的固定惩罚，比如-50
            return -50

    def compute_reward(self, old_lives, old_enemy_count, old_money, cost_penalty):
        reward = 0
        # life_loss = old_lives - self.lives
        # reward -= life_loss * 300

        # killed = old_enemy_count - len(self.enemys)
        # reward += killed * 50

        if len(self.attack_towers) + len(self.support_towers) >= 5:
            reward -= 0.1

        reward += cost_penalty

        return reward

    def reset_game(self):
        super().reset_game()
        self.wave = 0
        self.current_wave = waves[self.wave][:]
        self.pause = False   # 确保训练时不暂停游戏

    def run_q_learning(self):
        """
        点击qButton后执行训练：
        1. 只训练第一波敌人。
        2. 在训练过程中每个episode都从头开始。
        3. 当第一波结束或游戏失败，episode结束。
        """
        self.policy_mode = False
        self.training_done = False
        clock = pygame.time.Clock()

        for episode in range(self.num_training_episodes):
            self.reset_game()
            self.display_q_table(episode)  # 展示Q表
            done = False
            self.tick_counter = 0  # 重置tick计数器

            while not done:
                # 处理事件以防止卡死
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                clock.tick(self.training_tick_speed)
                self.tick_counter += 1  # 增加tick计数器

                state = self.get_state()
                old_lives = self.lives
                old_enemy_count = len(self.enemys)
                old_money = self.money

                action_idx = self.choose_action(state)
                cost_penalty = self.take_action(action_idx)

                # 更新游戏状态
                if not self.pause:
                    # 敌人生成（第一波）
                    if time.time() - self.timer >= 0.06:         # 这里可能需要修改！！！现实是10
                        self.timer = time.time()
                        self.gen_enemies()
                    self.update_game_state()

                next_state = self.get_state()
                reward = self.compute_reward(old_lives, old_enemy_count, old_money, cost_penalty)

                old_q = self.get_q_value(state, action_idx)
                future_val = self.compute_value_from_q_values(next_state)
                new_q = old_q + self.alpha * (reward + self.gamma * future_val - old_q)
                self.set_q_value(state, action_idx, new_q)

                # 判断episode结束条件
                # 第一波结束条件：current_wave耗尽且no enemies
                if (sum(self.current_wave) == 0 and len(self.enemys) == 0) or self.lives <= 0:
                    done = True

                    # 游戏结束时调整有效状态的分数
                    if self.lives > 9:  # 游戏完美通关
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # 根据通关奖励增加分数（例如 +100）
                            self.set_q_value(state, action_idx, old_q + 120)
                    elif self.lives > 8:
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # 根据通关奖励增加分数
                            self.set_q_value(state, action_idx, old_q - 300)
                    elif self.lives > 6:
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # 根据通关奖励增加分数
                            self.set_q_value(state, action_idx, old_q - 500)
                    else:  # 游戏失败
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # 根据失败惩罚减少分数
                            self.set_q_value(state, action_idx, old_q - 99999)

                    # 清空有效状态列表，准备下一局
                    self.effective_states = []

                # 在训练时也进行绘制
                # self.draw()
                # pygame.display.update()

            # 衰减epsilon
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay

        self.save_q_table()

        self.training_done = True
        self.policy_mode = True
        self.epsilon = 0.0
        self.run_policy_demo()

    def run_policy_demo(self):
        """
        使用训练的策略进行一次展示
        """
        self.load_q_table()  # 在演示前加载 Q 表

        self.reset_game()
        run_game = True
        clock = pygame.time.Clock()
        self.tick_counter = 0  # 初始化tick计数器

        while run_game:
            clock.tick(self.policy_tick_speed)
            self.tick_counter += 1  # 增加tick计数器

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

            if self.lives <= 0 or (sum(self.current_wave) == 0 and len(self.enemys) == 0):
                run_game = False
                break

            # 使用贪心策略
            state = self.get_state()
            q_values = [(self.get_q_value(state, a_idx), a_idx) for a_idx in range(len(self.actions))]
            q_values.sort(key=lambda x: x[0], reverse=True)
            best_action_idx = q_values[0][1]
            self.take_action(best_action_idx)

            if not self.pause:
                # 敌人生成（第一波）
                if time.time() - self.timer >= TIME_DISTANCE:
                    self.timer = time.time()
                    self.gen_enemies()
                self.update_game_state()

            self.draw()
            pygame.display.update()

        # pygame.quit()

    def save_q_table(self, filename="q_table.pkl"):
        """
        使用 pickle 将 Q 表保存到文件。
        """
        with open(filename, 'wb') as f:
            pickle.dump(self.Q, f)
        print(f"Q 表已保存到 {filename}")

    def load_q_table(self, filename="q_table.pkl"):
        """
        使用 pickle 从文件中加载 Q 表。
        """
        try:
            with open(filename, 'rb') as f:
                self.Q = pickle.load(f)
            print(f"Q 表已从 {filename} 加载。")
        except FileNotFoundError:
            print(f"未找到 Q 表文件 {filename}。请先进行训练。")
            self.Q = {}

    def display_q_table(self, episode):
        print(f"Episode starting with state: {self.get_state()}")
        for (state, action), value in self.Q.items():
            print(f"State: {state}, Action: {action}, Q-Value: {value:.2f}")
        print("-" * 50)

        # Define a single file to save all Q-Tables
        filename = "q_table_combined.txt"
        with open(filename, 'a', encoding='utf-8') as file:  # Open in append mode
            file.write(f"Q-Table for Episode {episode + 1}\n")
            file.write("=" * 50 + "\n")
            for (state, action), value in self.Q.items():
                file.write(f"State: {state}, Action: {action}, Q-Value: {value:.2f}\n")
            file.write("-" * 50 + "\n")
        # print(f"Q-Table appended to {filename}")

    def draw(self):
        super().draw(update=False)
        self.qTrainButton.draw(self.win)
        self.qPlayButton.draw(self.win)
        pygame.display.update()

    def run(self):
        """
        如果没有点击qButton，就跟普通Game运行方式一样
        如果点击了qButton，qButton会调用run_q_learning方法，因此这里run就和Game一样即可
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        self.tick_counter = 0  # 初始化tick计数器

        while run_game:
            clock.tick(60)
            self.tick_counter += 1  # 增加tick计数器

            pos = pygame.mouse.get_pos()

            # 如果已经在policy_mode或训练模式中，run方法就不处理点击事件了。
            # 这里为了保持逻辑简单，在policy_mode和训练模式跑完后直接退出了游戏展示。
            if self.training_done and self.policy_mode:
                # 说明展示已经结束
                # 不再继续普通游戏逻辑，可以在这里选择退出或重置
                run_game = False
                break

            # 只有在非训练、非policy模式下才像普通Game那样运行
            if not self.training_done and not self.policy_mode:
                if not self.pause:
                    # 定时产生敌人
                    if time.time() - self.timer >= random.uniform(TIME_DISTANCE, TIME_DISTANCE):
                        self.timer = time.time()
                        self.gen_enemies()

                # Handle moving towers (if any)
                if self.moving_object:
                    self.moving_object.move(pos[0], pos[1])
                    tower_list = self.attack_towers + self.support_towers
                    collide = False
                    for tower in tower_list:
                        if tower.collide(self.moving_object):
                            collide = True
                            tower.place_color = (255, 0, 0, 100)
                            self.moving_object.place_color = (255, 0, 0, 100)
                        else:
                            tower.place_color = (0, 0, 255, 100)
                            if not collide:
                                self.moving_object.place_color = (0, 0, 255, 100)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_game = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.moving_object:
                            # 如果正在放置塔，点击地图尝试放置
                            self.place_tower(pygame.mouse.get_pos())
                        else:
                            # 检查是否点击了菜单中的塔
                            side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                            if side_menu_button:
                                # 选择塔类型
                                self.selected_tower_type = side_menu_button
                                self.add_tower(self.selected_tower_type)
                                continue  # 防止后续点击处理

                            # 检查是否点击了控制按钮
                            if self.playPauseButton.click(pos[0], pos[1]):
                                self.pause = not self.pause
                                self.playPauseButton.paused = self.pause

                            elif self.soundButton.click(pos[0], pos[1]):
                                self.music_on = not self.music_on
                                self.soundButton.paused = self.music_on
                                if self.music_on:
                                    pygame.mixer.music.unpause()
                                else:
                                    pygame.mixer.music.pause()

                            # 检查 Q 学习按钮
                            if self.qTrainButton.click(pos[0], pos[1]):
                                # 在单独线程中启动 Q 学习训练以防止阻塞主循环
                                import threading
                                training_thread = threading.Thread(target=self.run_q_learning)
                                training_thread.start()

                            if self.qPlayButton.click(pos[0], pos[1]):
                                # 启动策略演示
                                # 确保在演示前已加载 Q 表
                                if not self.Q:
                                    self.load_q_table()
                                self.run_policy_demo()

                            # look if you clicked on attack tower or support tower
                            btn_clicked = None
                            if self.selected_tower:
                                btn_clicked = self.selected_tower.menu.get_clicked(pos[0], pos[1])
                                if btn_clicked:
                                    if btn_clicked == "Upgrade":
                                        cost = self.selected_tower.get_upgrade_cost()
                                        if self.money >= cost:
                                            self.money -= cost
                                            self.selected_tower.upgrade()
                                        else:
                                            print("没有足够的金钱进行升级")

                            if not btn_clicked:
                                for tw in self.attack_towers:
                                    if tw.click(pos[0], pos[1]):
                                        tw.selected = True
                                        self.selected_tower = tw
                                    else:
                                        tw.selected = False

                                for tw in self.support_towers:
                                    if tw.click(pos[0], pos[1]):
                                        tw.selected = True
                                        self.selected_tower = tw
                                    else:
                                        tw.selected = False

                # update game state
                if not self.pause:
                    self.update_game_state()

                # draw all elements
                self.draw()

        pygame.quit()
