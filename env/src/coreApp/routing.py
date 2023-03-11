from django.urls import re_path
from . import consumers

# list of URL patterns that maps to a consumer.
# Used to define WebSocket endpoints for the Django Channels application.
websocket_urlpatterns = [
    re_path(r"ws/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
