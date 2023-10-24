import json
from collections.abc import AsyncGenerator

import psycopg
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from dissonance.chatrooms.forms import RoomForm
from dissonance.chatrooms.models import Message, Room
from dissonance.events import event_stream


def index(request: HttpRequest) -> HttpResponse:
    rooms = Room.objects.order_by("name")
    return render(request, "chatrooms/index.html", {"rooms": rooms, "form": RoomForm()})


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room.objects.select_related("owner"), pk=room_id)
    messages = (
        Message.objects.filter(room=room).select_related("user").order_by("created")
    )
    return render(
        request,
        "chatrooms/room_detail.html",
        {
            "room": room,
            "messages": messages,
        },
    )


def latest_message(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room.objects.select_related("owner"), pk=room_id)
    if latest_message := (
        Message.objects.filter(room=room)
        .select_related("user")
        .order_by("created")
        .last()
    ):
        return render(
            request,
            "chatrooms/_message.html",
            {
                "message": latest_message,
            },
        )
    return HttpResponse()


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


@require_POST
@login_required
def post_message(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=room_id)

    if text := request.POST.get("text"):
        Message.objects.create(room=room, user=request.user, text=text)
    return render(request, "chatrooms/_message_form.html", {"room": room})


def delete_message(request: HttpRequest, message_id: int) -> HttpResponse:
    if request.user.is_authenticated:
        if (
            message := Message.objects.select_related("room")
            .filter(pk=message_id, user=request.user)
            .first()
        ):
            message.delete()

    return HttpResponse()


@transaction.non_atomic_requests
async def events(
    request: HttpRequest,
    room_id: int,
) -> StreamingHttpResponse:
    room = await Room.objects.filter(pk=room_id).afirst()

    if not room:
        raise Http404("no room found")

    return await event_stream(room.get_channel_id())
