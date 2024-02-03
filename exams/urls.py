from django.urls import path
from .views import take_exam_view, exam_complete, test_ajax_request

urlpatterns = [
    path("exams/exam/<uuid:uuid>", take_exam_view, name='take-exam'),
    path("exam-complete/", exam_complete, name="exam-complete"),
    path("test-ajax/", test_ajax_request, name="test-ajax")
]