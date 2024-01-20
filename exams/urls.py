from django.urls import path
from .views import question_view, TakeExamView

urlpatterns = [
    path("exams/question/<int:pk>", question_view, name='question'),
    path("exams/take-exam", TakeExamView.as_view(), name='take-exam')
]