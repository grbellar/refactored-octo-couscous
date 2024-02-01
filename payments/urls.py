from django.urls import path
from .views import create_checkout_session, payments_webhook

urlpatterns = [
    path("stripe-checkout/", create_checkout_session, name="stripe-checkout"),
    path("handle-payments/", payments_webhook)
]
