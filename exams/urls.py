from django.urls import path
from .views import take_exam_view, exam_complete

urlpatterns = [
    path("exams/exam/<uuid:uuid>", take_exam_view, name='take-exam'),
    path("exam-complete/", exam_complete, name="exam-complete")
]