from django.urls import path
from .views import create_checkout_session, payments_webhook

urlpatterns = [
    path("get-access/", create_checkout_session, name="get-access"),
    path("handle-payments/", payments_webhook)
]
