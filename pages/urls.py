from django.urls import path
from .views import *

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("podcast/", PodcastPageView.as_view(), name="podcast"),
    path("get-access/buy/", get_access_buy, name="get-access-buy"),
    path("my-exams/", my_exams, name="my-exams"),
    path("my-results/", my_results, name="my-results"),
    path("my-results/result/<int:id>", single_result, name="single-result"),
    path('my-quizzes/', choose_quiz_type, name='choose-quiz-type'),
    path('my-quizzes/<str:quiz_type_name>', choose_quiz_category, name='choose-quiz-category'),
    path('my-quizzes/<str:_quiz_type_name>/<str:_category_name>-<int:category_id>', choose_quiz, name='choose-quiz'),
]
