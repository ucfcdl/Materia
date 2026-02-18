import uuid
import time
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.consumers.kahoot_state import get_or_create_room, save_room, delete_room_if_empty
from api.consumers.kahoot_broadcast import broadcast_directory

class KahootConsumer(AsyncJsonWebsocketConsumer):

    def now_s(self) -> float:
        return time.time()

    async def broadcast_room(self, room, event="lobby_update") -> None:
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "group_event",
                "event": event,
                "payload": room
             },
        )

    async def broadcast_game_state(self, room) -> None:
        game = room.get("game")
        if not game:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "group_event",
             "event": "game_state",
             "payload": game
            },
        )

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
        # if host left, pick a new host based on first remaining player or none
        if room.get("hostId") == self.player_id:
            room["hostId"] = room["players"][0]["id"] if room["players"] else None

        save_room(self.room_code, room)

        # if lobby is empty, delete it and refresh directory
        if delete_room_if_empty(self.room_code):
            await broadcast_directory(self.channel_layer)
            return

        await self.broadcast_room(room, event="lobby_update")

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

        if event == "admin_next_question":
            await self.handle_admin_next_question()
            return

        if event == "admin_pause":
            await self.handle_admin_pause()
            return

        if event == "admin_resume":
            await self.handle_admin_resume()
            return

        if event == "admin_end_game":
            await self.handle_admin_end_game()
            return

        await self.send_json({"event": "error", "payload": {"message": f"unknown event: {event}"}})

    async def handle_join(self, payload):
        name = (payload.get("name") or "").strip()
        if not name:
            await self.send_json(
                {
                    "event": "error",
                    "payload": {"message": "name required"}
                }
            )
            return

        # prevent re-join spam
        if self.player_name:
            return

        room = get_or_create_room(self.room_code)
        # if no host yet, first join becomes host
        # (should be done automatically when you join on client side)
        if room.get("hostId") is None:
            room["hostId"] = self.player_id


        #this will techincally never run but if it does sho this
        if room.get("started"):
            await self.send_json(
                {
                    "event": "error",
                    "payload": {"message": "game already started"}
                }
            )
            return

        for p in room["players"]:
            if (p.get("name") or "").lower() == name.lower():
                await self.send_json({"event": "error", "payload": {"message": "name taken"}})
                return

        self.player_name = name
        # include host flag?
        room["players"].append(
            {
                "id": self.player_id,
                "name": name
            }
        )
        save_room(self.room_code, room)
        await self.broadcast_room(room)
        # if game already running, sync this joiner with game_state
        if room.get("started") and room.get("game"):
            await self.send_json(
                {
                    "event": "game_state",
                    "payload": room["game"]
                }
            )

        # do ni need this?
        # await self.channel_layer.group_send(
        #     self.group_name,
        #     {"type": "group_event", "event": "lobby_update", "payload": room},
        # )
        await broadcast_directory(self.channel_layer)

    async def handle_start(self):
        room = get_or_create_room(self.room_code)

        # only host can see admin
        if room.get("hostId") != self.player_id:
            await self.send_json({"event": "error", "payload": {"message": "host only"}})
            return

        room["started"] = True

        # start question 0
        # gotta repalce durationMS with the qset
        room["game"] = {
            "questionIndex": 0,
            "questionStartedAt": self.now_s(),
            "durationMs": 30000,
            "paused": False,
            "pausedAt": None,
        }

        save_room(self.room_code, room)

        await self.broadcast_room(room, event="lobby_update")
        await self.broadcast_room(room, event="game_started")
        await self.broadcast_game_state(room)

        await broadcast_directory(self.channel_layer)


    async def group_event(self, message):
        await self.send_json({"event": message["event"], "payload": message.get("payload", {})})

    async def _require_host(self, room) -> bool:
        if room.get("hostId") != self.player_id:
            await self.send_json({"event": "error", "payload": {"message": "host only"}})
            return False
        return True

    async def handle_admin_next_question(self):
        room = get_or_create_room(self.room_code)
        if not await self._require_host(room):
            return
        if not room.get("started") or not room.get("game"):
            await self.send_json({"event": "error", "payload": {"message": "game not started"}})
            return

        game = room["game"]
        game["questionIndex"] += 1
        game["questionStartedAt"] = self.now_s()
        game["paused"] = False
        game["pausedAt"] = None
        # durationMs stays same for now

        room["game"] = game
        save_room(self.room_code, room)

        await self.broadcast_game_state(room)

    async def handle_admin_pause(self):
        room = get_or_create_room(self.room_code)
        if not await self._require_host(room):
            return
        game = room.get("game")
        if not game or game.get("paused"):
            return

        game["paused"] = True
        game["pausedAt"] = self.now_s()
        room["game"] = game
        save_room(self.room_code, room)

        await self.broadcast_game_state(room)

    async def handle_admin_resume(self):
        room = get_or_create_room(self.room_code)
        if not await self._require_host(room):
            return
        game = room.get("game")
        if not game or not game.get("paused"):
            return

        paused_at = game.get("pausedAt")
        if paused_at:
            # shift the start time forward by paused duration
            game["questionStartedAt"] += (self.now_s() - paused_at)

        game["paused"] = False
        game["pausedAt"] = None
        room["game"] = game
        save_room(self.room_code, room)

        await self.broadcast_game_state(room)

    async def handle_admin_end_game(self):
        room = get_or_create_room(self.room_code)
        if not await self._require_host(room):
            return

        room["started"] = False
        room["game"] = None
        save_room(self.room_code, room)

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "group_event", "event": "game_ended", "payload": {}},
        )
        await broadcast_directory(self.channel_layer)
