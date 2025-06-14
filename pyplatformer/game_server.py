import asyncio
import logging
from typing import TypedDict

import pygame
from aiohttp import WSMsgType, web
from pygame.locals import K_LEFT, K_RIGHT, K_UP, KEYDOWN, KEYUP

from pyplatformer.character import CharacterLogic

log = logging.getLogger(__name__)


class GameServerEvent(TypedDict):
    action: int
    key: int


class TrackedPlayer(TypedDict):
    object: CharacterLogic
    socket: web.WebSocketResponse


class GameServer:
    AREA = (0, 0, 800, 600)
    RECT = (392, 568, 16, 32)
    players: dict[str, TrackedPlayer]

    def __init__(self, loop: asyncio.AbstractEventLoop | None = None):
        self.loop = loop or asyncio.get_event_loop()
        self.players = {}

    def create_character(self) -> CharacterLogic:
        return CharacterLogic(pygame.Rect(self.AREA), pygame.Rect(self.RECT))

    async def handle_message(
        self,
        character: CharacterLogic,
        message: GameServerEvent,
    ) -> None:
        action = message["action"]
        key = message["key"]
        log.info("Input message: %s", message)
        if action == KEYDOWN:
            if key == K_LEFT:
                character.move(-1)
            elif key == K_RIGHT:
                character.move(1)
            elif key == K_UP:
                character.jump()
        elif action == KEYUP and key in (K_LEFT, K_RIGHT):
            character.stop()

    async def send_handler(self) -> None:
        while True:
            objects = []
            for player in self.players.values():
                obj = player["object"]
                obj.update()
                objects.append(obj.dump())

            for player in self.players.values():
                log.info("Sending to %s objects %s", player, objects)
                await player["socket"].send_json({"objects": objects})
            await asyncio.sleep(1 / 60)

    async def send(self, app: web.Application) -> None:
        self.loop.create_task(self.send_handler())

    async def input_handler(self, request: web.Request) -> web.Response:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        character = self.create_character()
        characted_id = character.obj_id
        self.players[characted_id] = {
            "socket": ws,
            "object": character,
        }
        log.info("created: %s", characted_id)
        async for msg in ws:
            log.info("message: %s", msg)
            if msg.type == WSMsgType.TEXT:
                log.info("%s %s", characted_id, msg.json())
                await self.handle_message(character, msg.json())
            elif msg.type == WSMsgType.ERROR:
                log.error("ws connection closed with exception %s", ws.exception())
            await asyncio.sleep(1 / 60)

        self.players.pop(characted_id, None)
        log.info("ws connection closed, player %s has left", characted_id)
        return web.Response(body="Closed")

    def setup_routes(self, app: web.Application) -> None:
        app.router.add_route("GET", "/", self.input_handler, name="input")

    def get_app(self) -> web.Application:
        app = web.Application()
        app.on_startup.append(self.send)
        self.setup_routes(app)
        return app
