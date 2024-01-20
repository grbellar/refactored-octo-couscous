from django.urls import path
from .views import question_view

urlpatterns = [
    path("exams/question/<int:pk>", question_view, name='question')
]