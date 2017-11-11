import sys

import pygame
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, QUIT

from character import load_image, Character
from config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS


class Game:
    DEFAULT_BACKGROUND = "gra_bg.png"

    def __init__(self):
        self.hero = None
        self.screen = None
        self.back_ground = None
        self.sprites = None

    def handle_events(self, event):

        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.key == K_LEFT:
                self.hero.move(-1)
            elif event.key == K_RIGHT:
                self.hero.move(1)
            elif event.key == K_UP:
                self.hero.jump()
        elif event.type == KEYUP:
            if event.key in (K_LEFT, K_RIGHT):
                self.hero.stop()

    def initialize_screen(self):
        pygame.init()
        pygame.display.set_caption("The Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.back_ground, _ = load_image(self.DEFAULT_BACKGROUND)
        self.draw_empty_screen()

    def draw_empty_screen(self):
        self.screen.blit(self.back_ground, (0, 0))

    def create_sprites(self):
        self.hero = Character(self.screen.get_rect())
        self.sprites = pygame.sprite.RenderPlain(self.hero)

    def redraw_scene(self):
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        self.initialize_screen()
        self.create_sprites()
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                self.handle_events(event)
            clock.tick(TARGET_FPS)
            self.redraw_scene()
