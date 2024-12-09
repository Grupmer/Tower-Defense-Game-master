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
import time
import random
pygame.font.init()
pygame.init()

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
q_btn = pygame.transform.scale(
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
    [0, 0, 30],
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
        self.money = 4000
        self.bg = pygame.image.load(os.path.join("game_assets", "bg.png"))
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        self.timer = time.time()
        self.life_font = pygame.font.SysFont("comicsans", 45)
        self.selected_tower = None
        self.menu = VerticalMenu(self.width - side_img.get_width() + 70, 250, side_img)
        self.menu.add_btn(buy_archer, "buy_archer", 500)
        self.menu.add_btn(buy_archer_2, "buy_archer_2", 750)
        self.menu.add_btn(buy_stone, "buy_stone", 1000)
        self.menu.add_btn(buy_magic, "buy_magic", 500)
        self.moving_object = None
        self.wave = 0
        self.current_wave = waves[self.wave][:]
        self.pause = True
        self.music_on = True
        self.playPauseButton = PlayPauseButton(play_btn, pause_btn, 10, self.height - 85)
        self.soundButton = PlayPauseButton(sound_btn, sound_btn_off, 90, self.height - 85)
        self.restartButton = ActionButton(restart_btn, 170, self.height - 85)
        self.valid_positions = [(117, 113), (544, 160), (485, 612), (899, 564), (1070, 160)]

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
            "archer": 500,
            "archer_2": 750,
            "damage": 1000,
            "range": 1000,
            "stone": 1000,
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
        self.money = 4000
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
        self.win.blit(wave_bg, (10, 10))
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
                if time.time() - self.timer >= random.uniform(6, 6):
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
                if time.time() - self.timer >= random.uniform(6, 6):
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
        self.qButton = ActionButton(greedy_btn, 330, self.height - 85)
        self.valid_positions = [(117, 113), (544, 160), (485, 612), (899, 564), (1070, 160)]

        # Q-learning相关参数
        self.alpha = 0.1
        self.gamma = 1.0
        self.epsilon = 1.0  # 初始探索率
        self.epsilon_decay = 0.999  # 每个episode结束后降低epsilon
        self.min_epsilon = 0.01
        self.num_training_episodes = 200  # 训练的回合数，可根据需要调整
        self.training_tick_speed = 1000  # 训练时每秒tick数（越大越快）
        self.policy_tick_speed = 60  # 展示时的tick速度
        self.Q = {}  # Q表: Q[(wave, lives, money)][action] = q_value

        self.actions = self.generate_actions()  # 生成所有动作
        self.training_done = False  # 标记训练结束
        self.policy_mode = False  # 是否处于演示模式

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
        将状态简单化为 (wave, lives, money)
        你可以根据需要扩展状态信息
        """
        return (self.wave, self.lives, self.money)

    def get_q_value(self, state, action):
        return self.Q.get((state, action), 0.0)

    def set_q_value(self, state, action, value):
        self.Q[(state, action)] = value

    def choose_action(self, state):
        """
        epsilon-greedy策略选择动作
        """
        import random
        if random.random() < self.epsilon:
            # 探索
            action_idx = random.randint(0, len(self.actions)-1)
        else:
            # 利用: 选择Q值最大的action
            q_values = [(self.get_q_value(state, a_idx), a_idx) for a_idx in range(len(self.actions))]
            q_values.sort(key=lambda x: x[0], reverse=True)
            action_idx = q_values[0][1]
        return action_idx

    def compute_value_from_q_values(self, state):
        """
        给定状态，从所有action中返回最大的Q值
        """
        q_values = [self.get_q_value(state, a_idx) for a_idx in range(len(self.actions))]
        if len(q_values) == 0:
            return 0.0
        return max(q_values)

    def take_action(self, action_idx):
        """
        执行动作:
        action = (tower_type, position)
        如果action是none，就不放塔
        否则尝试放塔，并根据结果（花费）给与奖励
        """
        action = self.actions[action_idx]
        if action[0] == "none":
            # 不做任何事情
            cost = 0
        else:
            tower_type = action[0]
            pos = action[1]
            # 根据tower_type获取cost
            cost = self.get_tower_cost(tower_type)
            if self.money >= cost:
                # 检查位置是否可以放置塔
                # 如果该位置已经有塔就等于无效动作，但这里依然扣费（或者不执行放塔）
                # 为简单起见，如果有塔就不放并不扣费
                tower_list = self.attack_towers + self.support_towers
                occupied = any(t.x == pos[0] and t.y == pos[1] for t in tower_list)
                if not occupied:
                    # 放置塔
                    if tower_type in attack_tower_names:
                        # 创建相应塔
                        if tower_type == "archer":
                            new_tower = ArcherTowerLong(*pos)
                        elif tower_type == "stone":
                            new_tower = StoneTower(*pos)
                        elif tower_type == "magic":
                            new_tower = MagicTower(*pos)
                        self.attack_towers.append(new_tower)
                        self.money -= cost
                    # support towers不允许放置，故不处理
                else:
                    # 已被占据，不放塔，不花钱
                    cost = 0
            else:
                # 没钱，不放塔
                cost = 0
        # cost越大，惩罚越大
        cost_penalty = cost * 0.1  # 每花1块钱扣0.1分
        return -cost_penalty

    def compute_reward(self, old_lives, old_enemy_count, old_money, cost_penalty):
        """
        根据本轮状态变化计算奖励
        - 生命减少: 每减少1点生命 -10分
        - 击杀怪物: 如果敌人减少了，就给予奖励，每杀1怪 +50分
        - 花费cost已经在take_action返回的cost_penalty中计算
        - 每tick生存 +1分 (可选)
        - 如果游戏失败(生命<=0)则 -1000分
        """
        reward = 0
        # 生命损失
        life_loss = old_lives - self.lives
        reward -= life_loss * 10
        # 击杀怪物
        # old_enemy_count - len(self.enemys) = 杀死怪物的数量
        killed = old_enemy_count - len(self.enemys)
        reward += killed * 50
        # 花钱惩罚
        reward += -cost_penalty
        # 存活奖励
        reward += 1
        if self.lives <= 0:
            reward -= 1000
        return reward

    def reset_game(self):
        super().reset_game()

    def run_q_learning(self):
        """
        当点击qButton后执行的Q-learning流程：
        1. 进入训练模式，加快tick（不画图或减少频率）
        2. 训练若干回合，直到Q表收敛或达到特定回合数
        3. 训练结束后，恢复正常tick，用贪心策略展示一次游戏
        """
        # 进入训练模式
        self.policy_mode = False
        self.training_done = False

        # 训练
        for episode in range(self.num_training_episodes):
            self.reset_game()
            # 扩展：可以在这里随机化初始条件，比如wave，money等
            done = False
            while not done:
                state = self.get_state()
                old_lives = self.lives
                old_enemy_count = len(self.enemys)
                old_money = self.money

                action_idx = self.choose_action(state)
                cost_penalty = self.take_action(action_idx)

                # 快进游戏：更新游戏状态
                # 加快tick，不绘制
                # 这里相当于执行一帧更新
                if not self.pause:
                    self.update_game_state()

                next_state = self.get_state()
                reward = self.compute_reward(old_lives, old_enemy_count, old_money, cost_penalty)

                # 更新Q值
                old_q = self.get_q_value(state, action_idx)
                future_val = self.compute_value_from_q_values(next_state)
                new_q = old_q + self.alpha * (reward + self.gamma * future_val - old_q)
                self.set_q_value(state, action_idx, new_q)

                if self.lives <= 0:
                    # 游戏失败或回合结束
                    done = True

            # 衰减epsilon
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay

        # 训练结束
        self.training_done = True

        # 开始policy展示模式
        self.policy_mode = True
        self.epsilon = 0.0  # 演示时仅使用贪心策略
        self.run_policy_demo()

    def run_policy_demo(self):
        """
        使用训练得到的Q表，以贪心策略在正常速度下演示一次游戏
        """
        self.reset_game()
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(self.policy_tick_speed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

            if self.lives <= 0:
                # 游戏结束
                run_game = False
                break

            # 正常游戏进程
            # 根据Q表贪心选择动作
            state = self.get_state()
            # 选择Q值最高的动作
            q_values = [(self.get_q_value(state, a_idx), a_idx) for a_idx in range(len(self.actions))]
            q_values.sort(key=lambda x: x[0], reverse=True)
            best_action_idx = q_values[0][1]
            self.take_action(best_action_idx)

            if not self.pause:
                self.update_game_state()

            self.draw()

        pygame.quit()

    def draw(self):
        super().draw(update=False)
        self.qButton.draw(self.win)
        pygame.display.update()

    def run(self):
        """
        如果没有点击qButton，就跟普通Game运行方式一样
        如果点击了qButton，qButton会调用run_q_learning方法，因此这里run就和Game一样即可
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(60)

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
                    if time.time() - self.timer >= random.uniform(6, 6):
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

                            # 检查qButton
                            # qButton 的逻辑是在初始化时已经将其action绑定为self.run_q_learning
                            # 如果点击到了qButton，将自动调用self.run_q_learning
                            if self.qButton.click(pos[0], pos[1]):
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
