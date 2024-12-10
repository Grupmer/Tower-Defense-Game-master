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
from menu.menu import VerticalMenu, PlayPauseButton
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

# Music and Game pause button at the lower left corner
play_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_start.png")).convert_alpha(), (75, 75))
pause_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_pause.png")).convert_alpha(), (75, 75))
sound_btn = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_sound.png")).convert_alpha(), (75, 75))
sound_btn_off = pygame.transform.scale(
    pygame.image.load(os.path.join("game_assets/icon","button_sound_off.png")).convert_alpha(), (75, 75))

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

        # loop through support towers
        for tw in self.support_towers:
            tw.support(self.attack_towers)

        # if you lose
        if self.lives <= 0:
            print("You Lose")
            pygame.time.delay(3000)
            pygame.quit()
            exit()
    def get_tower_cost(self, tower_name):
        """
        Patch to get the cost of a tower.
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
        """
        Check if a given position is valid for placing a tower.
        :param x: X-coordinate
        :param y: Y-coordinate
        :param threshold: Distance threshold for valid positions
        :return: Valid position or None if invalid
        """
        for pos in self.valid_positions:
            if abs(x - pos[0]) < threshold and abs(y - pos[1]) < threshold:
                return pos
        return None

    def add_tower(self, name):
        """
        Prepare to place a tower, completed by the user clicking on the map a second time.
        :param name: Name of the tower to be placed
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
        """
        Place the tower at the specified position.
        :param pos: Tuple (x, y) coordinates
        """
        if self.moving_object is None:
            return

        x, y = pos
        # Check if the position is valid
        valid_pos = self.is_valid_position(x, y)
        if not valid_pos:
            print("Please choose a valid position to place the tower!")
            self.moving_object = None
            return

        # Check if the position is already occupied
        tower_list = self.attack_towers + self.support_towers
        for tower in tower_list:
            if tower.x == valid_pos[0] and tower.y == valid_pos[1]:
                print("This position is already occupied by another tower!")
                self.moving_object = None
                return

        # Get the tower cost
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

        # Successfully placed, clear selected state
        self.moving_object.moving = False
        self.moving_object = None
        self.selected_tower_type = None

    def update_game_state(self):
        """
        Update the positions of enemies and towers, handle attacks, and check for game over.
        """
        # Loop through enemies
        to_del = []
        for en in self.enemys:
            en.move()
            if en.x < -15:
                to_del.append(en)

        # Delete all enemies off the screen
        for d in to_del:
            self.lives -= 1
            self.enemys.remove(d)

        # Loop through attack towers
        for tw in self.attack_towers:
            if tw.name in attack_tower_with_bullet:  # Process towers with projectiles
                tw.attack(self.enemys)  # Generate projectiles, do not handle hits
                self.money += tw.update_projectiles(self.enemys)  # Update projectiles and handle hits
            else:  # Direct attack logic for non-projectile towers
                self.money += tw.attack(self.enemys)

    def draw(self):
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

        pygame.display.update()

            # update game state
            if not self.pause:
                self.update_game_state()

            # draw all elements
            self.draw()

        pygame.quit()
    def run(self):
        """
        Run the traditional game. Two additional buttons allow traditional algorithms to run and automatically place defense towers.
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(60)

            if not self.pause:
                # Generate enemies
                # 0.33, 0.5
                if time.time() - self.timer >= random.uniform(0.5, 0.5):
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
                        # If a tower is being placed, try placing it on the map
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # Check if a tower was clicked in the menu
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
                            self.music_on = not self.music_on
                            self.soundButton.paused = self.music_on
                            if self.music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()

                        # Check if AI button was clicked (not yet implemented)
                        # if self.playPauseButton.click(pos[0], pos[1]):

                        # Check if an attack or support tower was clicked
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

                            # Check if a support tower was clicked
                            for tw in self.support_towers:
                                if tw.click(pos[0], pos[1]):
                                    tw.selected = True
                                    self.selected_tower = tw
                                else:
                                    tw.selected = False
    def run_q(self):
        """
        Run the AI algorithm, including training and a final demonstration.
        """
        pygame.mixer.music.play(loops=-1)
        run_game = True
        clock = pygame.time.Clock()
        while run_game:
            clock.tick(60)

            if not self.pause:
                # Generate enemies
                # 0.33, 0.5
                if time.time() - self.timer >= random.uniform(0.5, 0.5):
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

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_game = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.moving_object:
                        # If a tower is being placed, try placing it on the map
                        self.place_tower(pygame.mouse.get_pos())
                    else:
                        # Check if a tower was clicked in the menu
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
                            self.music_on = not self.music_on
                            self.soundButton.paused = self.music_on
                            if self.music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()

                        # Check if an AI button was clicked (not yet implemented)
                        # if self.playPauseButton.click(pos[0], pos[1]):

                        # Check if an attack or support tower was clicked
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

                            # Check if a support tower was clicked
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
