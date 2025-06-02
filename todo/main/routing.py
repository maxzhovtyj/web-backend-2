from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # path("ws/todos/", consumers.TodoConsumer.as_asgi()),
    path("ws/online/", consumers.OnlineUserConsumer.as_asgi()),
]