from exams.models import Category, Question, Choice
import json


with open('data.json', 'r') as file:
    question_list = json.load(file)

for question in question_list:
    new_question = Question.objects.create(
        text=question["text"],
        category=Category.objects.get(id=3)
        )
    print(f"\nAdded question: {new_question.text}")
    for choice in question["choices"]:
        new_choice = Choice.objects.create(
            question=new_question,
            text=choice["text"], 
            is_correct=choice["is_correct"]
        )
        print(f"Choice: {new_choice.text}")

print("\nDone.")
