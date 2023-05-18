from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# @login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "chatrooms/index.html")
