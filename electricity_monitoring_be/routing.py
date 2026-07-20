"""Project-level Channels routing.

Defines websocket_urlpatterns which are used by the ASGI application.
"""
from django.urls import path

from core.consumers import EchoConsumer


websocket_urlpatterns = [
    path('ws/', EchoConsumer.as_asgi()),
]
