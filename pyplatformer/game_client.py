import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from multiprocessing import Process, Queue
from queue import Empty
from typing import AsyncIterator, TypedDict

import pygame
from aiohttp import ClientSession, ClientWebSocketResponse
from pygame.event import Event
from pygame.locals import K_ESCAPE, KEYDOWN, KEYUP, QUIT

from pyplatformer.character import Character, CharacterDict
from pyplatformer.config.settings import TIME_STEP
from pyplatformer.game import BaseGame

log = logging.getLogger(__name__)


class ServerMessage(TypedDict):
    objects: list[CharacterDict]


class PygameEvent(TypedDict):
    action: int
    key: int


class GameClient(BaseGame):
    message_queue: Queue
    event_queue: Queue
    players: dict[str, Character]

    def __init__(self, server_addres: str):
        super().__init__()
        self.players = {}
        self.message_queue = Queue()
        self.event_queue = Queue()
        self.server_addres = server_addres

    def create_sprite(self, obj_id: str) -> Character:
        player = Character(area=self.screen.get_rect(), obj_id=obj_id)
        self.sprites.add(player)
        self.players[player.obj_id] = player
        return player

    def redraw_scene(self) -> None:
        message: ServerMessage = self.message_queue.get()
        for sprite in message.get("objects", []):
            player_id = sprite["id"]
            player = self.players.get(player_id) or self.create_sprite(player_id)
            player.load(sprite)
        super().redraw_scene()

    def handle_event(self, event: Event) -> None:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        elif event.type in (KEYDOWN, KEYUP):
            self.event_queue.put_nowait({"action": event.type, "key": event.key})

    def spawn_game_server_client(self) -> None:
        server_client = GameServerClient(
            server_addres=self.server_addres,
            message_queue=self.message_queue,
            event_queue=self.event_queue,
        )
        Process(target=server_client.run, daemon=True).start()


class GameServerClient:
    message_queue: Queue
    event_queue: Queue

    def __init__(self, server_addres: str, message_queue: Queue, event_queue: Queue):
        self.message_queue = message_queue
        self.event_queue = event_queue
        self.server_addres = server_addres

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[ClientWebSocketResponse]:
        async with (
            ClientSession() as session,
            session.ws_connect(self.server_addres) as socket,
        ):
            yield socket

    async def handle_messages(self, socket: ClientWebSocketResponse) -> None:
        while True:
            message: ServerMessage = await socket.receive_json()
            log.debug("Received message from server: %s", message)
            self.message_queue.put_nowait(message)
            await asyncio.sleep(TIME_STEP)

    async def handle_events(self, socket: ClientWebSocketResponse) -> None:
        while True:
            try:
                event: PygameEvent = self.event_queue.get_nowait()
            except Empty:
                await asyncio.sleep(TIME_STEP)
            else:
                log.debug("Received event from game: %s sending to server", event)
                await socket.send_json(event)

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        async with self.connect() as socket:
            asyncio.create_task(self.handle_events(socket))
            asyncio.create_task(self.handle_messages(socket))
            done = asyncio.Event()
            await done.wait()
