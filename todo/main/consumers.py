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

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TodoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add("todo_updates", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("todo_updates", self.channel_name)

    async def receive(self, text_data):
        from .models import Todo
        from .serializers import TodoSerializer

        data = json.loads(text_data)
        action = data.get("action")

        if action == "create":
            todo = Todo.objects.create(user=self.user, title=data["title"], completed=False)
            serialized = TodoSerializer(todo).data
            await self.channel_layer.group_send("todo_updates", {
                "type": "todo_created",
                "todo": serialized
            })

        elif action == "complete":
            todo = Todo.objects.get(id=data["id"], user=self.user)
            todo.completed = True
            todo.save()
            serialized = TodoSerializer(todo).data
            await self.channel_layer.group_send("todo_updates", {
                "type": "todo_updated",
                "todo": serialized
            })

        elif action == "delete":
            todo = Todo.objects.get(id=data["id"], user=self.user)
            todo.delete()
            await self.channel_layer.group_send("todo_updates", {
                "type": "todo_deleted",
                "id": data["id"]
            })

    async def todo_created(self, event):
        await self.send(text_data=json.dumps({"action": "created", "todo": event["todo"]}))

    async def todo_updated(self, event):
        await self.send(text_data=json.dumps({"action": "updated", "todo": event["todo"]}))

    async def todo_deleted(self, event):
        await self.send(text_data=json.dumps({"action": "deleted", "id": event["id"]}))
