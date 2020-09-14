from django.urls import path

from chat import consumers

webSocketUrlPatterns = [
    path('chat/', consumers.ChatConsumer.as_asgi()),
]