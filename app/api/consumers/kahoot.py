import uuid
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.consumers.kahoot_state import get_or_create_room, save_room, delete_room_if_empty
from api.consumers.kahoot_broadcast import broadcast_directory

class KahootConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"].upper()
        self.group_name = f"kahoot_{self.room_code}"

        self.player_id = uuid.uuid4().hex
        self.player_name = None

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        room = get_or_create_room(self.room_code)
        await self.send_json({"event": "lobby_state", "payload": room})

        # keep directory fresh so the lobby appears immediately
        await broadcast_directory(self.channel_layer)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # they never actually joined, so nothing to clean up
        if not self.player_name:
            return

        room = get_or_create_room(self.room_code)

        remaining = []
        for p in room["players"]:
            if p.get("id") != self.player_id:
                remaining.append(p)
        room["players"] = remaining
        save_room(self.room_code, room)

        # if lobby is empty, delete it and refresh directory
        if delete_room_if_empty(self.room_code):
            await broadcast_directory(self.channel_layer)
            return

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "group_event", "event": "lobby_update", "payload": room},
        )
        await broadcast_directory(self.channel_layer)

    async def receive_json(self, content, **kwargs):
        event = content.get("event")
        payload = content.get("payload") or {}

        if event == "join":
            await self.handle_join(payload)
            return

        if event == "start":
            await self.handle_start()
            return

        if event == "leave":
            await self.close()
            return

        await self.send_json({"event": "error", "payload": {"message": f"unknown event: {event}"}})

    async def handle_join(self, payload):
        name = (payload.get("name") or "").strip()
        if not name:
            await self.send_json({"event": "error", "payload": {"message": "name required"}})
            return

        # prevent re-join spam
        if self.player_name:
            return

        room = get_or_create_room(self.room_code)

        if room.get("started"):
            await self.send_json({"event": "error", "payload": {"message": "game already started"}})
            return

        for p in room["players"]:
            if (p.get("name") or "").lower() == name.lower():
                await self.send_json({"event": "error", "payload": {"message": "name taken"}})
                return

        self.player_name = name
        room["players"].append({"id": self.player_id, "name": name})
        save_room(self.room_code, room)

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "group_event", "event": "lobby_update", "payload": room},
        )
        await broadcast_directory(self.channel_layer)

    async def handle_start(self):
        room = get_or_create_room(self.room_code)
        room["started"] = True
        save_room(self.room_code, room)

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "group_event", "event": "game_started", "payload": {"room": self.room_code}},
        )
        await broadcast_directory(self.channel_layer)

    async def group_event(self, message):
        await self.send_json({"event": message["event"], "payload": message.get("payload", {})})

