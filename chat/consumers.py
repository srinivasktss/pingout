import json

from channels.generic.websocket import AsyncWebsocketConsumer

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Websocket Connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("Websocket Disconnected")
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))