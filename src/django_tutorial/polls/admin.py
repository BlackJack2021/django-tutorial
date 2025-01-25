from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    # 管理者画面でのフィールドの並び順を指定
    # fields = ["pub_date", "question_text"]

    # より構造化して admin の表示を制御
    fieldsets = [
        ("質問のタイトル", {"fields": ["question_text"]}),
        ("質問の公開日", {"fields": ["pub_date"]}),
    ]
    inlines = [ChoiceInline]

    list_display = ["question_text", "pub_date", "was_published_recently"]

    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
