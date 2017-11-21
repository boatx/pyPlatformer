import sys
import json
import logging
import asyncio
from multiprocessing import Queue

import pygame
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, QUIT
from aiohttp import ClientSession, ClientConnectorError

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
        self.queue = Queue()

    async def connect(self):
        session = ClientSession()
        self.socket = await session.ws_connect('http://localhost:8000/')
        log.info('connected')

    def handle_events(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        elif event.type in (KEYDOWN, KEYUP):
            self.socket.send_str(json.dumps({'action': event.type, 'key': event.key}))

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
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    async def update(self):
        while True:
            if self.socket:
                message = await self.socket.receive_str()
                message = json.loads(message)
                if message and message['objects']:
                    message = message['objects'][0]
                    self.queue.put(message)
            await asyncio.sleep(1/60)

    async def run(self):
        #clock = pygame.time.Clock()
        result = await self.connect()
        while True:
            for event in pygame.event.get():
                self.handle_events(event)
            #clock.tick(TARGET_FPS)
            await asyncio.sleep(1/60)

    def image_drawer(self):
        clock = pygame.time.Clock()
        while True:
            message = self.queue.get()
            print(message)
            self.redraw_scene(message)
            clock.tick(TARGET_FPS)

