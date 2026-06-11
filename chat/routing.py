from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/main', consumers.MainConsumer.as_asgi(), name='main'),
]