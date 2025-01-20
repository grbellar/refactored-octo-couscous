import os
import django
import random

# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.local_settings')

# Initialize Django
django.setup()

from review.models import Question, Quiz

# Fetch all questions
all_questions = list(Question.objects.all())

# Shuffle the questions to ensure randomness
random.shuffle(all_questions)

# Determine the number of quizzes to create
num_quizzes = len(all_questions) // 10

for i in range(num_quizzes):
    # Create a new quiz
    new_quiz = Quiz.objects.create(title=f"Anatomy and Physiology: Quiz{i+1}")
    print(f"\nCreated {new_quiz.title}")

    # Assign 10 questions to the quiz
    quiz_questions = all_questions[i*10:(i+1)*10]
    for question in quiz_questions:
        new_quiz.questions.add(question)
        print(f"Added question: {question.text}")

print("\nDone.")