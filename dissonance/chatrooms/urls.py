from django.urls import path

from dissonance.chatrooms import views

app_name = "chatrooms"


urlpatterns = [
    path("", views.index, name="index"),
]
