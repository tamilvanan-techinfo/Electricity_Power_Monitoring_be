import asyncio

from .websocket_client import CloudSocketClient


def start():

    client = CloudSocketClient()

    asyncio.run(client.connect())