from api.consumers.kahoot_state import DIRECTORY_GROUP, rooms_summary

async def broadcast_directory(channel_layer):
    await channel_layer.group_send(
        DIRECTORY_GROUP,
        {
            "type": "directory_event",
            "event": "rooms",
            "payload": {"rooms": rooms_summary()},
        },
    )

