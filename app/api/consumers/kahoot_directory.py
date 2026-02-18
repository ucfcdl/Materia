import random
import string
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.core.cache import cache

from api.consumers.kahoot_state import DIRECTORY_GROUP, rooms_summary, save_room, _room_key, _get_room_codes, _save_room_codes, ROOM_TTL
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

        existing_codes = _get_room_codes()
        code = gen_code(4)
        while code in existing_codes:
            code = gen_code(4)

        room = {"name": name, "players": [], "started": False}
        save_room(code, room)
        existing_codes.add(code)
        _save_room_codes(existing_codes)

        await self.send_json({"event": "room_created", "payload": {"code": code}})
        await broadcast_directory(self.channel_layer)

    async def directory_event(self, message):
        await self.send_json({"event": message["event"], "payload": message.get("payload", {})})

