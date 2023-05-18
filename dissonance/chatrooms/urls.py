from django.urls import path

from dissonance.chatrooms import views

app_name = "chatrooms"


urlpatterns = [
    path("", views.index, name="index"),
    path("rooms/new/", views.create_room, name="create_room"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/<int:room_id>/post/", views.post_message, name="post_message"),
    path("rooms/<int:room_id>/messages/", views.messages, name="messages"),
    path("rooms/<int:room_id>/stream/", views.messages_stream, name="messages_stream"),
]
