import os
import django

# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.local_settings') # change when about to insert prod data

# Initialize Django
django.setup()

from review.models import Question, Answer, Explanation
from exams.models import Category
import json
with open('PBSE-AP.json', 'r') as file:
    question_list = json.load(file)

for quiz_question in question_list:
    new_question = Question.objects.create(
        text=quiz_question["text"],
        category=Category.objects.get(id=1)
        )
    print(f"\nAdded question: {new_question.text}")
    for choice in quiz_question["choices"]:
        answer = Answer.objects.create(
            question=new_question,
            text=choice["text"], 
            is_correct=choice["is_correct"]
        )
        print(f"Choice: {answer.text}")
    explanation = Explanation.objects.create(
        question=new_question,
        text=quiz_question["explanation"]
    )

print("\nDone.")
