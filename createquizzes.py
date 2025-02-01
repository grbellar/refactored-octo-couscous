import os
import django
import random
import logging

# Set up logging to a file
logging.basicConfig(filename='createquizzeslog.txt', level=logging.INFO, format='%(message)s')

# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.local_settings')

# Initialize Django
django.setup()

from review.models import Quiz, Question
from exams.models import Category, ExamType

# Fetch all categories
all_categories = Category.objects.all()
logging.info("--*START*--\n----------------------------------\n")
logging.info(all_categories)

for category in all_categories:
    # Fetch all questions for the current category
    category_questions = list(Question.objects.filter(category=category))

    logging.info(f"\n---------------------------\n{category.name} - {category.exam_type.name}: {len(category_questions)} questions")

    # Shuffle the questions to ensure randomness
    random.shuffle(category_questions)

    # Determine the number of quizzes to create for this category
    num_quizzes = (len(category_questions) + 9) // 10  # Calculate the number of quizzes needed

    for i in range(num_quizzes):
        # Create a new quiz for the current category
        new_quiz = Quiz.objects.create(
            title=f"{category.name}: Quiz {i+1}",
            category=category,  # Set the category for the quiz
            quiz_type=category.exam_type 
        )
        logging.info(f"\nCreated {new_quiz.title}\n with category ID {category.id}")

        # Assign questions to the quiz
        quiz_questions = category_questions[i*10:(i+1)*10]
        for question in quiz_questions:
            new_quiz.questions.add(question)
            logging.info(f"Added question: {question.text}")

logging.info("--*END*--\n----------------------------------\n")