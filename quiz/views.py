from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import random
from datetime import timedelta
from django.utils import timezone

from .models import Question, QuestionOption, UserQuizProgress
from .serializer import QuestionSerializer

class QuizViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['GET'])
    def daily_questions(self, request):
        user_progress, created = UserQuizProgress.objects.get_or_create(
            user=request.user
        )
        
        if not user_progress.can_take_quiz():
            return Response(
                {"error": "Vous avez déjà complété le quiz aujourd'hui"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get 5 random questions user hasn't answered
        completed_questions = user_progress.completed_questions.all()
        available_questions = Question.objects.exclude(
            id__in=completed_questions
        )
        
        if not available_questions.exists():
            user_progress.completed_questions.clear()
            available_questions = Question.objects.all()
        
        questions = random.sample(
            list(available_questions), 
            min(5, available_questions.count())
        )
        
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def submit_answers(self, request):
        user_progress = get_object_or_404(UserQuizProgress, user=request.user)
        
        if not user_progress.can_take_quiz():
            return Response(
                {"error": "Vous avez déjà complété le quiz aujourd'hui"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answers = request.data.get('answers', [])
        points_earned = 0
        
        for answer in answers:
            question = get_object_or_404(Question, id=answer['question_id'])
            selected_option = get_object_or_404(
                QuestionOption, 
                id=answer['option_id'],
                question=question
            )
            
            if selected_option.is_correct:
                points_earned += 5  # Points par bonne réponse
            
            user_progress.completed_questions.add(question)
        
        request.user.total_points += points_earned
        request.user.save()
        user_progress.last_quiz_date = timezone.now().date()
        
        # Mise à jour du streak
        yesterday = timezone.now().date() - timedelta(days=1)
        if user_progress.last_quiz_date == yesterday:
            user_progress.current_streak += 1
        else:
            user_progress.current_streak = 1
        
        user_progress.save()
        
        return Response({
            'points_earned': points_earned,
            'total_points': user_progress.total_points,
            'current_streak': user_progress.current_streak
        })