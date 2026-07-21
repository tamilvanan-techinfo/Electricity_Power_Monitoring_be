"""Project-level Channels routing.

Defines websocket_urlpatterns which are used by the ASGI application.
"""
from django.urls import path, re_path

from core.consumers import EchoConsumer
from screen_controller.consumers import ScreenConsumer


websocket_urlpatterns = [
    path('ws/', EchoConsumer.as_asgi()),
    re_path(r"ws/screen/(?P<role>\w+)/$", ScreenConsumer.as_asgi()),
    
]
