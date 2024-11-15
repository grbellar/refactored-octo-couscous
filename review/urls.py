from django.urls import path
from .views import take_review

urlpatterns = [
    path('review/', take_review, name='take-review'),
]

