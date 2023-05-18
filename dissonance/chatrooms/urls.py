from django.urls import path

from dissonance.chatrooms import views

app_name = "chatrooms"


urlpatterns = [
    path("", views.index, name="index"),
    path("rooms/new/", views.create_room, name="create_room"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
]
