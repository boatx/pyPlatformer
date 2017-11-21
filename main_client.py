import asyncio
import logging

from multiprocessing import Process

from pyplatformer.game_client import GameClient


logging.basicConfig(level=logging.INFO)

def main():
    client = GameClient()
    client.initialize_screen()
    client.create_sprites()
    Process(target=client.image_drawer).start()
    loop = asyncio.get_event_loop()
    loop.create_task(client.run())
    loop.create_task(client.update())
    loop.run_forever()

if __name__ == "__main__":
    main()
