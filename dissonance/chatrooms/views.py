from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from dissonance.chatrooms.forms import RoomForm
from dissonance.chatrooms.models import Message, Room


@login_required
def index(request: HttpRequest) -> HttpResponse:
    rooms = Room.objects.order_by("name")
    return render(request, "chatrooms/index.html", {"rooms": rooms, "form": RoomForm()})


@login_required
def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room.objects.select_related("owner"), pk=room_id)
    messages = (
        Message.objects.filter(room=room).select_related("user").order_by("-created")
    )

    return render(
        request,
        "chatrooms/room_detail.html",
        {
            "room": room,
            "messages": messages,
        },
    )


@login_required
def create_room(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect(room)
    else:
        form = RoomForm()

    return render(request, "chatrooms/room_form.html", {"form": form})
