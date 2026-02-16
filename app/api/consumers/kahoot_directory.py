import random
import string
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.consumers.kahoot_state import ROOMS, DIRECTORY_GROUP, rooms_summary
from api.consumers.kahoot_broadcast import broadcast_directory


def gen_code(length=4):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


class KahootDirectoryConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(DIRECTORY_GROUP, self.channel_name)
        await self.accept()
        await self.send_json({"event": "rooms", "payload": {"rooms": rooms_summary()}})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(DIRECTORY_GROUP, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event = content.get("event")
        payload = content.get("payload") or {}

        if event == "list_rooms":
            await self.send_json({"event": "rooms", "payload": {"rooms": rooms_summary()}})
            return

        if event == "create_room":
            await self.handle_create_room(payload)
            return

        await self.send_json({"event": "error", "payload": {"message": f"unknown event: {event}"}})

    async def handle_create_room(self, payload):
        name = (payload.get("name") or "").strip()
        if not name:
            await self.send_json({"event": "error", "payload": {"message": "lobby name required"}})
            return

        code = gen_code(4)
        while code in ROOMS:
            code = gen_code(4)

        ROOMS[code] = {"name": name, "players": [], "started": False}

        await self.send_json({"event": "room_created", "payload": {"code": code}})
        await broadcast_directory(self.channel_layer)

    async def directory_event(self, message):
        await self.send_json({"event": message["event"], "payload": message.get("payload", {})})

