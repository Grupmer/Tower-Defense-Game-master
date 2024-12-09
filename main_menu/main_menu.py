from game import Game_dp, Game_q
import pygame
import os


start_btn_left = pygame.image.load(os.path.join("game_assets/icon", "button_left.png")).convert_alpha()
start_btn_right = pygame.image.load(os.path.join("game_assets/icon", "button_right.png")).convert_alpha()
logo = pygame.image.load(os.path.join("game_assets", "logo.png")).convert_alpha()


class MainMenu:
    def __init__(self, win):
        self.width = 1350
        self.height = 700
        self.bg = pygame.image.load(os.path.join("game_assets", "bg.png"))
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        self.win = win

        # Define the area for the left and right buttons
        self.btn_left = (
            self.width/4 - start_btn_left.get_width()/2, 350, start_btn_left.get_width(), start_btn_left.get_height()
            )
        self.btn_right = (
            3 * self.width/4 - start_btn_right.get_width()/2, 350, start_btn_right.get_width(), start_btn_right.get_height()
            )

    def run(self):
        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONUP:
                    # Get mouse position
                    x, y = pygame.mouse.get_pos()

                    # Check if the left button is clicked (traditional algorithm)
                    if self.btn_left[0] <= x <= self.btn_left[0] + self.btn_left[2]:
                        if self.btn_left[1] <= y <= self.btn_left[1] + self.btn_left[3]:
                            print("Running traditional algorithms")
                            game_dp = Game_dp(self.win)
                            game_dp.run()
                            del game_dp

                    # Check if the right button was clicked (AI algorithm)
                    elif self.btn_right[0] <= x <= self.btn_right[0] + self.btn_right[2]:
                        if self.btn_right[1] <= y <= self.btn_right[1] + self.btn_right[3]:
                            print("Running q-learning algorithms")
                            game_q = Game_q(self.win)
                            game_q.run()
                            del game_q

            self.draw()

        pygame.quit()

    def draw(self):
        self.win.blit(self.bg, (0, 0))
        self.win.blit(logo, (self.width/2 - logo.get_width()/2, 0))
        self.win.blit(start_btn_left, (self.btn_left[0], self.btn_left[1]))
        self.win.blit(start_btn_right, (self.btn_right[0], self.btn_right[1]))
        pygame.display.update()
