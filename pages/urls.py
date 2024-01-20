from django.urls import path

from .views import HomePageView, AboutPageView, MyExamsView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("my-exams/", MyExamsView.as_view(), name="my-exams"),
]
