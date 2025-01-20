import os
import django
import random

# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.local_settings')

# Initialize Django
django.setup()

from review.models import Quiz, Question
from exams.models import Category, ExamType

# Fetch all categories
all_categories = Category.objects.all()
print(all_categories)

for category in all_categories:
    # Fetch all questions for the current category
    category_questions = list(Question.objects.filter(category=category))

    # Shuffle the questions to ensure randomness
    random.shuffle(category_questions)

    # Determine the number of quizzes to create for this category
    num_quizzes = len(category_questions) // 10

    for i in range(num_quizzes):
        # Create a new quiz for the current category
        new_quiz = Quiz.objects.create(
            title=f"{category.name}: Quiz {i+1}",
            category=category,  # Set the category for the quiz
            quiz_type=category.exam_type 
        )
        print(f"\nCreated {new_quiz.title}")

        # Assign 10 questions to the quiz
        quiz_questions = category_questions[i*10:(i+1)*10]
        for question in quiz_questions:
            new_quiz.questions.add(question)
            print(f"Added question: {question.text}")

print("\nDone.")