import asyncio
import logging
import sys
from multiprocessing import Queue, Process

import pygame
from aiohttp import ClientSession
from pygame.locals import KEYDOWN, KEYUP, K_ESCAPE, QUIT

from pyplatformer.game import BaseGame
from pyplatformer.character import load_image, Character, Orientation, State
from pyplatformer.config.settings import (
    SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS, TIME_STEP
)

log = logging.getLogger(__name__)


class PygameClient(BaseGame):

    def __init__(self, message_queue):
        super().__init__()
        self.players = {}
        self.message_queue = message_queue

    def create_sprite(self, obj_id):
        player = Character(area=self.screen.get_rect(), obj_id=obj_id)
        self.sprites.add(player)
        self.players[player.obj_id] = player
        return player

    def redraw_scene(self):
        message = self.message_queue.get()
        for sprite in message.get('objects', []):
            player_id = sprite['id']
            player = self.players.get(player_id) or self.create_sprite(player_id)
            player.orientation = Orientation(sprite['orientation'])
            player.state = State(sprite['state'])
            player.rect = pygame.Rect(sprite['rect'])
        super().redraw_scene()

    def handle_events(self):
        return


class GameClient:
    def __init__(self, server_addres):
        self.socket = None
        self.message_queue = Queue()
        self.server_addres = server_addres
        self.pygame_client = None

    async def connect(self):
        session = ClientSession()
        self.socket = await session.ws_connect(self.server_addres)
        log.info('connected')

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

    def spawn_drawer_process(self):
        Process(target=self.pygame_client.run).start()

    def run(self, loop=None):
        self.pygame_client = PygameClient(self.message_queue)
        self.pygame_client.initialize_screen()
        self.spawn_drawer_process()
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.create_task(self.handle_events())
        loop.create_task(self.handle_messages())
        loop.run_forever()
