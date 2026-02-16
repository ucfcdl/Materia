from django.urls import re_path
from api.consumers.kahoot import KahootConsumer
from api.consumers.kahoot_directory import KahootDirectoryConsumer

websocket_urlpatterns = [
    re_path(r"^ws/kahoot/$", KahootDirectoryConsumer.as_asgi()),
    re_path(r"^ws/kahoot/(?P<room_code>[A-Z0-9]{4,8})/$", KahootConsumer.as_asgi()),
]

# websocket_urlpatterns = [
#     re_path(r"^ws/kahoot/(?P<room_code>[A-Z0-9]{4,8})/$", KahootConsumer.as_asgi()),
# ]

