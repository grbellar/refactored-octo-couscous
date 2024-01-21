from django.urls import path
from .views import take_exam_view

urlpatterns = [
    path("exams/exam/<int:pk>", take_exam_view, name='take-exam')
]