import asyncio
import logging
import sys
from multiprocessing import Queue

import pygame
from aiohttp import ClientSession
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, QUIT

from pyplatformer.character import load_image, Character, Orientation, State
from pyplatformer.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS

log = logging.getLogger(__name__)


class GameClient:
    DEFAULT_BACKGROUND = "gra_bg.png"

    def __init__(self):
        self.hero = None
        self.screen = None
        self.back_ground = None
        self.sprites = None
        self.socket = None
        self.message_queue = Queue()

    async def connect(self):
        session = ClientSession()
        self.socket = await session.ws_connect('http://localhost:8000/')
        log.info('connected')

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        elif event.type in (KEYDOWN, KEYUP):
            self.socket.send_json({'action': event.type, 'key': event.key})

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

    def redraw_scene(self, message):
        self.hero.orientation = Orientation(message['orientation'])
        self.hero.state = State(message['state'])
        self.hero.rect = pygame.Rect(message['rect'])
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    async def handle_messages(self):
        while True:
            if self.socket:
                message = await self.socket.receive_json()
                if message and message['objects']:
                    message = message['objects'][0]
                    self.message_queue.put(message)
            await asyncio.sleep(1/60)

    async def handle_events(self):
        await self.connect()
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            await asyncio.sleep(1/60)

    def image_drawer(self):
        clock = pygame.time.Clock()
        while True:
            message = self.message_queue.get()
            self.redraw_scene(message)
            clock.tick(TARGET_FPS)
