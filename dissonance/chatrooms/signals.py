import json

from django.db import connection
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dissonance.chatrooms.models import Message, Room


@receiver(post_save, sender=Message, dispatch_uid="message:created")
def message_notify_on_create(
    sender: type[Message], instance: Message, **kwargs
) -> None:
    _notify_for_room(instance.room, "new-message")


@receiver(pre_delete, sender=Message, dispatch_uid="message:deleted")
def message_notify_on_delete(
    sender: type[Message], instance: Message, **kwargs
) -> None:
    _notify_for_room(instance.room, f"delete-message-{instance.pk}")


def _notify_for_room(room: Room, event: str, data: str = "none") -> None:
    with connection.cursor() as cursor:
        payload = json.dumps(
            {
                "event": event,
                "data": data,
            },
        )
        cursor.execute(f"NOTIFY {room.get_channel_id()}, '{payload}'")
