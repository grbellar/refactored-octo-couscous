import os
import django
import logging

logging.basicConfig(filename='createquestionslog.txt', level=logging.INFO, format='%(message)s')


# Set the settings module for your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.local_settings') # change when about to insert prod data

# Initialize Django
django.setup()

from review.models import Question, Answer, Explanation
from exams.models import Category
import json

# Get all categories and their IDs
# categories = Category.objects.all()
# print("\nAvailable Categories:")
# for category in categories:
#     print(f"{category.exam_type.name} - {category.name} - {category.id}")
# print("\n")

categories = [
('CAPE - Devices and Equipment.json', 16),
('PBSE - Devices and Equipment.json', 17),
('CAPE - Pathology.json', 10),
('PBSE - Special Procedures & Techniques.json', 27),
('CAPE - Special Patient Groups.json', 24),
('PBSE - Clinical Management.json', 15),
('CAPE - Laboratory Analysis.json', 7),
('PBSE - Pathology.json', 5),
('CAPE - Anatomy and Physiology.json', 4),
('PBSE - Monitoring.json', 19),
('CAPE - Pharmacology.json', 20),
('PBSE - Special Patient Groups.json', 25),
('CAPE - Catastrophic Events and Device Failure.json', 12),
('PBSE - Quality Assurance.json', 23),
('PBSE - Pharmacology.json', 28),
('CAPE - Clinical Management.json', 14),
('CAPE - Special Procedures and Techniques.json', 26),
('PBSE - Anatomy and Physiology.json', 1),
('CAPE - Quality Assurance.json', 22),
('PBSE - Laboratory Analysis.json', 9),
('CAPE - Monitoring.json', 18)
]

logging.info("--*START*--\n----------------------------------\n")
for category in categories:

    logging.info(f"{category[0]} ID: {category[1]}\n")

    fp = category[0]

    with open(f"zfinal-json/{fp}", 'r') as file:
        question_list = json.load(file)

    logging.info(f"{len(question_list)} questions\n")

    for quiz_question in question_list:
        category_from_db = Category.objects.get(id=category[1])
        new_question = Question.objects.create(
            text=quiz_question["text"],
            category=category_from_db
            )
        logging.info(f"\nAdded question no {quiz_question['question_number']}: {new_question.text}")
        for choice in quiz_question["choices"]:
            answer = Answer.objects.create(
                question=new_question,
                text=choice["text"], 
                is_correct=choice["is_correct"]
            )
            logging.info(f"Choice: {answer.text} - {answer.is_correct}")
        explanation = Explanation.objects.create(
            question=new_question,
            text=quiz_question["explanation"],
            sources=quiz_question["sources"]
        )

logging.info("--*END*--.")
