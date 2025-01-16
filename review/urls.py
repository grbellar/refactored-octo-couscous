from django.urls import path
from .views import take_quiz, check_answer, save_answer, update_question_index

urlpatterns = [
    path('review/quiz/<uuid:quiz_uuid>', take_quiz, name='take-quiz'),
    path('review/quiz/<uuid:quiz_uuid>/check-answer', check_answer, name='check-answer'),
    path('save-answer/<uuid:quiz_uuid>', save_answer, name='save-answer'),
    path('update-question-index/<uuid:quiz_uuid>', update_question_index, name='update-question-index'),

]

