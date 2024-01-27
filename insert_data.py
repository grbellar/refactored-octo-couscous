from exams.models import Category, Question, Choice

questions_list = [
    {
        "question": "In a patient with anemia and normal lungs which of the following would be REDUCED?",
        "choices": [
            {"text": "arterial pO2", "is_correct": False},
            {"text": "SaO2", "is_correct": False},
            {"text": "arterial O2 content", "is_correct": True},
            {"text": "arterial-venous content difference", "is_correct": False}
        ]
    },
    {
        "question": "A LOWER than normal PaCO2 is found in:",
        "choices": [
            {"text": "compensated metabolic alkalosis", "is_correct": False},
            {"text": "compensated respiratory acidosis", "is_correct": False},
            {"text": "uncompensated respiratory alkalosis", "is_correct": True},
            {"text": "uncompensated metabolic acidosis", "is_correct": False}
        ]
    }
]


for question in questions_list:
    new_question = Question.objects.create(
        text=question["question"],
        category=Category.objects.get(id=3)
        )
    print(f"Added question: {new_question.text}")
    for choice in question["choices"]:
        new_choice = Choice.objects.create(
            question=new_question,
            text=choice["text"], 
            is_correct=choice["is_correct"]
        )
        print(f"Choice: {new_choice.text}")

print("Done.")
