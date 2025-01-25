from django.db.models import F
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse

from .models import Choice, Question


def index(request: HttpRequest) -> HttpResponse:
    # ハイフンありだと降順で並ぶ。ハイフンがないと昇順。
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context = {
        "latest_question_list": latest_question_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})


def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # 以下が主なエラー時
        # 1. POST メソッドでデータが送信されていない
        # 2. 選択肢が選択されていない
        # 3. 存在しない選択肢のIDが送信s慣れた場合 (Question.DoesNotExist)
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "選択肢が選択されていません"},
        )
    else:
        # F はデータの競合を避けつつ値を更新するために利用する
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # POSTメソッドでデータが更新された場合は、HttpResponseRedirect を返すのが Web のベストプラクティス
        # reverse は URL を「逆引き」するもの
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
