from django.urls import path
from .views import question_view, take_exam_view

urlpatterns = [
    path("exams/question/<int:pk>", question_view, name='question'),
    path("exams/exam/<int:pk>", take_exam_view, name='take-exam')
]