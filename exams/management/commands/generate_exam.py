from django.core.management.base import BaseCommand
from django.db.models import Count
from exams.models import Exam, Question, ExamType, Category
import random
from typing import List, Optional

# Question distribution for Perfusion Basic Science Examination (PBSE)
BASIC_SCIENCE_QUESTIONS = {
    "Anatomy and Physiology": 24,
    "Pharmacology": 12,
    "Pathology": 15,
    "Laboratory Analysis": 4,
    "Quality Assurance": 1,
    "Devices and Equipment": 11,
    "Clinical Management": 11,
    "Special Patient Groups": 6,
    "Special Procedures and Techniques": 11,
    "Catastrophic Events and Device Failure": 2,
    "Monitoring": 3
}

# Question distribution for Clinical Application Perfusion Examination (CAPE)
CLINICAL_APPLICATION_QUESTIONS = {
    "Anatomy and Physiology": 3,
    "Pharmacology": 3,
    "Pathology": 22,
    "Laboratory Analysis": 8,
    "Quality Assurance": 4,
    "Devices and Equipment": 9,
    "Clinical Management": 23,
    "Special Patient Groups": 6,
    "Special Procedures and Techniques": 16,
    "Catastrophic Events and Device Failure": 4,
    "Monitoring": 2
}

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

        # Determine which category distribution to use based on exam type
        if exam_type_name == "Basic Science":
            category_distribution = BASIC_SCIENCE_QUESTIONS
        elif exam_type_name == "Clinical Application":
            category_distribution = CLINICAL_APPLICATION_QUESTIONS
        else:
            self.stdout.write(self.style.ERROR(f'Invalid exam type: {exam_type_name}'))
            return

        # Create the exam
        exam = Exam.objects.create(
            name=exam_name,
            exam_type=exam_type,
            description=description,
            is_active=True,
            is_promo=True
        )

        selected_questions = []
        operation_failed = False

        # Select questions for each category according to the distribution
        for category_name, num_required in category_distribution.items():
            try:
                category = Category.objects.get(name=category_name, exam_type=exam_type)
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category "{category_name}" does not exist for exam type {exam_type_name}'))
                operation_failed = True
                break

            # First try to get unused questions for this category
            unused_questions = list(Question.objects.filter(
                category=category
            ).exclude(exam__isnull=False))

            # If we don't have enough unused questions and allow_reuse is False, abort
            if len(unused_questions) < num_required and not allow_reuse:
                self.stdout.write(self.style.ERROR(
                    f'Not enough unused questions for category "{category_name}". '
                    f'Found {len(unused_questions)} unused questions, but need {num_required}. '
                    f'Use --allow-reuse to include previously used questions.'
                ))
                operation_failed = True
                break

            questions_needed = num_required
            category_selected = []

            # First use unused questions
            if unused_questions:
                num_unused_to_use = min(len(unused_questions), questions_needed)
                unused_selected = random.sample(unused_questions, num_unused_to_use)
                category_selected.extend(unused_selected)
                questions_needed -= num_unused_to_use

            # If we still need more questions and allow_reuse is True, use previously used questions
            if questions_needed > 0 and allow_reuse:
                used_questions = list(Question.objects.filter(
                    category=category,
                    exam__isnull=False
                ).distinct())
                
                if used_questions:
                    num_used_to_use = min(len(used_questions), questions_needed)
                    used_selected = random.sample(used_questions, num_used_to_use)
                    category_selected.extend(used_selected)
                    questions_needed -= num_used_to_use

                # If we still need questions after using both unused and used questions
                if questions_needed > 0:
                    self.stdout.write(self.style.ERROR(
                        f'Not enough questions available for category "{category_name}". '
                        f'Found {len(category_selected)} total questions, but need {num_required}.'
                    ))
                    operation_failed = True
                    break

            selected_questions.extend(category_selected)
            self.stdout.write(self.style.SUCCESS(
                f'Selected {len(category_selected)} questions from category "{category_name}" '
                f'({len(unused_questions)} unused)'
            ))

        # If operation failed or no questions were selected, clean up and exit
        if operation_failed or not selected_questions:
            self.stdout.write(self.style.ERROR('Exam creation failed. Cleaning up...'))
            exam.delete()
            return

        # Add selected questions to the exam
        exam.questions.set(selected_questions)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created exam "{exam_name}" with {len(selected_questions)} questions'
        )) 