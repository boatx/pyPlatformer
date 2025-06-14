import logging

from aiohttp import web
from command_manager import Manager

from pyplatformer.game import Game
from pyplatformer.game_client import GameClient
from pyplatformer.game_server import GameServer


logging.basicConfig(level=logging.INFO)

manager = Manager()


@manager.command
def single():
    game = Game()
    game.initialize_screen()
    game.run()


@manager.option("--port", default=8888, type=int)
@manager.option("--host", default="localhost", type=str)
def client(host, port):
    client = GameClient(server_addres="http://{}:{}/".format(host, port))
    client.run()


@manager.option("--port", default=8888, type=int)
@manager.option("--host", default="localhost", type=str)
def server(host, port):
    game_server = GameServer()
    app = game_server.get_app()
    web.run_app(app, host=host, port=port, loop=game_server.loop)


if __name__ == "__main__":
    manager.run_command()
