import asyncio
import json
import logging

import pygame
from aiohttp import web, WSMsgType
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP

from pyplatformer.character import CharacterLogic
from pyplatformer.helpfun import load_image

log = logging.getLogger(__name__)


class GameServer:
    DEFAULT_BACKGROUND = "gra_bg.png"

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.characters = {}
        self.area = pygame.Rect([0, 0, 800, 600])
        self.rect = pygame.Rect([392, 568, 16, 32])
        self.message = None
        self.listeners = []

    async def handle_message(self, character_object, message):
        message = json.loads(message)
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
            for item in self.characters.values():
                obj = item['object']
                obj.update()
                objects.append(obj.dump())

            for item in self.characters.values():
                item['socket'].send_str(json.dumps({'objects': objects}))
            await asyncio.sleep(1/60)

    async def send(self, app):
        self.loop.create_task(self.send_handler())

    async def input_handler(self, request):
        log.info('connection from:{} '.format(request.host))
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        character_object = CharacterLogic(self.area, self.rect)
        self.characters[request.host] = {
            'socket': ws, 'object': character_object}

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await self.handle_message(character_object, msg.data)
            elif msg.type == WSMsgType.ERROR:
                log.error('ws connection closed with exception {}'.format(
                    ws.exception()))
            await asyncio.sleep(1/60)

        self.charactes.pop(request.host)

    async def output_handler(self, request):
        log.info('connection from:{} '.format(request.host))
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.listeners.append(ws)
        while True:
            ws.send_str('Test message')
            print('send test')
            await asyncio.sleep(0.1)

    def setup_routes(self, app):
        app.router.add_route('GET', '/', self.input_handler, name='input')
        app.router.add_route('GET', '/output', self.output_handler, name='output')

    def get_app(self):
        app = web.Application()
        app.on_startup.append(self.send)
        self.setup_routes(app)
        return app
