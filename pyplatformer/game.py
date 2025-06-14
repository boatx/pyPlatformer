import sys

import pygame
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, QUIT

from pyplatformer.character import load_image, Character
from pyplatformer.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS


class BaseGame:
    DEFAULT_BACKGROUND = "gra_bg.png"
    WINDOW_CAPTION = "The Game"

    def __init__(self):
        self.screen = None
        self.back_ground = None
        self.sprites = pygame.sprite.RenderPlain()

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        raise NotImplementedError()

    def initialize_screen(self):
        pygame.init()
        pygame.display.set_caption(self.WINDOW_CAPTION)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.back_ground, _ = load_image(self.DEFAULT_BACKGROUND)
        self.draw_empty_screen()

    def draw_empty_screen(self):
        self.screen.blit(self.back_ground, (0, 0))

    def redraw_scene(self):
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            clock.tick(TARGET_FPS)
            self.redraw_scene()


class Game(BaseGame):
    def __init__(self):
        super().__init__()
        self.hero = None

    def handle_event(self, event):

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

    def create_sprites(self):
        self.hero = Character(self.screen.get_rect())
        self.sprites.add(self.hero)

    def redraw_scene(self):
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def initialize_screen(self):
        super().initialize_screen()
        self.create_sprites()
