from django.core.management.base import BaseCommand
from django.db.models import Count
from exams.models import Exam, Question, ExamType, Category
import random
from typing import List, Optional

class Command(BaseCommand):
    help = 'Generates an exam with random questions from the database'

    def add_arguments(self, parser):
        parser.add_argument('--exam-type', type=str, required=True, help='Name of the exam type')
        parser.add_argument('--num-questions', type=int, required=True, help='Number of questions to include in the exam')
        parser.add_argument('--exam-name', type=str, required=True, help='Name of the exam')
        parser.add_argument('--description', type=str, help='Description of the exam')
        parser.add_argument('--allow-reuse', action='store_true', help='Allow reusing questions that have been used in other exams')

    def handle(self, *args, **options):
        exam_type_name = options['exam_type']
        num_questions = options['num_questions']
        exam_name = options['exam_name']
        description = options.get('description')
        allow_reuse = options.get('allow_reuse', False)

        try:
            exam_type = ExamType.objects.get(name=exam_type_name)
        except ExamType.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Exam type "{exam_type_name}" does not exist'))
            return

        # Get all questions for this exam type
        questions = Question.objects.filter(category__exam_type=exam_type)
        
        if not questions.exists():
            self.stdout.write(self.style.ERROR(f'No questions found for exam type "{exam_type_name}"'))
            return

        # Get questions that haven't been used in any exam
        unused_questions = questions.exclude(exam__isnull=False)
        self.stdout.write(self.style.SUCCESS(f'Found {unused_questions.count()} unused questions'))
        
        # If we don't have enough unused questions and allow_reuse is True, include used questions
        if unused_questions.count() < num_questions and allow_reuse:
            self.stdout.write(self.style.WARNING(
                f'Not enough unused questions ({unused_questions.count()}). '
                f'Will include previously used questions to reach {num_questions} total.'
            ))
            questions_to_use = list(unused_questions) + list(questions.filter(exam__isnull=False))
        else:
            questions_to_use = list(unused_questions)

        if len(questions_to_use) < num_questions:
            self.stdout.write(self.style.ERROR(
                f'Not enough questions available. Found {len(questions_to_use)} questions, '
                f'but need {num_questions}.'
            ))
            return

        # Randomly select questions
        selected_questions = random.sample(questions_to_use, num_questions)

        # Create the exam
        exam = Exam.objects.create(
            name=exam_name,
            exam_type=exam_type,
            description=description,
            is_active=True
        )
        exam.questions.set(selected_questions)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created exam "{exam_name}" with {num_questions} questions'
        )) 