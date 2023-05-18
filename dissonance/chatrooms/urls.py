from django.urls import path

from dissonance.chatrooms import views

app_name = "chatrooms"


urlpatterns = [
    path("", views.index, name="index"),
    path("ping/", views.ping, name="ping"),
    path("rooms/new/", views.create_room, name="create_room"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/<int:room_id>/latest", views.latest_message, name="latest_message"),
    path("rooms/<int:room_id>/post/", views.post_message, name="post_message"),
    path("rooms/<int:room_id>/events/", views.events, name="events"),
    path("messages/<int:message_id>/", views.delete_message, name="delete_message"),
]
