import sys

import pygame
from pygame.event import Event
from pygame.locals import K_ESCAPE, K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP, QUIT

from pyplatformer.character import Character, load_image
from pyplatformer.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS


class BaseGame:
    DEFAULT_BACKGROUND = "gra_bg.png"
    WINDOW_CAPTION = "The Game"
    _screen: None | pygame.Surface
    _back_ground: None | pygame.Surface

    def __init__(self) -> None:
        self._screen = None
        self._back_ground = None
        self.sprites = pygame.sprite.RenderPlain()

    @property
    def screen(self) -> pygame.Surface:
        if not self._screen:
            raise ValueError("Screen not initialized")
        return self._screen

    @property
    def back_ground(self) -> pygame.Surface:
        if not self._back_ground:
            raise ValueError("Background not loaded")
        return self._back_ground

    def handle_events(self) -> None:
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event: Event) -> None:
        raise NotImplementedError()

    def initialize_screen(self) -> None:
        pygame.init()
        pygame.display.set_caption(self.WINDOW_CAPTION)
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._back_ground, _ = load_image(self.DEFAULT_BACKGROUND)
        self.draw_empty_screen()

    def draw_empty_screen(self) -> None:
        self.screen.blit(self.back_ground, (0, 0))

    def redraw_scene(self) -> None:
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            clock.tick(TARGET_FPS)
            self.redraw_scene()


class Game(BaseGame):
    hero: None | Character

    def __init__(self) -> None:
        super().__init__()
        self.hero = None

    def handle_event(self, event: Event) -> None:
        if not self.hero:
            raise ValueError("Player character not created")
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

    def create_sprites(self) -> None:
        self.hero = Character(self.screen.get_rect())
        self.sprites.add(self.hero)

    def redraw_scene(self) -> None:
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def initialize_screen(self) -> None:
        super().initialize_screen()
        self.create_sprites()
