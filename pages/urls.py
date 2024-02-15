from django.urls import path

from .views import *

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("get-access/buy/", get_access_buy, name="get-access-buy"),
    path("my-exams/", my_exams, name="my-exams"),
    path("my-results/", my_results, name="my-results"),
    path("my-results/result/<int:id>", single_result, name="single-result")
]
