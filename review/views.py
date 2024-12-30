from django.shortcuts import render
import json
from .models import Quiz

with open('review/test-review-data.json', 'r') as file:
    quizzes = json.load(file)

# Create your views here.
def take_quiz(request):
    print(quizzes)
    for question in quizzes:
        print(question["text"])
    return render(request, "review/take_quiz.html")
