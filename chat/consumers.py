import json

from channels.generic.websocket import AsyncWebsocketConsumer

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Websocket Connected")

        self.user = self.scope['user']
        print(self.user)

        self.personal_group = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.personal_group ,
            self.channel_name
        )

        await self.accept()

        print(f"{self.user.username} connected — {self.channel_name}")

    async def disconnect(self, close_code):
        if hasattr(self, 'personal_group'):
            await self.channel_layer.group_discard(
                self.personal_group,
                self.channel_name
            )

        print("Websocket Disconnected")
        print(f"{self.user.username} disconnected — {self.channel_name}")

    async def receive(self, text_data):
        pass

    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event['conversation_id'],
            'from': event['from_user'],
            'to': event['to_user'],
            'message': event['message']
        }))