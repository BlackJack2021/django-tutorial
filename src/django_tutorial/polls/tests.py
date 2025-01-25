import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """未来の質問については False を返すことを確認"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """24時間前以前に公開された情報については、False を返すことを確認"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """過去の質問については、24時間前までに公開されたものが True を返すことを確認

        評価時点で time の定義から1秒以上経過してしまうとテストしたいことがテストできないので、
        現在時刻を固定した状態でテストを行う。
        ただし、timezone.now がメソッドの中で使われていると仮定している。
        """
        current_time = timezone.now()

        time = current_time - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        with patch("django.utils.timezone.now", return_value=current_time):
            self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text: str, days: int) -> Question:
    """<days>日後に公開された質問を作成するためのショートカット関数"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """質問がない場合は、適切なメッセージが表示されることを確認"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "質問がありません。")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """過去の質問が表示されることを確認"""
        question = create_question(question_text="過去の質問", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """未来の質問は表示されないことを確認"""
        create_question(question_text="未来の質問", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "質問がありません。")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_question(self):
        """過去の質問と未来の質問が混在している場合は、過去の質問のみが表示されることを確認"""
        past_question = create_question(question_text="過去の質問", days=-30)
        create_question(question_text="未来の質問", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [past_question],
        )

    def test_two_past_questions(self):
        """過去の質問が2つ以上存在する場合は、複数の質問がcontextに含まれることを表示"""
        question1 = create_question(question_text="過去の質問1", days=-30)
        question2 = create_question(question_text="過去の質問2", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDEtailViewTests(TestCase):
    def test_future_question(self):
        """未来の質問の詳細ページへのアクセスは404を返すことを確認"""
        future_question = create_question(question_text="未来の質問", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """過去の質問の詳細ページでは質問のテキストが表示されることを確認"""
        past_question = create_question(question_text="過去の質問", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
