from django.urls import path
from . import views

urlpatterns = [
    path('chat_bot/', views.chat_bot_view, name='chat_bot'),
    path('ask/', views.chat, name='chatbot_ask'), 
]
