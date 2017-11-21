import logging

from aiohttp import web, WSMsgType

from pyplatformer.game_server import GameServer

logging.basicConfig(level=logging.INFO)


def main():
    game_server = GameServer()
    app = game_server.get_app()
    web.run_app(app, host='127.0.0.1', port=8000)


if __name__ == "__main__":
    main()
