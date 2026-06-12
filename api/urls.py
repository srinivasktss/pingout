from django.urls import path

from users.views import UserSearchView
from chat.views import GetConversationView

urlpatterns = [
    path('users/search', UserSearchView.as_view(), name='user-search'),
    path('conversations/', GetConversationView.as_view(), name='create-conversation')
]