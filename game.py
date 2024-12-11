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
from algorithm.greedy import improved_greedy_placement
from algorithm.dp import dp_placement
import pickle
import json
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
    pygame.image.load(os.path.join("game_assets/icon","button_greedy.png")).convert_alpha(), (75, 75))
dp_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_dp.png")).convert_alpha(), (75, 75))
q_train_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_qtraining.png")).convert_alpha(), (75, 75))
q_play_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_qinference.png")).convert_alpha(), (75, 75))

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
        self.tick_counter = 0
        self.ticks_per_enemy = 360
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
            if self.tick_counter % self.ticks_per_enemy == 0:  # Generate enemy based on tick count
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
        Patch to get tower prices.
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
        self.current_wave = waves[self.wave][:]
        self.tick_counter = 0
        self.pause = True
        self.moving_object = None

    def add_tower(self, name):
        """
        Prepares to place a tower. The user clicks on the map a second time to finalize placement.
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
            print(f"{name} is not a valid tower name!")

    def place_tower(self, pos):
        if self.moving_object is None:
            return

        x, y = pos
        # Check if the click is on a valid position
        valid_pos = self.is_valid_position(x, y)
        if not valid_pos:
            print("Please select a valid position to place the tower!")
            self.moving_object = None
            return

        # Check if the position overlaps with existing towers
        tower_list = self.attack_towers + self.support_towers
        for tower in tower_list:
            if tower.x == valid_pos[0] and tower.y == valid_pos[1]:
                print("This position is already occupied by another tower!")
                self.moving_object = None
                return

        # Get the cost of the tower
        cost = self.get_tower_cost(self.moving_object.name)
        if self.money < cost:
            print("Not enough money to place this tower!")
            self.moving_object = None
            return

        # Place the tower
        self.moving_object.x, self.moving_object.y = valid_pos
        if self.moving_object.name in attack_tower_names:
            self.attack_towers.append(self.moving_object)
            self.money -= cost
        elif self.moving_object.name in support_tower_names:
            self.support_towers.append(self.moving_object)
            self.money -= cost
        else:
            print("Unknown tower type!")
            self.moving_object = None
            return

        # Successfully placed the tower, clear selection state
        self.moving_object.moving = False
        self.moving_object = None
        self.selected_tower_type = None

    def update_game_state(self):
        """
        Updates the positions of enemies and towers, processes attacks, and checks for game over.
        """
        # Loop through enemies
        to_remove = []
        for enemy in self.enemys:
            enemy.move()
            if enemy.x < -15:
                to_remove.append(enemy)

        # Remove all enemies that are off the screen
        for enemy in to_remove:
            self.lives -= 1
            self.enemys.remove(enemy)

        # Loop through attack towers
        for tower in self.attack_towers:
            if tower.name in attack_tower_with_bullet:  # Only process towers with projectiles
                tower.attack(self.enemys)  # Only generates projectiles, does not handle hits and damage
                self.money += tower.update_projectiles(self.enemys)  # Update projectiles and handle hits
            else:  # Direct attack logic for non-projectile towers
                self.money += tower.attack(self.enemys)

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
            clock.tick(60)  # 60 FPS
            self.tick_counter += 1  # Increment the tick counter each frame

            if not self.pause:
                self.gen_enemies()  # Generate enemies based on ticks

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
                        # If a tower is being placed, click on the map to attempt placement
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # Check if a tower in the menu was clicked
                        side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                        if side_menu_button:
                            # Select tower type
                            self.selected_tower_type = side_menu_button
                            self.add_tower(self.selected_tower_type)
                            continue  # Prevent further click handling

                        # Check if a control button was clicked
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
                                        print("Not enough money to upgrade")

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
        Run the traditional game. Includes two additional buttons to run traditional algorithms and automatically place defense towers.
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()

        name_map = {
            "MagicTower": "buy_magic",
            "ArrowTower": "buy_archer",
            "CannonTower": "buy_stone"
        }

        while run_game:
            clock.tick(60)  # 60 FPS
            self.tick_counter += 1  # Increment a tick for every frame

            if not self.pause:
                self.gen_enemies()  # Generate enemies based on ticks

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
                        # If a tower is being placed, click on the map to attempt placement
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # Check if a menu tower was clicked
                        side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                        if side_menu_button:
                            # Select the tower type
                            self.selected_tower_type = side_menu_button
                            self.add_tower(self.selected_tower_type)
                            continue  # Prevent further click handling

                        # Check if a control button was clicked
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

                        # *** DP Function button ***
                        if self.dpButton.click(pos[0], pos[1]):
                            positions, names = dp_placement()
                            for dp_position, dp_name in zip(positions, names):
                                self.add_tower(name_map[dp_name])
                                self.place_tower(self.valid_positions[dp_position])

                        # *** GREEDY Function button ***
                        if self.greedyButton.click(pos[0], pos[1]):
                            greedy_positions, greedy_names = improved_greedy_placement()
                            for greedy_position, greedy_name in zip(greedy_positions, greedy_names):
                                self.add_tower(name_map[greedy_name])
                                self.place_tower(self.valid_positions[greedy_position])

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
                                        print("Not enough money to upgrade")

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
        self.qTrainButton = ActionButton(q_train_btn, 600, self.height - 85)
        self.qPlayButton = ActionButton(q_play_btn, 680, self.height - 85)
        self.valid_positions = [(117, 113), (544, 160), (1070, 160), (899, 564), (485, 612)]

        # Q-learning related parameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.2  # Discount factor
        self.epsilon = 1.0  # Initial exploration rate
        self.epsilon_decay = 0.999  # Decay rate for epsilon after each episode
        self.min_epsilon = 0.01  # Minimum exploration rate
        self.num_training_episodes = 2000  # Number of training episodes, adjustable as needed
        self.training_tick_speed = 100000  # Tick speed during training (higher means faster)
        self.policy_tick_speed = 60  # Tick speed during demonstration
        self.Q = {}  # Q-table: Q[(wave, discretized_money, built_positions)][action] = q_value
        self.effective_states = []  # Records effective states and actions during placement

        self.actions = self.generate_actions()  # Generate all possible actions
        self.training_done = False  # Flag indicating if training is complete
        self.policy_mode = False  # Indicates whether in demonstration mode

    def gen_enemies_q(self):
        """
        generate the next enemy or enemies to show
        :return: enemy
        """
        if self.tick_counter % self.ticks_per_enemy == 0:  # Determine whether to spawn an enemy based on the current tick
            wave_enemies = [Scorpion(), Wizard(), Club(), Sword()]
            for x in range(len(self.current_wave)):
                if self.current_wave[x] != 0:
                    self.enemys.append(wave_enemies[x])
                    self.current_wave[x] = self.current_wave[x] - 1
                    break

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
        Action Space: A total of 16 actions
        0: do nothing
        1~5: Place an archer at the corresponding valid_positions
        6~10: Place a stone tower at the corresponding valid_positions
        11~15: Place a magic tower at the corresponding valid_positions
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
        discretized_money = self.money // 200  # Discretize money into intervals of 200

        def tower_type_to_int(tower):
            if "archer" in tower.name:
                return 1
            elif "stone" in tower.name:
                return 2
            elif "magic" in tower.name:
                return 3
            else:
                return 0

        built_positions = []
        for pos in self.valid_positions:
            # Find the tower at the specified position, if it exists
            tower_found = None
            for tower in (self.attack_towers + self.support_towers):
                if (tower.x, tower.y) == pos:
                    tower_found = tower
                    break

            if tower_found:
                built_positions.append(tower_type_to_int(tower_found))
            else:
                built_positions.append(0)

        built_positions = tuple(built_positions)

        return (self.wave, discretized_money, built_positions)

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
            # do nothing
            return 0.1

        # Recording state before performing an action
        prev_state = self.get_state()

        tower_type = action[0]
        pos = action[1]

        pre_money = self.money
        pre_tower_count = len(self.attack_towers) + len(self.support_towers)

        name_map = {
            "archer": "buy_archer",
            "stone": "buy_stone",
            "magic": "buy_magic"
        }

        if tower_type not in name_map:
            # Unknown tower type, give some penalty
            return -50

        # Check if there is already a tower at that location
        if pos in self.valid_positions:
            for tower in self.attack_towers + self.support_towers:
                if (tower.x, tower.y) == pos:
                    # There is already a tower, give punishment
                    return -70

        # Add a tower (equivalent to the player clicking the button of the corresponding tower in the menu)
        self.add_tower(name_map[tower_type])
        self.place_tower(pos)

        post_money = self.money
        post_tower_count = len(self.attack_towers) + len(self.support_towers)

        if post_tower_count > pre_tower_count:
            # Successfully placed tower
            cost = pre_money - post_money
            cost_penalty = cost * 0.5

            self.effective_states.append((prev_state, action_idx))

            return -cost_penalty
        else:
            # Failed to place the tower, give some punishment
            return -70

    def compute_reward(self, old_lives, old_enemy_count, old_money, cost_penalty):
        reward = 0
        towers_nb = len(self.attack_towers) + len(self.support_towers)
        life_loss = old_lives - self.lives
        reward -= life_loss * 30

        killed = old_enemy_count - len(self.enemys)
        reward += killed * 10

        if towers_nb >= 2:
            reward -= 1.5
        elif towers_nb >= 3:
            reward -= 10
        elif towers_nb >= 4:
            reward -= 28.1
        elif towers_nb >= 5:
            reward -= 40.4

        reward += cost_penalty

        return reward

    def reset_game(self):
        super().reset_game()
        self.pause = False  # Ensure the game is not paused during training

    def run_q_learning(self):
        """
        Execute Q-learning training when the qButton is clicked:
        1. Train on the first wave of enemies only.
        2. Each episode starts from the beginning of the wave.
        3. The episode ends when the first wave is defeated or the game is lost.
        """
        self.policy_mode = False
        self.training_done = False
        clock = pygame.time.Clock()

        for episode in range(self.num_training_episodes):
            self.reset_game()
            # self.display_q_table(episode)  # Display the Q-table
            done = False
            self.tick_counter = 0

            while not done:
                clock.tick(self.training_tick_speed)
                self.tick_counter += 1  # Increment tick counter

                state = self.get_state()
                old_lives = self.lives
                old_enemy_count = len(self.enemys)
                old_money = self.money

                action_idx = self.choose_action(state)
                cost_penalty = self.take_action(action_idx)

                # Update game state
                if not self.pause:
                    self.gen_enemies_q()  # Special generation method
                    self.update_game_state()

                next_state = self.get_state()
                reward = self.compute_reward(old_lives, old_enemy_count, old_money, cost_penalty)

                old_q = self.get_q_value(state, action_idx)
                future_val = self.compute_value_from_q_values(next_state)
                new_q = old_q + self.alpha * (reward + self.gamma * future_val - old_q)
                self.set_q_value(state, action_idx, new_q)

                # Check episode termination conditions
                # Termination for the first wave: current_wave is exhausted and no enemies
                if (sum(self.current_wave) == 0 and len(self.enemys) == 0) or self.lives <= 0:
                    done = True

                    # Adjust scores of effective states when the game ends
                    if self.lives > 9:  # Perfect completion
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # Increase scores based on completion reward
                            self.set_q_value(state, action_idx, old_q + 5)
                    else:  # Game failure
                        for state, action_idx in self.effective_states:
                            old_q = self.get_q_value(state, action_idx)
                            # Decrease scores based on failure penalty
                            self.set_q_value(state, action_idx, old_q - 1000)

                    money_bonus = self.money * 0.5

                    for state, action_idx in self.effective_states:
                        old_q = self.get_q_value(state, action_idx)
                        self.set_q_value(state, action_idx, old_q + money_bonus)

                    # Clear the list of effective states, prepare for the next game
                    print(self.effective_states)
                    self.effective_states = []

                # Perform drawing during training as well
                # self.draw()
                # pygame.display.update()

            # Decay epsilon
            if self.epsilon > self.min_epsilon:
                self.epsilon *= self.epsilon_decay

        self.save_q_table()

        self.training_done = True
        self.policy_mode = True
        self.epsilon = 0.0
        # self.run_policy_demo()
        pygame.quit()

    def run_policy_demo(self):
        """
        Demonstrate the trained policy
        """
        self.load_q_table()  # Load the Q-table before the demonstration

        self.reset_game()
        run_game = True
        clock = pygame.time.Clock()

        while run_game:
            clock.tick(self.policy_tick_speed)
            self.tick_counter += 1  # Increment tick counter

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

            if self.lives <= 0 or (sum(self.current_wave) == 0 and len(self.enemys) == 0):
                run_game = False
                break

            # Use greedy strategy
            state = self.get_state()
            q_values = [(self.get_q_value(state, a_idx), a_idx) for a_idx in range(len(self.actions))]
            q_values.sort(key=lambda x: x[0], reverse=True)
            best_action_idx = q_values[0][1]
            self.take_action(best_action_idx)

            print(f"Tick: {self.tick_counter}, State: {state}, Q-Values: {q_values}, Best Action: {best_action_idx}")

            if not self.pause:
                self.gen_enemies()
                self.update_game_state()

            self.draw()
            pygame.display.update()

        # pygame.quit()
        self.reset_game()
        self.run()

    def save_q_table(self, filename="q_table.pkl"):
        """
        Save the Q-table to a file using pickle.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self.Q, f)
        print(f"Q-table has been saved to {filename}")

    def load_q_table(self, filename="q_table.pkl"):
        """
        Load the Q-table from a file using pickle.
        """
        try:
            with open(filename, 'rb') as f:
                self.Q = pickle.load(f)
            print(f"Q-table has been loaded from {filename}.")
        except FileNotFoundError:
            print(f"Q-table file {filename} not found. Please train first.")
            self.Q = {}

    def save_q_table(self, filename="q_table.json"):
        """
        Save the Q-table to a file using JSON.
        """
        # JSON does not support non-string dictionary keys, convert tuples to strings
        json_compatible_Q = {str(key): value for key, value in self.Q.items()}
        
        with open(filename, 'w') as f:
            json.dump(json_compatible_Q, f, indent=4)
        print(f"Q-table has been saved to {filename}")

    def load_q_table(self, filename="q_table.json"):
        """
        Load the Q-table from a file using JSON.
        """
        try:
            with open(filename, 'r') as f:
                json_compatible_Q = json.load(f)
            
            # Restore string keys back to tuples
            self.Q = {eval(key): value for key, value in json_compatible_Q.items()}
            print(f"Q-table has been loaded from {filename}.")
        except FileNotFoundError:
            print(f"Q-table file {filename} not found. Please train first.")
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
        If the qButton is not clicked, run the game normally.
        If the qButton is clicked, it calls run_q_learning, so run works like Game here.
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        self.tick_counter = 0  # Initialize tick counter
        print(self.actions)

        while run_game:
            clock.tick(60)
            self.tick_counter += 1  # Increment tick counter

            pos = pygame.mouse.get_pos()

            # If already in policy_mode or training mode, run no longer handles click events.
            # Here, for simplicity, the game exits after policy_mode and training mode finish.
            if self.training_done and self.policy_mode:
                # Indicates that the demonstration is over
                # No longer continue normal game logic, you can choose to exit or reset here
                run_game = False
                break

            # Run like normal Game only in non-training and non-policy mode
            if not self.training_done and not self.policy_mode:
                if not self.pause:
                    self.gen_enemies()  # Generate enemies based on ticks

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
                            # If placing a tower, click the map to attempt placement
                            self.place_tower(pygame.mouse.get_pos())
                        else:
                            # Check if a tower in the menu was clicked
                            side_menu_button = self.menu.get_clicked(pos[0], pos[1])
                            if side_menu_button:
                                # Select tower type
                                self.selected_tower_type = side_menu_button
                                self.add_tower(self.selected_tower_type)
                                continue  # Prevent subsequent click handling

                            # Check if control buttons were clicked
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

                            # Check Q-learning buttons
                            if self.qTrainButton.click(pos[0], pos[1]):
                                # Start Q-learning training in a separate thread to avoid blocking the main loop
                                import threading
                                training_thread = threading.Thread(target=self.run_q_learning)
                                training_thread.start()

                            if self.qPlayButton.click(pos[0], pos[1]):
                                # Start policy demonstration
                                # Ensure Q-table is loaded before demonstration
                                if not self.Q:
                                    self.load_q_table()
                                self.run_policy_demo()

                            # Look if an attack tower or support tower was clicked
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
                                            print("Not enough money to upgrade")

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

                # Update game state
                if not self.pause:
                    self.update_game_state()

                # Draw all elements
                self.draw()

        pygame.quit()
