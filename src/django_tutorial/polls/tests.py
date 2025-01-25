import datetime
from unittest.mock import patch

from django.test import TestCase
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
