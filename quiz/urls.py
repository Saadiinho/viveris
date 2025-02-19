# urls.py pour le quiz
from django.urls import path
from .views import QuizViewSet

urlpatterns = [
    path('getquiz/', QuizViewSet.as_view({
        'get': 'daily_questions'
    })),
    path('submitquiz/', QuizViewSet.as_view({
        'post': 'submit_answers'
    })),
]