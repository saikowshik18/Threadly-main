from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('room/<int:pk>/', views.chat_room_view, name='chat_room'),
    path('start/<int:item_pk>/', views.chat_start_view, name='chat_start'),
    path('room/<int:pk>/send/', views.send_message_view, name='send_message'),
    path('room/<int:pk>/poll/', views.poll_messages_view, name='poll_messages'),
]
