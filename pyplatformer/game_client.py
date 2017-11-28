import asyncio
import logging
import sys
from multiprocessing import Queue, Process

import pygame
from aiohttp import ClientSession
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, QUIT

from pyplatformer.character import load_image, Character, Orientation, State
from pyplatformer.config.settings import (
    SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS, TIME_STEP
)

log = logging.getLogger(__name__)


class GameClient:
    DEFAULT_BACKGROUND = 'gra_bg.png'
    CAPTION = 'Game Client'

    def __init__(self, server_addres):
        self.players = {}
        self.screen = None
        self.back_ground = None
        self.socket = None
        self.message_queue = Queue()
        self.server_addres = server_addres
        self.sprites = pygame.sprite.RenderPlain()

    async def connect(self):
        session = ClientSession()
        self.socket = await session.ws_connect(self.server_addres)
        log.info('connected')

    def initialize_screen(self):
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.back_ground, _ = load_image(self.DEFAULT_BACKGROUND)
        self.draw_empty_screen()

    def draw_empty_screen(self):
        self.screen.blit(self.back_ground, (0, 0))

    def create_sprite(self, obj_id):
        player = Character(area=self.screen.get_rect(), obj_id=obj_id)
        self.sprites.add(player)
        self.players[player.obj_id] = player
        return player

    def redraw_scene(self, message):
        for sprite in message.get('objects', []):
            player_id = sprite['id']
            player = self.players.get(player_id) or self.create_sprite(player_id)
            player.orientation = Orientation(sprite['orientation'])
            player.state = State(sprite['state'])
            player.rect = pygame.Rect(sprite['rect'])
        self.sprites.update()
        self.draw_empty_screen()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    async def handle_messages(self):
        while True:
            message = await self.socket.receive_json()
            self.message_queue.put(message)
            await asyncio.sleep(TIME_STEP)

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        elif event.type in (KEYDOWN, KEYUP):
            self.socket.send_json({'action': event.type, 'key': event.key})

    async def handle_events(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            await asyncio.sleep(TIME_STEP)

    def image_drawer(self):
        clock = pygame.time.Clock()
        while True:
            message = self.message_queue.get()
            self.redraw_scene(message)
            clock.tick(TARGET_FPS)

    def spawn_drawer_process(self):
        Process(target=self.image_drawer).start()

    def run(self, loop=None):
        self.initialize_screen()
        self.spawn_drawer_process()
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.create_task(self.handle_events())
        loop.create_task(self.handle_messages())
        loop.run_forever()
