from django.urls import path

from users.views import UserSearchView
from chat.views import (
    GetConversationView, SendMessageView
)

urlpatterns = [
    path('users/search', UserSearchView.as_view(), name='user-search'),
    path('conversation', GetConversationView.as_view(), name='create-conversation'),
    path('message', SendMessageView.as_view(), name='send-message')
]