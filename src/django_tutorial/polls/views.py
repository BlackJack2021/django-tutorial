from django.http import HttpRequest, HttpResponse


# ruff:noqa: ARG001, 必須のパラメータなので警告を無視
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")
