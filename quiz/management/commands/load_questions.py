# quiz/management/commands/load_questions.py
from django.core.management.base import BaseCommand
from quiz.models import Question, QuestionOption
import json

class Command(BaseCommand):
    help = 'Charge les questions du quiz depuis un fichier JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Chemin vers le fichier JSON')

    def handle(self, *args, **options):  # Changé kwargs en options
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                for q_data in data['quiz']:
                    # Créer la question
                    question = Question.objects.create(
                        text=q_data['question']
                    )
                    
                    # Créer les options
                    for option in q_data['options']:
                        QuestionOption.objects.create(
                            question=question,
                            text=option,
                            is_correct=(option == q_data['answer'])
                        )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Question créée: {question.text[:50]}...')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Chargement terminé! {len(data["quiz"])} questions ajoutées.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du chargement: {str(e)}')
            )