import json
from collections.abc import AsyncGenerator

import psycopg
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

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


@require_POST
@login_required
def post_message(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=room_id)

    if text := request.POST.get("text"):
        message = Message.objects.create(room=room, user=request.user, text=text)
        _notify(
            channel=f"room{room.pk}",
            event="new-message",
            event_id=str(message.pk),
            data=_render_message(message),
        )
    return HttpResponse("OK")


async def messages_stream(
    request: HttpRequest,
    room_id: int,
) -> StreamingHttpResponse:
    if room := Room.objects.filter(pk=room_id).afirst():
        latest_message = Message.objects.filter(room=room).order_by("-created").afirst()

        return StreamingHttpResponse(
            streaming_content=_stream_messages(room, latest_message),
            content_type="text/event-stream",
        )
    raise Http404("Room not found")


async def _stream_messages(
    room: Room, latest_message: Message | None = None
) -> AsyncGenerator[str, None]:
    connection_params = connection.get_connection_params()
    connection_params.pop("cursor_factory")

    if latest_message:
        yield _sse_message(
            event="new-message",
            event_id=str(latest_message.pk),
            data=_render_message(latest_message),
        )

    conn = await psycopg.AsyncConnection.connect(**connection_params, autocommit=True)

    async with conn.cursor() as cursor:
        await cursor.execute(f"LISTEN room{room.pk}")
        async for notify_msg in conn.notifies():
            yield _sse_message(**json.loads(notify_msg.payload))


def _sse_message(*event: str, event_id: str, data: str) -> str:
    return "\n".join(
        [
            f"id: {event_id}",
            f"event: {event}",
            f"data: {data}",
        ]
    )


def _notify(*, channel: str, event: str, event_id: int, data: str) -> None:
    payload = json.dumps(
        {
            "event": event,
            "event_id": event_id,
            "data": data,
        },
    )
    with connection.cursor() as cursor:
        cursor.execute(f"NOTIFY {channel}, '{payload}'")


def _render_message(message) -> str:
    return render_to_string("chatrooms/_message.html", {"message": message})
