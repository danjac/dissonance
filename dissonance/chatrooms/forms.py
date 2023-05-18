from django import forms

from dissonance.chatrooms.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name",)
