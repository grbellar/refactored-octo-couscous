from django.urls import path
from .views import take_quiz, save_answer, update_question_index, set_quiz_complete

urlpatterns = [
    path('review/quiz/<uuid:quiz_uuid>', take_quiz, name='take-quiz'),
    path('save-answer/<uuid:quiz_uuid>', save_answer, name='save-answer'),
    path('update-question-index/<uuid:quiz_uuid>', update_question_index, name='update-question-index'),
    path('set-quiz-complete/<uuid:quiz_uuid>', set_quiz_complete, name='set-quiz-complete')

]

