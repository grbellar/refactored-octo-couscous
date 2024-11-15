from django.shortcuts import render
import json

with open('review/test-review-data.json', 'r') as file:
    quizzes = json.load(file)

# Create your views here.
def take_review(request):
    print(quizzes)
    for question in quizzes:
        print(question["text"])
    return render(request, "review/take_review.html")
