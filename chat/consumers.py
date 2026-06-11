import json

from channels.generic.websocket import AsyncWebsocketConsumer

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Websocket Connected")

        self.user = self.scope['user']
        print(self.user)

        self.personal_group = f"user_{self.user.username}"

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
        text_data_json = json.loads(text_data)
        from_user = text_data_json['from']
        to_user = text_data_json['to']
        message = text_data_json['message']

        await self.channel_layer.group_send(
            f"user_{to_user}",
            {
                'type': 'new_message',
                'from_user': from_user,
                'to_user': to_user,
                'message': message
            }
        )

        # Send the message back to the sender as well
        await self.channel_layer.group_send(
            f"user_{from_user}",
            {
                'type': 'new_message',
                'from_user': from_user,
                'to_user': to_user,
                'message': message
            }
        )

    async def new_message(self, event):
        from_user = event['from_user']
        to_user = event['to_user']
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'from': from_user,
            'to': to_user,
            'message': message
        }))