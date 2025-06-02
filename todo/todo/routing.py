from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import todo.main.routing as m

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(m.websocket_urlpatterns)
    ),
})