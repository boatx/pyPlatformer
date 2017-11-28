import logging

from pyplatformer.game_client import GameClient


logging.basicConfig(level=logging.INFO)


def main():
    client = GameClient(server_addres='http://localhost:8000/')
    client.run()


if __name__ == "__main__":
    main()
