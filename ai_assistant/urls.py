from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_assistant, name='ai_assistant'),
    path('chat/', views.chat_api, name='chat_api'),
]