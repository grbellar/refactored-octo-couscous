from django.urls import path
from pages.views import my_quizzes
from .views import take_quiz

# TODO: Setup take-quiz to actually accept quiz id as parameter
urlpatterns = [
    path('my-quizzes/', my_quizzes, name='my-quizzes'),
    path('take-quiz/', take_quiz, name='take-quiz')
]

