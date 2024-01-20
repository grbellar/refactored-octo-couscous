from django.urls import path

from .views import SingleQuestionView, HandleQuestionSubmissions

urlpatterns = [
    path("exams/question/<int:pk>", SingleQuestionView.as_view(), name="question"),
    path("exams/success/", HandleQuestionSubmissions.as_view(), name="success")
]