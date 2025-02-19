# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Question(models.Model):
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class UserQuizProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Utilisation de AUTH_USER_MODEL au lieu de User
        on_delete=models.CASCADE
    )
    last_quiz_date = models.DateField(null=True, blank=True)
    completed_questions = models.ManyToManyField(Question, blank=True)
    current_streak = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def can_take_quiz(self):
        return self.last_quiz_date != timezone.now().date()

    def __str__(self):
        return f"Quiz progress for {self.user.username}"