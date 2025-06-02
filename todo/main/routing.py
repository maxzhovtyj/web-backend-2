from django.urls import path
from . import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/todos/$', consumers.TodoConsumer.as_asgi()),
    path("ws/online/", consumers.OnlineUserConsumer.as_asgi()),
]
