from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, TypedDict

DIRECTORY_GROUP = "kahoot_directory"


class Player(TypedDict):
    id: str
    name: str


class Room(TypedDict):
    name: str
    players: List[Player]
    started: bool


# ROOMS[CODE] = {"name": str, "players": [{"id","name"}], "started": bool}
ROOMS: Dict[str, Room] = {}


def get_or_create_room(code: str) -> Room:
    if code not in ROOMS:
        ROOMS[code] = {"name": code, "players": [], "started": False}
    return ROOMS[code]


def delete_room_if_empty(code: str) -> bool:
    room = ROOMS.get(code)
    if not room:
        return False
    if room["players"]:
        return False
    ROOMS.pop(code, None)
    return True


def rooms_summary():
    rooms = []
    for code, room in ROOMS.items():
        rooms.append(
            {
                "code": code,
                "name": room.get("name", code),
                "players": len(room.get("players", [])),
                "started": bool(room.get("started", False)),
            }
        )
    return rooms

