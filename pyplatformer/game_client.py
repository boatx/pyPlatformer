import asyncio
import logging
import sys
from multiprocessing import Process, Queue
from queue import Empty

import pygame
from aiohttp import ClientSession
from pygame.locals import K_ESCAPE, KEYDOWN, KEYUP, QUIT

from pyplatformer.character import Character, Orientation, State
from pyplatformer.config.settings import TIME_STEP
from pyplatformer.game import BaseGame

log = logging.getLogger(__name__)


class PygameClient(BaseGame):
    def __init__(self, message_queue, event_queue):
        super().__init__()
        self.players = {}
        self.message_queue = message_queue
        self.event_queue = event_queue

    def create_sprite(self, obj_id):
        player = Character(area=self.screen.get_rect(), obj_id=obj_id)
        self.sprites.add(player)
        self.players[player.obj_id] = player
        return player

    def redraw_scene(self):
        message = self.message_queue.get()
        for sprite in message.get("objects", []):
            player_id = sprite["id"]
            player = self.players.get(player_id) or self.create_sprite(player_id)
            player.orientation = Orientation(sprite["orientation"])
            player.state = State(sprite["state"])
            player.rect = pygame.Rect(sprite["rect"])
        super().redraw_scene()

    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        elif event.type in (KEYDOWN, KEYUP):
            self.event_queue.put_nowait({"action": event.type, "key": event.key})


class GameClient:
    def __init__(self, server_addres):
        self.socket = None
        self.message_queue = Queue()
        self.event_queue = Queue()
        self.server_addres = server_addres

    async def connect(self):
        session = ClientSession()
        self.socket = await session.ws_connect(self.server_addres)
        log.info("connected")

    async def handle_messages(self):
        while True:
            message = await self.socket.receive_json()
            log.info("Received message from server: %s", message)
            self.message_queue.put_nowait(message)
            await asyncio.sleep(TIME_STEP)

    async def handle_events(self):
        while True:
            try:
                event = self.event_queue.get_nowait()
                log.info("Received event from game: %s sending to server", event)
                await self.socket.send_json(event)
            except Empty:
                await asyncio.sleep(TIME_STEP)

    def spawn_drawer_process(self):
        def run_pygame() -> None:
            pygame_client = PygameClient(self.message_queue, self.event_queue)
            pygame_client.initialize_screen()
            pygame_client.run()

        Process(target=run_pygame).start()

    def run(self, loop=None):
        self.spawn_drawer_process()
        loop = loop or asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.create_task(self.handle_events())
        loop.create_task(self.handle_messages())
        loop.run_forever()
