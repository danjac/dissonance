import json
from collections.abc import AsyncGenerator

import psycopg
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
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
            data=str(message.pk),
        )
    return render(request, "chatrooms/_message_form.html", {"room": room})


def latest_message(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, pk=room_id)
    if (
        latest_message := Message.objects.filter(room=room)
        .select_related("user")
        .order_by("-created")
        .first()
    ):
        return render(
            request,
            "chatrooms/_message.html",
            {"message": latest_message},
        )
    return HttpResponse(status=204)


async def messages_stream(
    request: HttpRequest,
    room_id: int,
) -> StreamingHttpResponse:
    room = await Room.objects.filter(pk=room_id).afirst()

    async def _stream_messages() -> AsyncGenerator[str, None]:
        connection_params = connection.get_connection_params()
        connection_params.pop("cursor_factory")

        conn = await psycopg.AsyncConnection.connect(
            **connection_params, autocommit=True
        )

        async with conn.cursor() as cursor:
            await cursor.execute(f"LISTEN room{room.pk}")
            gen = conn.notifies()
            async for notify_msg in gen:
                yield _sse_message(**json.loads(notify_msg.payload))

    if room:
        return StreamingHttpResponse(
            streaming_content=_stream_messages(),
            content_type="text/event-stream",
        )
    raise Http404("Room not found")


def _sse_message(*, event: str, data: str) -> str:
    return "\n".join([f"event: {event}", f"data: {data}", "\n"])


def _notify(*, channel: str, event: str, data: str) -> None:
    payload = json.dumps(
        {
            "event": event,
            "data": data,
        },
    )
    with connection.cursor() as cursor:
        cursor.execute(f"NOTIFY {channel}, '{payload}'")
