from __future__ import annotations

from typing import Dict, List, TypedDict

from django.core.cache import cache

DIRECTORY_GROUP = "kahoot_directory"
ROOM_KEY_PREFIX = "kahoot_room:"
ROOM_INDEX_KEY = "kahoot_room_codes"
ROOM_TTL = 60 * 60 * 2  # 2 hours


class Player(TypedDict):
    id: str
    name: str


class Room(TypedDict):
    name: str
    players: List[Player]
    started: bool


def _room_key(code: str) -> str:
    return f"{ROOM_KEY_PREFIX}{code}"


def _get_room_codes() -> set:
    return cache.get(ROOM_INDEX_KEY) or set()


def _save_room_codes(codes: set):
    cache.set(ROOM_INDEX_KEY, codes, ROOM_TTL)


def get_or_create_room(code: str) -> Room:
    key = _room_key(code)
    room = cache.get(key)
    if room is None:
        room = {"name": code, "players": [], "started": False}
        cache.set(key, room, ROOM_TTL)
        codes = _get_room_codes()
        codes.add(code)
        _save_room_codes(codes)
    return room


def save_room(code: str, room: Room):
    cache.set(_room_key(code), room, ROOM_TTL)


def delete_room_if_empty(code: str) -> bool:
    room = cache.get(_room_key(code))
    if not room:
        return False
    if room["players"]:
        return False
    cache.delete(_room_key(code))
    codes = _get_room_codes()
    codes.discard(code)
    _save_room_codes(codes)
    return True


def rooms_summary():
    codes = _get_room_codes()
    rooms = []
    for code in codes:
        room = cache.get(_room_key(code))
        if room is None:
            continue
        rooms.append(
            {
                "code": code,
                "name": room.get("name", code),
                "players": len(room.get("players", [])),
                "started": bool(room.get("started", False)),
            }
        )
    return rooms
