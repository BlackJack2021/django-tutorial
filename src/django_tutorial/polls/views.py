from django.db.models import F
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    # template_name を指定しない場合は、
    # デフォルトで <app_name>/<model_name>_list.html が使用される
    # 今回はデフォルト名とは異なる templates 名なので、明示的に指定する必要がある
    template_name = "polls/index.html"
    # context_object_name を指定しない場合、
    # デフォルトで <model_name>_list という名称になる
    # デフォルト値とは異なる名前で定義していたので、明示的に指定が必要
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """最新の5件の質問を取得する"""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


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
