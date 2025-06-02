import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer

class OnlineUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.redis = redis.Redis()

        if self.user.is_authenticated:
            await self.accept()
            self.redis.sadd("online_users", self.user.username)

            await self.channel_layer.group_add("online", self.channel_name)
            await self.channel_layer.group_send("online", {
                "type": "send_online_users"
            })
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            self.redis.srem("online_users", self.user.username)
            await self.channel_layer.group_send("online", {
                "type": "send_online_users"
            })

            await self.channel_layer.group_discard("online", self.channel_name)

    async def send_online_users(self, event=None):
        users = self.redis.smembers("online_users")
        usernames = [u.decode("utf-8") for u in users]
        await self.send(text_data=json.dumps({"online": usernames}))
