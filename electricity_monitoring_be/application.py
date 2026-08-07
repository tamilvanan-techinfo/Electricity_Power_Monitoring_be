import asyncio

from electricity_monitoring_be.asgi import application as django_application


class LifespanApplication:
    def __init__(self, app):
        self.app = app
        self.task = None

    async def __call__(self, scope, receive, send):

        if scope["type"] == "lifespan":

            while True:
                message = await receive()

                if message["type"] == "lifespan.startup":

                    print("Starting Cloud Sync...")

                    from cloud_sync.sync.websocket_client import CloudSocketClient

                    self.task = asyncio.create_task(
                        CloudSocketClient().connect()
                    )

                    await send({
                        "type": "lifespan.startup.complete"
                    })

                elif message["type"] == "lifespan.shutdown":

                    if self.task:
                        self.task.cancel()

                    await send({
                        "type": "lifespan.shutdown.complete"
                    })
                    return

        else:
            await self.app(scope, receive, send)


application = LifespanApplication(django_application)