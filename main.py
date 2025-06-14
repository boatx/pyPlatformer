import logging

import click
from aiohttp import web

from pyplatformer.game import Game
from pyplatformer.game_client import GameClient
from pyplatformer.game_server import GameServer

logging.basicConfig(level=logging.INFO)


@click.group()
def cli(): ...


@cli.command()
def single():
    game = Game()
    game.initialize_screen()
    game.run()


@cli.command()
@click.option("--port", default=8888, type=int)
@click.option("--host", default="localhost", type=str)
def client(host, port):
    client = GameClient(server_addres="http://{}:{}/".format(host, port))
    client.run()


@cli.command()
@click.option("--port", default=8888, type=int)
@click.option("--host", default="localhost", type=str)
def server(host, port):
    game_server = GameServer()
    app = game_server.get_app()
    web.run_app(app, host=host, port=port, loop=game_server.loop)


if __name__ == "__main__":
    cli()
