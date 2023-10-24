import json

from django.db import connection
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dissonance.chatrooms.models import Message, Room
from dissonance.events import notify


@receiver(post_save, sender=Message, dispatch_uid="message:created")
def message_notify_on_create(
    sender: type[Message], instance: Message, **kwargs
) -> None:
    notify(instance.room.get_channel_id(), "new-message")


@receiver(pre_delete, sender=Message, dispatch_uid="message:deleted")
def message_notify_on_delete(
    sender: type[Message], instance: Message, **kwargs
) -> None:
    notify(instance.room.get_channel_id(), f"delete-message-{instance.pk}")
