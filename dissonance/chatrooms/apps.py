from django.apps import AppConfig


class ChatroomsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dissonance.chatrooms"

    def ready(self, **kwargs) -> None:
        from dissonance.chatrooms import signals  # noqa
