import json
from channels.generic.websocket import AsyncWebsocketConsumer

# This consumer sets up the basic functionality for the app's WebSocket chat application.
class ChatConsumer(AsyncWebsocketConsumer):

    # Override the connect() method to handle WebSocket connection requests.
    # In this method, the consumer adds the client to the specific group identified by self.rooself.room_group_name based on the URL route.
    # It also accepts the connection request.
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    # Override the disconnect() method to handle WebSocket disconnection requests.
    # In this method, the consumer removes the client from the group identified by self.room_group_name.
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Override the receive() method to handle WebSocket messages received from clients.
    # In this method, the consumer extracts the message from the received text data and sends the message to
    # the group identified by self.room_group_name.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Define a chat_message() method to handle messages sent to the group.
    # In this method, the consumer sends the message to all clients in the group.
    # Use json.dumps() and json.loads() to serialize and deserialize data
    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))
