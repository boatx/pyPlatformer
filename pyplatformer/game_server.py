import asyncio
import logging

import pygame
from aiohttp import web, WSMsgType
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP

from pyplatformer.character import CharacterLogic

log = logging.getLogger(__name__)


class GameServer:
    AREA = (0, 0, 800, 600)
    RECT = (392, 568, 16, 32)

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.players = {}

    def create_character(self):
        return CharacterLogic(pygame.Rect(self.AREA), pygame.Rect(self.RECT))

    async def handle_message(self, character_object, message):
        action = message['action']
        key = message['key']
        log.info('input_message:{}'.format(message))
        if action == KEYDOWN:
            if key == K_LEFT:
                character_object.move(-1)
            elif key == K_RIGHT:
                character_object.move(1)
            elif key == K_UP:
                character_object.jump()
        elif action == KEYUP:
            if key in (K_LEFT, K_RIGHT):
                character_object.stop()

    async def send_handler(self):
        while True:
            objects = []
            for player in self.players.values():
                obj = player['object']
                obj.update()
                objects.append(obj.dump())

            for player in self.players.values():
                player['socket'].send_json({'objects': objects})
            await asyncio.sleep(1/60)

    async def send(self, app):
        self.loop.create_task(self.send_handler())

    async def input_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        character_object = self.create_character()
        self.players[character_object.obj_id] = {
            'socket': ws, 'object': character_object}
        log.info('created: {}'.format(character_object.obj_id))
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                log.info('{} {}'.format(character_object.obj_id, msg.json()))
                await self.handle_message(character_object, msg.json())
            elif msg.type == WSMsgType.ERROR:
                log.error('ws connection closed with exception {}'.format(
                    ws.exception()))
            await asyncio.sleep(1/60)

        self.charactes.pop(character_object.obj_id)

    def setup_routes(self, app):
        app.router.add_route('GET', '/', self.input_handler, name='input')

    def get_app(self):
        app = web.Application()
        app.on_startup.append(self.send)
        self.setup_routes(app)
        return app
