from django.contrib import admin
from .models import Question, QuestionOption, UserQuizProgress

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    list_display = ('text', 'created_at')
    search_fields = ('text',)

@admin.register(UserQuizProgress)
class UserQuizProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_quiz_date', 'current_streak', 'total_points')
    search_fields = ('user__username',)