from django.urls import path

from .views import HomePageView, AboutPageView, my_exams_view

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("my-exams/", my_exams_view, name="my-exams"),
]
